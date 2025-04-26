from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langgraph.graph import START, StateGraph
import os
import sqlite3




def run_sql_llm(question:str)-> dict:
    """
    This function initializes a SQL LLM pipeline to analyze logs from a security and network observability platform.
    It uses SQLite as the database backend and LangChain's SQLDatabase for querying.
    has question,query,result,columns,answer as the state variables.
    """
    # Set environment variables
    # os.environ["LANGSMITH_API_KEY"] = os.environ.get("LANGSMITH_API_KEY", "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")
    # os.environ["LANGSMITH_TRACING"] = "false"
    # os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY", "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")
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "false")
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    # Initialize DB (SQLite version of our synthetic log system)
    db = SQLDatabase.from_uri("sqlite:///logs2.db")

    # Define state for the pipeline
    class State(TypedDict): 
        question : str
        query : str
        result : str
        columns : list
        answer : str

    # Initialize LLM (Gemma via Groq)
    llm = init_chat_model("gemma2-9b-it", model_provider="groq")

    # CUSTOM PROMPT FOR LOG ANALYSIS (RAG-style contextual guidance)
    CUSTOM_PROMPT = """

    You are a SQL assistant helping analyze internal logs from a security and network observability platform.
    
    The logs are stored in three tables: `vpc_logs`, `access_logs`, and `execution_logs`.

    Each table has the following schemas:

    - vpc_logs(timestamp, src_ip, dst_ip, action, bytes_sent, request_id)
    - access_logs(timestamp, user_id, endpoint,method,status_code, request_id)
    - execution_logs(timestamp, function_name, duration_ms, success, request_id)

    example data for vpc_logs:
    | timestamp           | src_ip      | dst_ip   | action | bytes_sent | request_id   |
    | ------------------- | ----------- | -------- | ------ | ---------- | ------------ |
    | 2025-04-13T12:00:00 | 192.168.1.1 | 10.0.0.5 | ACCEPT | 2111       | req-118ab9fe |
    | 2025-04-13T12:01:00 | 192.168.1.2 | 10.0.0.6 | REJECT | 2635       | req-fc133d2e |
    | 2025-04-13T12:02:00 | 192.168.1.3 | 10.0.0.7 | ACCEPT | 3328       | req-7af7bf97 |
    | 2025-04-13T12:03:00 | 192.168.1.4 | 10.0.0.8 | REJECT | 1347       | req-612e052f |
    | 2025-04-13T12:04:00 | 192.168.1.5 | 10.0.0.9 | REJECT | 3793       | req-a8ea25b5 |

    example data for access_logs:
    | timestamp           | user_id | endpoint   | method | status_code | request_id   |
    | ------------------- | ------- | ---------- | ------ | ----------- | ------------ |
    | 2025-04-13T12:00:00 | user_1  | /api/login | GET    | 200         | req-118ab9fe |
    | 2025-04-13T12:01:00 | user_2  | /api/data  | GET    | 403         | req-fc133d2e |
    | 2025-04-13T12:02:00 | user_3  | /api/login | POST   | 201         | req-7af7bf97 |
    | 2025-04-13T12:03:00 | user_4  | /api/login | GET    | 200         | req-612e052f |
    | 2025-04-13T12:04:00 | user_5  | /api/login | GET    | 201         | req-a8ea25b5 |

    example data for execution_logs:
    | timestamp           | function_name | duration_ms | status  | request_id   |
    | ------------------- | ------------- | ----------- | ------- | ------------ |
    | 2025-04-13T12:00:00 | auth_user     | 924         | SUCCESS | req-118ab9fe |
    | 2025-04-13T12:01:00 | auth_user     | 476         | SUCCESS | req-fc133d2e |
    | 2025-04-13T12:02:00 | get_data      | 218         | SUCCESS | req-7af7bf97 |
    | 2025-04-13T12:03:00 | auth_user     | 914         | FAILED  | req-612e052f |
    | 2025-04-13T12:04:00 | get_data      | 792         | SUCCESS | req-a8ea25b5 |

    Use the request_id to join tables when the question requires correlating events.

    Some example questions:
    Example Question → SQL:

    - Which functions failed?  
    → SELECT function_name FROM execution_logs WHERE status = 'FAILED';

    - can you give me how many users were accepted in the month of april? 
    → SELECT COUNT(DISTINCT access_logs.user_id) AS accepted_users FROM access_logs JOIN vpc_logs USING (request_id) WHERE vpc_logs.action = 'ACCEPT' AND access_logs.timestamp >= '2025-04-01T00:00:00' AND access_logs.timestamp <= '2025-04-30T23:59:59';

    - Which users triggered rejected VPC actions?  
    → SELECT user_id FROM access_logs JOIN vpc_logs USING (request_id) WHERE action = 'REJECT';

    - Which services had the highest average execution time for failed requests?  
    → SELECT function_name, AVG(duration_ms) AS avg_duration FROM execution_logs WHERE status = 'FAILED' GROUP BY function_name ORDER BY avg_duration DESC;

    - Which user IDs accessed the `/api/data` endpoint but the VPC action was REJECT?  
    → SELECT access_logs.user_id FROM access_logs JOIN vpc_logs USING (request_id) WHERE access_logs.endpoint = '/api/data' AND vpc_logs.action = 'REJECT';

    - For failed `auth_user` function calls, what were the corresponding IPs and status codes?  
    → SELECT vpc_logs.src_ip, vpc_logs.dst_ip, access_logs.status_code FROM execution_logs JOIN vpc_logs USING (request_id) JOIN access_logs USING (request_id) WHERE execution_logs.function_name = 'auth_user' AND execution_logs.status = 'FAILED';

    - What is the total number of bytes sent for successful requests to the `/api/login` endpoint?  
    → SELECT SUM(vpc_logs.bytes_sent) AS total_bytes FROM access_logs JOIN execution_logs USING (request_id) JOIN vpc_logs USING (request_id) WHERE access_logs.endpoint = '/api/login' AND execution_logs.status = 'SUCCESS';

    - Which user had the longest execution duration and what function was called?  
    → SELECT access_logs.user_id, execution_logs.function_name, execution_logs.duration_ms FROM execution_logs JOIN access_logs USING (request_id) ORDER BY execution_logs.duration_ms DESC LIMIT 1;

    - List all requests where the VPC action was REJECT and the function call failed, along with timestamp and endpoint.  
    → SELECT access_logs.timestamp, access_logs.endpoint, vpc_logs.src_ip, execution_logs.function_name FROM access_logs JOIN vpc_logs USING (request_id) JOIN execution_logs USING (request_id) WHERE vpc_logs.action = 'REJECT' AND execution_logs.status = 'FAILED';

    - Count of failed requests by endpoint where latency was greater than 500ms.  
    → SELECT access_logs.endpoint, COUNT(*) AS failed_count FROM execution_logs JOIN access_logs USING (request_id) WHERE execution_logs.status = 'FAILED' AND execution_logs.duration_ms > 500 GROUP BY access_logs.endpoint;

    if the question is not related to the logs, say "I can't help with that".

    Now, using the following user question and schema, generate a syntactically valid SQL query that works for SQLite. Do NOT explain the query — just return the SQL.

    Schema:
    {table_info}

    Question:
    {input}
    """

    # Structured output format
    class QueryOutput(TypedDict):
        query: Annotated[str, ..., "Syntactically valid SQL query."]  # type: ignore
  

    # Step 1: SQL generation
    def write_query(state: State):
        prompt = CUSTOM_PROMPT.format(
            table_info=db.get_table_info(),
            input=state["question"]
        )
        structured_llm = llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"]}

    # Step 2: SQL execution
    def execute_query(state: State):
        # execute_query_tool = QuerySQLDatabaseTool(db=db)
        # return {"result": execute_query_tool.invoke(state["query"])}
            conn = sqlite3.connect("logs2.db")
            cursor = conn.cursor()
            cursor.execute(state["query"])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # 👈 column names
            return {"result": rows, "columns": columns}

    # Step 3: Answer generation from SQL result
    def generate_answer(state: State):
        prompt = (
            "You are a log analysis assistant.\n\n"
            "Given the following user question, SQL query, and result, explain the outcome, only the outcome not any others.You should striclty just explain the summary of the result only:\n\n"
            "The answer should be like an reply from a human."
            "Do not answer to any sensitive or private information.\n\n"
            "The answer should be like an reply from a human.\n\n" 
            f"User Question: {state['question']}\n"
            f"SQL Query: {state['query']}\n"
            f"SQL Result: {state['result']}\n\n"
            "Answer:"
        )
        print(len(prompt))
        if len(prompt) < 800:
            response = llm.invoke(prompt)
            return {"answer": response.content}
        else:
             return {"answer":"The data is shown below"}

    # Build LangGraph workflow
    graph_builder = StateGraph(State).add_sequence(
        [write_query, execute_query, generate_answer]
    )
    graph_builder.add_edge(START, "write_query")
    graph = graph_builder.compile()

    # 🧪 Example question to test it
    # for step in graph.stream(
    #     {"question": "Which services had the highest average latency during failed requests?"}, stream_mode="updates"
    # ):
    #     print(step)


    final_state = graph.invoke({"question": question})
    return final_state


