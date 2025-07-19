from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api_qna import graph
from service.rate_limit_config import RATE_LIMIT_STRATEGY, DEFAULT_LIMITS, REDIS_CONFIG, get_endpoint_limits
from service.rate_limit_strategies import (
    get_ip_address, get_global_key, get_user_id_key, 
    get_api_key, get_combined_key, get_endpoint_specific_key
)
from slowapi.util import get_ipaddr

import redis
import ast
import json
import os
from datetime import datetime

# Initialize Redis connection for rate limiting
try:
    redis_client = redis.Redis(**REDIS_CONFIG)
    redis_client.ping()  # Test connection
    print("Connected to Redis for rate limiting")
    storage_uri = f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}"
except redis.ConnectionError:
    print("Warning: Redis not available, using in-memory rate limiting")
    redis_client = None
    storage_uri = "memory://"

# Select rate limiting key function based on strategy
def get_rate_limit_key_func():
    strategy_map = {
        "ip": get_ipaddr,
        "global": get_global_key,
        "user_id": get_user_id_key,
        "api_key": get_api_key,
        "combined": get_combined_key,
        "endpoint_specific": get_endpoint_specific_key
    }
    return strategy_map.get(RATE_LIMIT_STRATEGY, get_ipaddr)

# Initialize rate limiter with configurable strategy
limiter = Limiter(
    key_func=get_rate_limit_key_func(),
    storage_uri=storage_uri,
    default_limits=DEFAULT_LIMITS, enabled=False
)

# Get endpoint limits based on current strategy
ENDPOINT_LIMITS = get_endpoint_limits()

print(f"Rate limiting strategy: {RATE_LIMIT_STRATEGY}")
print(f"Endpoint limits: {ENDPOINT_LIMITS}")

app = FastAPI()

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##app.mount("/tests", StaticFiles(directory="test-app"), name="tests")
app.mount("/portal", StaticFiles(directory="portal"), name="tests")
## app.mount("/images", StaticFiles(directory="images"), name="images")


class QnARequest(BaseModel):
    question: str

str_query = ""
str_columns = ""
str_result = ""
str_answer = ""
token_info = {"write_query": {}, "extract_columns": {}, "generate_answer": {}}

def log_qna_request(request_data, client_ip):
    """
    Log QnA request and response data to a text file with timestamp
    """
    try:
        # Determine log directory - use Azure file share if available, otherwise local
        # log_dir = "/mnt/azurefiles/logs" if os.path.exists("/mnt/azurefiles/logs") else "logs"
        # os.makedirs(log_dir, exist_ok=True)
        
        log_dir = "log"
        log_file = os.path.join(log_dir, "qna_requests.log")
        
        # Create log entry with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # print(f"Log Entry begin:")
        # log_entry = {
        #     "timestamp": timestamp,
        #     "client_ip": client_ip,
        #     "question": request_data.get("question", ""),
        #     "query": request_data.get("query", ""),
        #     "columns": request_data.get("columns", ""),
        #     "result_count": len(request_data.get("result", [])) if request_data.get("result") else 0,
        #     #"answer": request_data.get("answer", ""),
        #     "input_tokens": request_data.get("token_info", {}).get("input_tokens", "0"),
        #     "output_tokens": request_data.get("token_info", {}).get("output_tokens", "0")
        # }
        # print(f"Log Entry end: {log_entry}")

        # Write to log file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | IP: {client_ip} | Question: {request_data.get('question', '')[:500]}... | "
                   f"Query: {request_data.get('query', '')[:1000]}... | "
                   f"Columns: {request_data.get('columns', '')[:50]}... | "
                   f"Results: {len(request_data.get('result', []))} rows | "
                   #f"Answer: {request_data.get('answer', '')[:200]}... | "  ## Commented as it was having issue parsing.
                   f"Tokens: {request_data.get('token_info', {}).get('input_tokens', '0')}in/{request_data.get('token_info', {}).get('output_tokens', '0')}out\n")
        
        print(f"Logged QnA request to {log_file}")
        
    except Exception as e:
        print(f"Error logging QnA request: {e}")


