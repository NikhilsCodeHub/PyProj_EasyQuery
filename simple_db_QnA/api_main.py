from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import FileResponse
import ast


app = FastAPI()


class QnARequest(BaseModel):
    question: str

str_query = ""
str_columns = ""
str_result = ""
str_answer = ""


@app.post("/api/v2/qna")
async def qna_response(qna_request: QnARequest):
    """
    Endpoint to get the QnA response.
    This will trigger the QnA process and return the result.
    """
    from api_qna import graph

    input_question = qna_request.question

    for step in graph.stream(
#    {"question": "Whats the Total Invoice for each month for each Artist ?. Show the Artist in columns and Month in Rows. Limit result to 100 rows"}, stream_mode="updates"
    {"question": input_question}, stream_mode="updates"):
        print("Step:", step)
        if "write_query" in step:
            str_query = step["write_query"]["query"]
        if "extract_columns" in step:
            str_columns = step["extract_columns"]["columns"]
        if "execute_query" in step:
            str_result = step["execute_query"]["result"]
        if "generate_answer" in step:
            str_answer = step["generate_answer"]["answer"]
    return {"query": str_query, "columns" : str_columns, "result": parse_result_string(str_result), "answer": str_answer}


@app.post("/api/v1/qna")
async def qna_response2(qna_request: QnARequest):
    """
    Endpoint to get the QnA response.
    This will trigger the QnA process and return the result.
    """
    from api_qna import graph

    input_question = qna_request.question

    for step in graph.stream(
#    {"question": "Whats the Total Invoice for each month for each Artist ?. Show the Artist in columns and Month in Rows. Limit result to 100 rows"}, stream_mode="updates"
    {"question": input_question}, stream_mode="updates"):
        print("Step:", step)
        if "write_query" in step:
            str_query = step["write_query"]["query"]
        if "execute_query" in step:
            str_result = step["execute_query"]["result"]
        if "generate_answer" in step:
            str_answer = step["generate_answer"]["answer"]
    return {"query": str_query, "result": str_result, "answer": str_answer}

def parse_result_string(result_string: str) -> list[list]:
    try:
        list_of_tuples = ast.literal_eval(result_string)
        return [list(t) for t in list_of_tuples]
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing result string: {e}")
        return [] # Or raise an exception, depending on your error handling strategy


@app.get("/api/v1/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

@app.get("/app")
def gethtml():
    return FileResponse("../app.html")

