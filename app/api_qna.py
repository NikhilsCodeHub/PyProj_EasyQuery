from app.db_connection import db
from app.llm_config import llm

from typing_extensions import TypedDict
import ast
import json

class State(TypedDict):
    question: str
    query: str
    columns: list[str]
    result: str
    answer: str
    token_usage: dict[str, str]

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
For real numbers or numeric, use round function to 2 decimal places.

DO NOT make any statements that contain (INSERT, UPDATE, DELETE, DROP etc.) to the database.
Output only 1 query even for multiple questions. 
Include the column names in the output.
Do not add any explanation. Do not add any comments.

Only use the following tables:
{table_info}

Fewshot learning examples:
{fewshot_examples}

"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate(
    [("system", system_message), ("user", user_prompt)]
)

#for message in query_prompt_template.messages:
#    message.pretty_print()

## ------ Step 2: Generate Query

from typing_extensions import Annotated


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information and return token usage info."""
    usage = {}
    #table_schema = db.get_table_info(['vw_providers_t', 'vw_drug_t', 'vw_drug_name_t', 'vw_claim_t', 'vw_drug_category_t','vw_place_of_service_t','vw_channel_t','vw_drug_source_type_t','vw_claim_type_t','vw_brand_generic_t'])
    #"table_info": db.get_table_info(['claim_view', 'drug_view', 'drug_name_view', 'provider_view', 'drug_category_view']),
    #table_schema = db.get_table_info(['vw_all_drug_claims_data'])  # Get table schema for the views used in the query
    table_schema = read_from_file('Table_Schema')  # Get table schema for the views used in the query
    db._view_support = True  # Enable view support for the database
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 100,
            "table_info": table_schema,
            "fewshot_examples": read_from_file('fewshot_examples'),
            ##"fewshot_examples": "",
            "input": state["question"],
        }
    )
    print("Table Schema:", table_schema)
    structured_llm = llm.with_structured_output(QueryOutput, include_raw=True)
    result = structured_llm.invoke(prompt)
    # Try to extract token usage if available
    # token_usage = getattr(result["raw"], 'response_metadata', None)
    print("Query Returned :", json.loads(result["raw"].content)["query"])
    # convert the token to a string
    usage = {"input_tokens" : str(result["raw"].usage_metadata['input_tokens']), "output_tokens" : str(result["raw"].usage_metadata['output_tokens'])}
    print("Query Token Usage: ", usage)
    return {"query": json.loads(result["raw"].content)["query"], "token_usage": usage}

def read_from_file(strtype = "fewshot_examples"):
    if strtype == "fewshot_examples":
        """Get fewshot examples for the prompt."""
        ## Read file fewshot_examples.txt
        with open("app/few_shot_examples.txt", "r") as file:
            read_from_file = file.read().strip()
    elif strtype == "Table_Schema":
        """Get fewshot examples for the prompt."""
        ## Read file fewshot_examples2.txt
        with open("data/table_schema.txt", "r") as file:
            read_from_file = file.read().strip() 
    return read_from_file

## ------ Step 3 : Extract columns from query
from typing_extensions import Annotated

class ColumnOutput(TypedDict):
    columns: Annotated[list[str], "List of column names in the SELECT statement, in order."]

def extract_columns(state: State):
    """Use LLM to extract column names from the SQL query and return token usage info."""
    usage = {}
    prompt = (
        "Given the following SQL query, list the column names that will appear in the result set, in order, as a Python list of strings. Also reformat as 'Abcd Efgh' to show as table column headers\n\n"
        f"SQL Query:\n{state['query']}\n\n"
        "Columns:"
    )
    structured_llm = llm.with_structured_output(ColumnOutput, include_raw=True)
    result = structured_llm.invoke(prompt)
    usage = {"input_tokens" : str(result["raw"].usage_metadata['input_tokens']), "output_tokens" : str(result["raw"].usage_metadata['output_tokens'])}
    print("Columns:", json.loads(result["raw"].content)["columns"])
    print("Column Token Usage: ", usage)
    #print("Result:", result)
    return {"columns": json.loads(result["raw"].content)["columns"], "token_usage": usage}


## ------ Step 4: Execute Query

from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool


def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    var_result = execute_query_tool.invoke(state["query"])
    print("Result:", var_result)
    return {"result": [] if not var_result else var_result}

## ------ Step 5: Generate Answer based on Query and Result

def generate_answer(state: State):
    """Answer question using retrieved information as context and return token usage info."""
    usage = {}
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )

    if len(state["result"])>2 and (len(ast.literal_eval(state["result"])[0]) > 3 or len(ast.literal_eval(state["result"])) > 3):
        response = "Result has too many value to send to LLM. Use datatable to show data. tuples {},length {}".format(
            len(state["result"][0]), len(state["result"])
        )
        usage = {}
    elif len(state["result"]) < 2:
        response = "No results found for the query."
        usage = {}
    else:
        # Use the LLM to generate an answer based on the prompt
        llm_response = llm.invoke(prompt)
        response = llm_response
        #token_usage = getattr(llm_response, 'response_metadata', None)
        usage = {"input_tokens" : str(response.usage_metadata['input_tokens']), "output_tokens" : str(response.usage_metadata['output_tokens'])}
        print("LLM Response:", llm_response)
    return {"answer": response, "token_usage": usage}

## ------

from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence(
    [write_query, extract_columns, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

## ------


