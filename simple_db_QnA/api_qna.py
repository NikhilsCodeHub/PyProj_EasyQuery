
from db_connection import db
from llm_config import llm
from typing_extensions import TypedDict
import ast

class State(TypedDict):
    question: str
    query: str
    columns: list[str]
    result: str
    answer: str


## ------ Step 1: System Prompt to Write Query

from langchain_core.prompts import ChatPromptTemplate

system_message = """
Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema
description. Be careful to not query for columns that do not exist. Also,
pay attention to which column is in which table.

DO NOT make any statements that contain (INSERT, UPDATE, DELETE, DROP etc.) to the database.
Output only 1 query even for multiple questions. 
Include the column names in the output.
Do not add any explanation. Do not add any comments.

Only use the following tables:
{table_info}
"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate(
    [("system", system_message), ("user", user_prompt)]
)

for message in query_prompt_template.messages:
    message.pretty_print()

## ------ Step 2: Generate Query

from typing_extensions import Annotated


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 100,
            "table_info": db.get_table_info(['RX_CLAIM', 'drug']),
            "input": state["question"],
        }
    )
    print("Prompt:", prompt)    
    # print("Prompt:", prompt.messages[1].content)

    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

## ------ Step 3 : Extract columns from query
from typing_extensions import Annotated

class ColumnOutput(TypedDict):
    columns: Annotated[list[str], "List of column names in the SELECT statement, in order."]

def extract_columns(state: State):
    """Use LLM to extract column names from the SQL query."""
    prompt = (
        "Given the following SQL query, list the column names that will appear in the result set, in order, as a Python list of strings.\n\n"
        f"SQL Query:\n{state['query']}\n\n"
        "Columns:"
    )
    structured_llm = llm.with_structured_output(ColumnOutput)
    result = structured_llm.invoke(prompt)
    return {"columns": result["columns"]}


## ------ Step 4: Execute Query

from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool


def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

## ------ Step 5: Generate Answer based on Query and Result

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )

    if len(ast.literal_eval(state["result"])[0]) > 3 or len(ast.literal_eval(state["result"])) > 5:
        response = "Result has too many value to send to LLM. Use datatable to show data. tuples {},length {}".format(
            len(state["result"][0]), len(state["result"])
        )
    else:
        # Use the LLM to generate an answer based on the prompt
        response = llm.invoke(prompt)
    #response = "Deliberately empty response"
    return {"answer": response}

## ------

from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence(
    [write_query, extract_columns, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

## ------




""" 
for step in graph.stream(
    {"question": "Which members have the highest total cost?"}, stream_mode="updates"
#    {"question": "Can we see a breakdown of Aerosmith's revenue by album or track for each of those years to identify their top-performing content? ?"}, stream_mode="updates"
):
    print("Step:", step)
    if "write_query" in step:
        str_query = step["write_query"]["query"]
    if "execute_query" in step:
        str_result = step["execute_query"]["result"]
    if "generate_answer" in step:
        str_answer = step["generate_answer"]["answer"]
    # if "Followup_Questions" in step:
    #     followup_questions = step["FollowupQuestions"]["Followup_Questions"]
    print("Query :", str_query)
    print("Result :", str_result)
    print("Answer :", str_answer)
    # print("Followup Questions :", followup_questions)
 """

