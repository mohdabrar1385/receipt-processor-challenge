# receipt-processor-challenge

## Receipt Processor

This is a web service that processes receipts and calculates points based on specified rules. You can test the application either using **unit tests** or **Postman**.

## Requirements

- Docker
- Postman (if testing via Postman)

## Running the Application

1. **Build the Docker image**:

    ```
    docker build -t receipt-processor .
    ```

2. **Run the Docker container with unit tests**:

    To run unit tests in the Docker container, uncomment the `CMD` line in the Dockerfile for unit tests and comment out the one that runs the Flask application.

    Dockerfile change:
    
    ```dockerfile
    # Define the command to run unit tests using unittest
    CMD ["python", "-m", "unittest", "test_app.py"]
    
    # Comment out this line to run unit tests instead of the app
    # CMD ["python", "app.py"]
    ```

    Then, run the container:
    
    ```
    docker run receipt-processor
    ```

    This will execute your unit tests defined in `test_app.py`.

3. **Run the Docker container for the Flask application**:

    To run the Flask application, uncomment the line in the Dockerfile that starts the app, and comment out the one for unit tests.

    Dockerfile change:

    ```dockerfile
    # Comment out the unit test command to run the Flask app
    # CMD ["python", "-m", "unittest", "test_app.py"]

    # Define the command to run the application
    CMD ["python", "app.py"]
    ```

    Then, run the container:

    ```
    docker run -p 8080:8080 receipt-processor
    ```

4. **Access the Application**:

    The application will be running on `http://localhost:8080`.

---

## Testing the Application with Postman

### Process Receipts

- **Endpoint:** `/receipts/process`
- **Method:** `POST`
- **Payload:** Receipt JSON
- **Response:** JSON containing an `id` for the receipt

#### POST Request in Postman

1. Open Postman and set up a new request.
2. Set the request type to **POST**.
3. Enter the URL `http://localhost:8080/receipts/process`.
4. Go to the **Body** tab, select **raw**, and choose **JSON** (application/json) from the dropdown.
5. Paste the following JSON payload:

    ```json
    {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"}
        ],
        "total": "35.35"
    }
    ```

6. Click **Send** to submit the request. You will receive a JSON response with a receipt `id`.

### Retrieve Points for a Receipt

- **Endpoint:** `/receipts/{id}/points`
- **Method:** `GET`
- **Payload:** Receipt `id` (String)
- **Response:** JSON containing the points awarded for the receipt

#### GET Request in Postman

1. Set up a new request in Postman.
2. Set the request type to **GET**.
3. Enter the URL `http://localhost:8080/receipts/{id}/points`, replacing `{id}` with the receipt `id` obtained from the previous step.
4. Click **Send** to submit the request. You will receive a JSON response with the points for that receipt.

---

## Running Unit Tests

To run the unit tests:

1. Ensure the Dockerfile is set up to run the unit tests (as described in the **Running the Application** section).
2. Once the container is up and running, the unit tests will execute automatically.

You can modify the `test_app.py` file to add more unit tests or modify the existing ones as needed.

---

## GitHub Repository

Find the GitHub repository for this project [here](receipt-processor-challenge.txt).
