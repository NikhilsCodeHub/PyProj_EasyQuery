# EasyQuery

This project implements a simple REST API that allows users to submit text questions and receive responses on their dataset in both JSON format.

# Demo Link
https://easyquery-app.happydune-f5c9b622.eastus2.azurecontainerapps.io/portal/demo.html

## Project Structure

```
EasyQuery
├── app                   # Main application files
├── requirements.txt      # Project dependencies
├── portal                # Directory for HTML for the portal.
    └── JS, CSS           # CSS, JS files used for dem
├── service               # Directory for API services that run the whole process using Langchain Framework.
├── data                  # Directory for SQLite DB.
├── README.md             # Project documentation
└── log                   # Directory for log file
└── Dockerfile            # Docker file for building the container image

```

## Requirements

To run this project, you need to have Python installed. You can install the required dependencies using the following command:

```
pip install -r requirements.txt
```

## Running the Application

To start the  application, run the following command:

```
uvicorn service.api_main:app --host 0.0.0.0 --port 8123
```

The application will be accessible at `https://localhost:8123`.

## API Endpoint

- **POST /api/v2/qna**: Accepts a JSON payload with a question and returns a JSON response with the answer and an HTML response.

### Example Request

```json
{
  "question": "How many claims were filed in Jan through Jun of 2021 related to category 'Eye Disorders'. Show months as headers"
}
```

### Example Response

**JSON Response:**

```json
{
  "columns": [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June"
],
"results": [
    "25.00",
    "27.00",
    "27.00",
    "29.00",
    "34.00",
    "23.00"
]
}

```

**Additional Features:**

- There are ratelimiting features added to the API call to prevent misuse and api hacking.
- The Logs can be written to Azure File share for post analysis
                            