@app.post("/api/v2/qna")
@limiter.limit(ENDPOINT_LIMITS["/api/v2/qna"])
async def qna_response(request: Request, qna_request: QnARequest):
    """
    Endpoint to get the QnA response.
    This will trigger the QnA process and return the result.
    """

    input_question = qna_request.question
    print("Question:", input_question)
    
    for step in graph.stream(
    {"question": input_question}, stream_mode="updates"):

        if "write_query" in step:
            ##print("Step:", step)
            str_query = step["write_query"]["query"]
            ##Print token_info
            token_info["write_query"] = step["write_query"].get("token_usage", {})
        if "extract_columns" in step:
            str_columns = step["extract_columns"]["columns"]
            token_info["extract_columns"] = step["extract_columns"].get("token_usage", {})
        if "execute_query" in step:
            str_result = step["execute_query"]["result"]
        if "generate_answer" in step:
            str_answer = step["generate_answer"]["answer"]
            token_info["generate_answer"] = step["generate_answer"].get("token_usage", {})
        #print("Step:", step)
    input_tokens, output_tokens = sum_token_usage(token_info)
    str_parsedResult = [] if not str_result else parse_result_string(str_result)
    str_parsedResult = format_numeric_values(str_parsedResult)

    # Prepare response data
    response_data = {
        "query": str_query,
        "columns": str_columns,
        "result": str_parsedResult,
        "answer": str_answer,
        "token_info": {"input_tokens": str(input_tokens), "output_tokens": str(output_tokens)}
    }
    
    # Log the request and response data
    try:
        client_ip = get_ipaddr(request)
        log_data = {
            "question": input_question,
            **response_data
        }
        log_qna_request(log_data, client_ip)
    except Exception as e:
        print(f"Error logging request: {e}")
    
    return response_data

def format_numeric_values(data):
    formatted = []
    for row in data:
        new_row = []
        for val in row:
            if isinstance(val, (int, float)):
                new_row.append(f"{val:.2f}")
            else:
                new_row.append(val)
        formatted.append(new_row)
    return formatted



def sum_token_usage(token_info):
    total_input = 0
    total_output = 0
    for step in token_info.values():
        if "input_tokens" in step:
            total_input += int(step["input_tokens"])
        if "output_tokens" in step:
            total_output += int(step["output_tokens"])
    return total_input, total_output



def parse_result_string(result_string: str) -> list[list]:
    try:
        list_of_tuples = ast.literal_eval(result_string)
        return [list(t) for t in list_of_tuples]
    except (ValueError, SyntaxError) as e:
        print(f"(fn:parse_result_string) Error parsing result string: {e}")
        return [] # Or raise an exception, depending on your error handling strategy


# @app.get("/api/v1/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

@app.get("/")
@limiter.limit(ENDPOINT_LIMITS["/"])
def read_root(request: Request):
    return RedirectResponse(url="/portal/index.html", status_code=307)

@app.get("/api/v1/health")
@limiter.limit(ENDPOINT_LIMITS["/api/v1/health"])
def health_check(request: Request):
    return {"status": "ok"}

# Visitor tracking (in production, use a database or Redis)
unique_visitors = set()
total_page_visits = 0

@app.get("/api/v1/visit-count")
@limiter.limit("100 per minute")  # More lenient for visit counter
def get_visit_count(request: Request):
    global unique_visitors, total_page_visits
    
    # Get the client's IP address
    client_ip = get_remote_address(request)
    
    # Add IP to the set (automatically handles uniqueness)
    unique_visitors.add(client_ip)
    
    # Increment total page visits
    total_page_visits += 1
    
    # Return both counts
    return {
        "unique_visitors": len(unique_visitors),
        "total_visits": total_page_visits
    }

# @app.get("/main")
# def gethtml():
#     return FileResponse("simple_db_QnA/index.html")

# @app.get("/app")
# def gethtml():
#     return FileResponse("simple_db_QnA/app.html")
