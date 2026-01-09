
from openai import OpenAI, APIConnectionError
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import streamlit as st
from OldCode.gpts.tools import TOOLS3
import json

# from gpts.tools import TOOLS

# TOOLS = [{
#     "type": "function",
#     "function": {
#         "name": "create_company_profile",
#         "description": "Call when the user says something similar to: 'Create a company profile (CompanyName)'. Extract the name inside parentheses.",
#         "parameters": {
#             "type": "object",
#             "properties": {"companyName": {"type": "string"}},
#             "required": ["companyName"],
#             "additionalProperties": False,
#         },
#     },
#     "function": {
#     "name": "add_company",
#     "description": "Call when the user says something similar to: 'Add this company (CompanyNumber)'. Extract the number sequence inside parentheses.",
#     "parameters": {
#         "type": "object",
#         "properties": {"companyNumber": {"type": "string"}},
#         "required": ["companyNumber"],
#         "additionalProperties": False,
#         },
#     },
# }]

def question_to_machine(question, OPENAI_API_KEY, model='gpt-5'):

    """
        This function receives the question the user originally wrote
        and rewrite it in an easier way for the Search and GPT.
    """

    web_openai = OpenAI(api_key=OPENAI_API_KEY)


    system_msg = """
        You are a RAG pipeline assistant of a financial analyst. 

        You receive questions given by people and you transform the original question into a more meaningful question to optimize Vector Search and Web Search.

        Prioritize the rewriting of the phrase to optimize vector search

        Guidelines:

        -ALWAYS state in the beginning of your answer the INFORMATION SOURCE SECTION to answer that question. The following SOURCES combinations are possible: annual reporting, annual reporting + web search, websearch. 
        -- IF the user states WEB SEARCH ONLY, cite in the question only WEB SEARCH.
        -- IF the user states annual report, cite in the question only ANNUAL REPORT.
        -- IF the user DOESNT state any source, assume ANNUAL REPORT.
        -- Otherwise always cite ANNUAL REPORT + WEB SEARCH.

        - WEB SEARCH NAVIGATION INSTRUCTIONS
        -- IF the SOURCE cites WEB SEARCH or ANNUAL REPORT + WEB SEARCH, follow these instructions
        -- Consider optimizing the question for WEB SEARCH as well.
    """
    user_msg = f"User Question: \n{question}"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg},
    ]

    try:
        resp = web_openai.responses.create(
            model=model,
            input=messages
        )

    except APIConnectionError as e:
        answer_text = f"Connection error calling OpenAI: {e}"

    return resp


def maybe_route_to_action(prompt, client, deployment) -> bool:
    """
    Returns True if the tool was invoked and handled here (so skip RAG),
    otherwise False to continue with your normal RAG flow.
    """
    sys_msg = """
        You are a router. 
        If the user asks to 'Create company profile (Name)', call the function with the extracted name. Otherwise, do nothing.
        If the user asks to 'Add company (Number)', call the function with the extracted number. Otherwise, do nothing.
        If the user asks for information with SOURCE or INFORMATION as 'web search', call the function 'web_search'.Otherwise, do nothing.
        If the user asks for information with SOURCE or INFORMATION as 'annual report + web_search', call the function 'web_search_duo'.Otherwise, do nothing.
    """

    try:
        resp = client.chat.completions.create(
            model=deployment,
            tools=TOOLS3,
            tool_choice="auto",
            messages=[
                {"role": "system",
                 "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
        )
    except APIConnectionError:
        return False

    msg = resp.choices[0].message
    calls = getattr(msg, "tool_calls", None)

    return calls 


def summarizer(prompt, prompt2, OPENAI_API_KEY, deployment, reasoning_effort = "high") -> bool:
    """
    Designed to receive two text inputs and create a 
    summary out of them in order to join both prompts into one
    """
    web_openai = OpenAI(api_key=OPENAI_API_KEY)

    try:
        resp = web_openai.responses.create(
            model=deployment,
            input=[
                {"role": "system",
                 "content": """
                    You are a financial analyst assistant.
                    You receive two prompts and create concise and complete summaries where you ALWAYS give especial attention to financial metrics, financial statements. 
                    ALWAYS quote the sources used in every paragraph
                 """},
                {"role": "user", 
                 "content": f""" 
                    Prompt One: \n {prompt} Prompt Two: \n {prompt2}
                """},
            ],
            reasoning={"effort": reasoning_effort}
        )
    except APIConnectionError:
        return False

    return resp.output_text

def general_assistant(prompt_sys, prompt_user, OPENAI_API_KEY, deployment, reasoning_effort = "medium") -> bool:
    """
    Designed to receive two text inputs and create a 
    summary out of them in order to join both prompts into one
    """
    web_openai = OpenAI(api_key=OPENAI_API_KEY)

    REASONING_MODELS = {
    "o3", "o3-mini", "o3-mini-high", "o4-mini",'gpt-5'
    }

    NON_REASONING_MODELS = {
        "gpt-4o", "gpt-4.1", "gpt-4.1-mini",
    }   

    if deployment in NON_REASONING_MODELS:
        try:
            resp = web_openai.responses.create(
                model=deployment,
                input=[
                    {"role": "system",
                    "content": f"""
                        {prompt_sys}
                    """},
                    {"role": "user", 
                    "content": f"""Input: \n {prompt_user}
                    """},
                ]
            )
        except APIConnectionError:
            return False
    elif deployment in REASONING_MODELS:
        try:
            resp = web_openai.responses.create(
                model=deployment,
                input=[
                    {"role": "system",
                    "content": f"""
                        {prompt_sys}
                    """},
                    {"role": "user", 
                    "content": f"""Input: \n {prompt_user}
                    """},
                ],
                reasoning={"effort": reasoning_effort}
            )
        except APIConnectionError:
            return False

    return resp.output_text

# def get_companies():

#     client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(ADMIN_KEY))

#     # Replace with your actual field names:
#     KEY_FIELD = "id"  # or "metadata_storage_path"
#     fields = [KEY_FIELD, "parent_id", "chunk_id"]  # parent_id/chunk_id exist if you used the wizard

#     results = client.search(search_text="*", select=fields, top=1000)  # page as needed
#     ids = [(doc.get(KEY_FIELD), doc.get("parent_id"), doc.get("chunk_id")) for doc in results]
