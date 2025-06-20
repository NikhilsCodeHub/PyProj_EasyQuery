
from simple_db_QnA.db_connection import db
from simple_db_QnA.llm_config import llm
# from db_connection import db
# from llm_config import llm
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
For decimal numbers, limit the precision to 2 decimal places.

DO NOT make any statements that contain (INSERT, UPDATE, DELETE, DROP etc.) to the database.
Output only 1 query even for multiple questions. 
Include the column names in the output.
Do not add any explanation. Do not add any comments.

Only use the following tables:
{table_info}

You can refer to the following sample questions to understand the type of questions and queries you can generate:
Question 1: Total Net Money by Drug Category of Nausea and Year
--sql 1
SELECT
    STRFTIME('%Y', fill_dt) AS fill_year,
    drug_category_name,
    SUM(net_mony) AS total_net_money
FROM
    pharmacy_claims_drug_provider_view
WHERE
    drug_category_name like '%Nausea%'
GROUP BY
    fill_year,
    drug_category_name
ORDER BY
    fill_year,
    total_net_money DESC;
---

Question 2: Top 5 Prescribers by Quantity Dispensed for a Specific Drug Type

--sql 2
SELECT
    prescriber_id,
    SUM(quantity) AS total_quantity_dispensed,
    COUNT(DISTINCT claim_id) AS total_claims
FROM
    pharmacy_claims_drug_provider_view
WHERE
    drug_name like  '%SYNTHROID%' -- Replace with any specific drug name
GROUP BY
    prescriber_id
ORDER BY
    total_quantity_dispensed DESC
LIMIT 5;
---

Question 3: Average Copay and Admin Fee per Claim for Pharmacy vs. Medical Benefits
--sql 3
SELECT
    benefit_type_Pharmacy_or_Medical,
    AVG(copay_mony) AS average_copay,
    AVG(admin_mony) AS average_admin_fee,
    COUNT(claim_id) AS number_of_claims
FROM
    pharmacy_claims_drug_provider_view
GROUP BY
    benefit_type_Pharmacy_or_Medical;
---

Question 4: Count of Unique Members and Claims by Provider State in New York, Texas and Kentucky
--sql 4
SELECT
    provider_location_state,
    provider_location_city,
    COUNT(DISTINCT member_id) AS unique_members,
    COUNT(DISTINCT claim_id) AS unique_claims
FROM
    pharmacy_claims_drug_provider_view
WHERE
    provider_location_state in ('TX','NY', 'KY') AND provider_location_city IS NOT NULL
GROUP BY
    provider_location_state,
    provider_location_city
ORDER BY
    provider_location_state,
    provider_location_city;
---

Question 5: Provide Brand vs. Generic Drug Dispensing by Specialty Indicator (with Percentage)
--sql 5
SELECT
    specialty_indicator,
    brand_or_generic,
    COUNT(claim_id) AS total_claims,
    SUM(quantity) AS total_quantity,
    CAST(COUNT(claim_id) * 100.0 / SUM(COUNT(claim_id)) OVER (PARTITION BY specialty_indicator) AS REAL) AS percentage_of_claims_in_group
FROM
    pharmacy_claims_drug_provider_view
GROUP BY
    specialty_indicator,
    brand_or_generic
ORDER BY
    specialty_indicator,
    brand_or_generic;

Question 6: What is the total number of claims group by days supply partition by provider location in TX, NY, PA and CA. Provider location as column headers
--sql 6
SELECT    days_supply,    COUNT(claim_id) AS total_claims,    SUM(CASE WHEN provider_location_state = 'TX' THEN 1 ELSE 0 END) AS TX,
    SUM(CASE WHEN provider_location_state = 'NY' THEN 1 ELSE 0 END) AS NY,    SUM(CASE WHEN provider_location_state = 'PA' THEN 1 ELSE 0 END) AS PA,
        SUM(CASE WHEN provider_location_state = 'CA' THEN 1 ELSE 0 END) AS CA
        FROM    pharmacy_claims_drug_provider_view 
        WHERE     provider_location_state IN ('TX', 'NY', 'PA', 'CA') 
        GROUP BY    days_supply
        ORDER BY    days_supply;


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
    """Generate SQL query to fetch information."""
    db._view_support = True  # Enable view support for the database
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 100,
            #"table_info": db.get_table_info(['claim']),
            #"table_info": db.get_table_info(['claim_view', 'drug_view', 'drug_name_view', 'provider_view', 'drug_category_view']),
            "table_info": db.get_table_info(['pharmacy_claims_drug_provider_view']),
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
    var_result = execute_query_tool.invoke(state["query"])
    print("Result:", var_result)
    return {"result": [] if not var_result else var_result}

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

    if len(state["result"])>2 and (len(ast.literal_eval(state["result"])[0]) > 3 or len(ast.literal_eval(state["result"])) > 3):
        response = "Result has too many value to send to LLM. Use datatable to show data. tuples {},length {}".format(
            len(state["result"][0]), len(state["result"])
        )
    elif len(state["result"]) < 2:
        response = "No results found for the query."
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

