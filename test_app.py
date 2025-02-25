import unittest
from app import app  # Import the app from your file
import json

class ReceiptAppTestCase(unittest.TestCase):

    # Set up the Flask test client for each test
    def setUp(self):
        """
        Set up the Flask test client before each test is run.
        This allows us to simulate requests to the application without needing a live server.
        """
        self.app = app.test_client()  # Create a test client for making HTTP requests
        self.app.testing = True  # Enable testing mode for the Flask app
        self.client = app.test_client()  # Initialize the client again for clarity

    def test_valid_receipt(self):
        """
        Test case for processing a valid receipt.
        This test ensures that a valid receipt returns a 200 status and contains an 'id' in the response.
        """
        receipt_data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-02-24",
            "purchaseTime": "14:30",
            "items": [
                {"shortDescription": "item1", "price": "5.50"},
                {"shortDescription": "item2", "price": "3.00"}
            ],
            "total": "8.50"
        }
        response = self.app.post('/receipts/process', json=receipt_data)
        self.assertEqual(response.status_code, 200)  # Check that the status code is 200 (OK)
        response_json = json.loads(response.data)  # Parse the JSON response
        self.assertIn('id', response_json)  # Ensure the response contains an 'id'

    def test_invalid_receipt_missing_field(self):
        """
        Test case for a receipt with a missing required field.
        This test ensures that when a field is missing, the response returns a 'Validation Error'.
        """
        receipt_data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-02-24",
            "purchaseTime": "14:30",
            "items": []  # Missing required items
        }

        response = self.client.post('/receipts/process', json=receipt_data)
        response_json = response.get_json()  # Parse the response as JSON

        # Check if the error message matches the expected 'Validation Error'
        self.assertEqual(response_json['error'], 'Validation Error')

    def test_invalid_receipt_invalid_price(self):
        """
        Test case for a receipt with an invalid price (negative value).
        This ensures that when an item has an invalid price, the response returns a 'Validation Error'.
        """
        receipt_data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-02-24",
            "purchaseTime": "14:30",
            "items": [
                {"shortDescription": "item1", "price": "5.50"},
                {"shortDescription": "item2", "price": "-3.00"}  # Invalid price (negative)
            ],
            "total": "2.50"
        }
        response = self.app.post('/receipts/process', json=receipt_data)
        self.assertEqual(response.status_code, 400)  # Expect a '400 Bad Request' for invalid data
        response_json = json.loads(response.data)
        self.assertEqual(response_json['error'], 'Validation Error')  # Check the specific error message

    def test_invalid_receipt_total_mismatch(self):
        """
        Test case for a receipt where the total doesn't match the sum of the item prices.
        This ensures that the system catches mismatched totals and returns a validation error.
        """
        receipt_data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-02-24",
            "purchaseTime": "14:30",
            "items": [
                {"shortDescription": "item1", "price": "5.00"},
                {"shortDescription": "item2", "price": "3.50"}
            ],
            "total": "9.00"  # Incorrect total
        }

        response = self.client.post('/receipts/process', json=receipt_data)
        response_json = response.get_json()

        # Expect a validation error due to the total mismatch
        self.assertEqual(response_json['error'], 'Validation Error')

    def test_receipt_points(self):
        """
        Test case for calculating points based on a processed receipt.
        This test ensures that once a receipt is processed, the points endpoint returns points.
        """
        receipt_data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-02-24",
            "purchaseTime": "14:30",
            "items": [
                {"shortDescription": "item1", "price": "5.50"},
                {"shortDescription": "item2", "price": "3.00"}
            ],
            "total": "8.50"
        }
        response = self.app.post('/receipts/process', json=receipt_data)  # Post receipt data
        receipt_id = json.loads(response.data)['id']  # Extract the receipt ID from the response
        response = self.app.get(f'/receipts/{receipt_id}/points')  # Get points for the receipt
        self.assertEqual(response.status_code, 200)  # Ensure that the response status is 200
        response_json = json.loads(response.data)  # Parse the response
        self.assertIn('points', response_json)  # Ensure that points are returned in the response

    def test_receipt_not_found(self):
        """
        Test case for handling the scenario where a receipt ID is not found.
        This ensures that when an invalid receipt ID is requested, the system returns a 'Not Found' error.
        """
        response = self.app.get('/receipts/nonexistent_id/points')  # Attempt to get points for a nonexistent receipt
        self.assertEqual(response.status_code, 404)  # Expect a '404 Not Found' status
        response_json = json.loads(response.data)
        self.assertEqual(response_json['error'], 'Not Found')  # Ensure the error message is correct

if __name__ == '__main__':
    unittest.main()
