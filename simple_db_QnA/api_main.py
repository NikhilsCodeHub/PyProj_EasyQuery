from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI


app = FastAPI()


class QnARequest(BaseModel):
    question: str

@app.post("/api/v1/qna")
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
        if "execute_query" in step:
            str_result = step["execute_query"]["result"]
        if "generate_answer" in step:
            str_answer = step["generate_answer"]["answer"]
    return str_result


@app.get("/api/v1/qna")
def qna_response():
    """
    Endpoint to get the QnA response.
    This will trigger the QnA process and return the result.
    """
    # Assuming 'graph' is defined and initialized in api_qna.py
    from api_qna import graph

    for step in graph.stream(
#    {"question": "Whats the Total Invoice for each month for each Artist ?. Show the Artist in columns and Month in Rows. Limit result to 100 rows"}, stream_mode="updates"
    {"question": "What was the revenue of each album for each Artist ?"}, stream_mode="updates"):
        print("Step:", step)
        if "write_query" in step:
            str_query = step["write_query"]["query"]
        if "execute_query" in step:
            str_result = step["execute_query"]["result"]
        if "generate_answer" in step:
            str_answer = step["generate_answer"]["answer"]
    return str_result


@app.get("/api/v1/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