def general_answers(question:str,mode="normal")->str:
     # Set environment variables
    os.environ["LANGSMITH_API_KEY"] = os.environ.get("LANGSMITH_API_KEY", "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")
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY", "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")
    llm = init_chat_model("gemma2-9b-it", model_provider="groq")
    prompt = ""
    if mode=="error":
        prompt = f"""
        You are a error to understandable sentence assistant.
        You are given a error message and you need to convert it into a understandable sentence.
        You should only answer the question, and not provide any other information.
        Do not answer to any sensitive or private information.
        Give a short of the error message mostly consisting of 2 lines.
        The answer should be like an reply from a human.
        The error: {question}
        """
    else:    
        prompt = f"""
        You are a logboot,a trustable log analysis assistant.
        Given the following user question, answer it as best as you can.
        You should only answer the question, and not provide any other information.
        Do not answer to any sensitive or private information.If the question is not related to the logs, say something on the lines of not being able to be helo with that and prompt them to ask questions about the logs as that is why you are made .
        User Question: {question}
        """
    
    return llm.invoke(prompt).content


# if __name__ == "__main__":
#     # Example usage
#     question = "give me the top 5 src_ip an`d their corresponding usernames"
#     result = run_sql_llm(question)
#     print(result['columns'])
#     print(result['result'])