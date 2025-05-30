# Simple DB QnA API

This project implements a simple REST API using Flask that allows users to submit text questions and receive responses in both JSON and HTML formats.

## Project Structure

```
simple_db_QnA
├── app.py                # Main application file
├── requirements.txt      # Project dependencies
├── templates             # Directory for HTML templates
│   └── response.html     # HTML template for displaying responses
├── static                # Directory for static files (CSS, JS, images)
├── README.md             # Project documentation
└── tests                 # Directory for unit tests
    └── test_app.py       # Unit tests for the application
```

## Requirements

To run this project, you need to have Python installed. You can install the required dependencies using the following command:

```
pip install -r requirements.txt
```

## Running the Application

To start the Flask application, run the following command:

```
python app.py
```

The application will be accessible at `https://localhost:5000`.

## API Endpoint

- **POST /ask**: Accepts a JSON payload with a question and returns a JSON response with the answer and an HTML response.

### Example Request

```json
{
  "question": "What is the capital of France?"
}
```

### Example Response

**JSON Response:**

```json
{
  "answer": "The capital of France is Paris."
}
```

**HTML Response:**

The HTML response will be rendered using the `response.html` template, displaying the answer in a user-friendly format.

## Testing

To run the unit tests, navigate to the `tests` directory and execute:

```
python -m unittest test_app.py
```

This will ensure that the API behaves as expected.