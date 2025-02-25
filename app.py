from flask import Flask, request, jsonify
import uuid
import re
import math
from datetime import datetime
import logging

app = Flask(__name__)
receipts = {}

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Custom error handler
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {error}")
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

def validate_receipt(receipt):
    # Validate required fields
    required_fields = ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
    for field in required_fields:
        if field not in receipt:
            raise ValueError(f"Missing required field: {field}")

    # Validate retailer
    if not isinstance(receipt["retailer"], str) or not receipt["retailer"].strip():
        raise ValueError("Invalid retailer name")

    # Validate total
    try:
        total = float(receipt["total"])
        if total < 0:
            raise ValueError("Total amount cannot be negative")
    except ValueError:
        raise ValueError("Invalid total format")

    # Validate purchaseDate
    try:
        datetime.strptime(receipt["purchaseDate"], "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid purchaseDate format, expected YYYY-MM-DD")

    # Validate purchaseTime
    try:
        datetime.strptime(receipt["purchaseTime"], "%H:%M")
    except ValueError:
        raise ValueError("Invalid purchaseTime format, expected HH:MM")

    # Validate items
    if not isinstance(receipt["items"], list) or not all(isinstance(item, dict) for item in receipt["items"]):
        raise ValueError("Items should be a list of objects")

    for item in receipt["items"]:
        if "shortDescription" not in item or "price" not in item:
            raise ValueError("Each item must have 'shortDescription' and 'price'")
        if not isinstance(item["shortDescription"], str) or not item["shortDescription"].strip():
            raise ValueError("Invalid shortDescription in items")
        try:
            price = float(item["price"])
            if price < 0:
                raise ValueError("Item price cannot be negative")
        except ValueError:
            raise ValueError("Invalid price format in items")

def process_receipt_data(receipt):
    # Calculate the total based on items
    calculated_total = sum(float(item["price"]) for item in receipt["items"])

    # Check if the provided total matches the calculated total
    total = float(receipt["total"])
    if not math.isclose(total, calculated_total, abs_tol=0.01):  # using abs_tol for floating point comparison
        raise ValueError(f"Total mismatch: calculated total is {calculated_total}, but provided total is {total}")

    return receipt

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    try:
        receipt = request.json
        if not receipt or not isinstance(receipt, dict):
            raise ValueError("Invalid JSON format")

        # Validate the receipt
        validate_receipt(receipt)

        # Process the receipt (e.g., calculate total and store it)
        processed_receipt = process_receipt_data(receipt)

        # Generate receipt ID and store it
        receipt_id = str(uuid.uuid4())
        points = calculate_points(processed_receipt)
        receipts[receipt_id] = processed_receipt

        return jsonify({"id": receipt_id}), 200

    except ValueError as ve:
        return jsonify({"error": "Validation Error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

@app.route('/receipts/<id>/points', methods=['GET'])
def get_points(id):
    try:
        if id not in receipts:
            raise ValueError("Receipt not found")
        
        receipt = receipts[id]
        points = calculate_points(receipt)
        return jsonify({"points": points}), 200

    except ValueError as ve:
        return jsonify({"error": "Not Found", "message": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500


def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += len(re.findall(r'[a-zA-Z0-9]', receipt['retailer']))

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = float(receipt['total'])
    if total.is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(receipt['items']) // 2) * 5

    # Rule 5: Multiply the price by 0.2 and round up to the nearest integer if item description length is multiple of 3
    for item in receipt['items']:
        trimmed_length = len(item['shortDescription'].strip())
        if trimmed_length % 3 == 0:
            price = float(item['price'])
            points += math.ceil(price * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt['purchaseDate'], '%Y-%m-%d')
    if purchase_date.day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt['purchaseTime'], '%H:%M')
    if 14 <= purchase_time.hour < 16:
        points += 10

    return points


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
