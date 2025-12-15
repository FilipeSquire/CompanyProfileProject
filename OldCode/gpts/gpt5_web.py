# app.py
import os
import textwrap
from dotenv import load_dotenv, find_dotenv
import json
from rags.rag import (
    retrieve_hybrid_enhanced,
    build_context,
    get_aoai_client
)
from typing import List, Dict, Optional
from gpts.gpt_assistants import question_to_machine, summarizer, general_assistant, maybe_route_to_action
from openai import OpenAI, APIConnectionError
import streamlit as st
from prompts import default_gpt_prompt
import time
load_dotenv(find_dotenv(), override=True)

# ---- Config (same Azure Search envs you already use) ----
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX    = os.environ["AZURE_SEARCH_INDEX"]
SEARCH_KEY      = os.getenv("AZURE_SEARCH_API_KEY")  # omit if using AAD/RBAC
VECTOR_FIELD    = os.getenv("VECTOR_FIELD")
TEXT_FIELD      = os.getenv("TEXT_FIELD")

# ---- OpenAI (standard) config ----
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")        # required
OPENAI_MODEL    = os.getenv("FELIPE_OPENAI_MODEL", "gpt-5")  # e.g., "gpt-5" or "gpt-5-mini"


class WebAgent():

    """
        - This class is responsible to operate calls and allow the usage of websearch
        - The websearch is activated through chat by mentioning "web search" in the paragraph
    """

    def __init__(self,
                k: int = 50,
                max_text_recall_size: int = 200,
                # max_chars: int,
                model: Optional[str] = OPENAI_MODEL,
                top = 20,
                max_output_tokens: int = 1200,
                reasoning_effort: str = "medium",      # "minimal" | "low" | "medium" | "high"
                verbosity: str = "medium",                 # "low" | "medium" | "high"
                tool_choice: str = "none",              # "none" | "auto" | {"type":"tool","name":"..."}
                streaming: bool = False
                ):

        # Parameters settings
        # self.company_name = company_name
        self.k = k
        self.max_text_recall_size = max_text_recall_size
        # self.max_chars = max_chars
        # ===================================
        # RAG PARAMETERS
        self.top = top
        self.k = k
        self.max_text_recall_size

        # ===================================
        # LLM settings
        self.model = model
        # self.temperature = temperature
        # self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort
        self.verbosity = verbosity
        self.streaming = streaming

        # OpenAI standard client
        self.web_openai = OpenAI(api_key=OPENAI_API_KEY)
        self.client = get_aoai_client()

    
    def _web_search(self, messages):
        resp = self.web_openai.responses.create(
            model=self.model,
            input=messages,
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            # max_output_tokens=self.max_output_tokens,
            reasoning={"effort": self.reasoning_effort},
            text={"verbosity": self.verbosity},
        )
        
        return resp.output_text
    
    def _web_off(self, messages):

        resp_off = self.web_openai.responses.create(
                model=self.model,
                input=messages,
                # max_output_tokens=self.max_output_tokens,
                reasoning={"effort": "high"},
                text={"verbosity": self.verbosity},
                )
        resp_off_answer = resp_off.output_text
        return resp_off_answer

    def _answer(self, question, stream = False):

        # 1. TRANSLATE TO MACHINE

        opt_user_query = question_to_machine(question, OPENAI_API_KEY)
        new_user_query = opt_user_query.output_text

        # 2. TOOL DETECTOR

        calls = maybe_route_to_action(new_user_query, self.client, self.model)
        
        if calls: #if no action detected, normal proccess
        # 3. PIPELINE CALL
            for call in calls:
                if call.function.name == "web_search":

                    try:
                        messages = [
                            {"role": "system", "content": default_gpt_prompt},
                            {"role": "user",   "content": new_user_query},
                        ]
                        
                        resp = self._web_search(messages)
                        return resp

                    except Exception as e:
                        return f'Activated web search but found error {e}'
                    
                elif call.function.name == "web_search_duo":
                    
                    # SPLITTING THE TEXT FOR EACH SOURCE
                    instruction = """
                    You are a financial assistant that receive instructions with multiple sources, and splits the request by source.
                    GIVE AS OUTPUT the parts of the question that DOESNT require the USE of WEB SEARCH.
                    """
                    offline_question = general_assistant(instruction, new_user_query, OPENAI_API_KEY, 'o3')
                    time.sleep(1.2)
                    instruction = """
                    You are a financial assistant that receive instructions with multiple sources, and splits the request by source.
                    GIVE AS OUTPUT the parts of the question that REQUIRES the use of WEB SEARCH.

                    Transform them into question optimized for web search
                    """
                    online_question = general_assistant(instruction, new_user_query, OPENAI_API_KEY, 'o3')
                    time.sleep(1.2)

                    # RETRIEVING THE ANSWERS
                    messages = [
                        {"role": "system", "content": default_gpt_prompt},
                        {"role": "user",   "content": online_question},
                    ]
                    resp_on_answer = self._web_search(messages)
                    time.sleep(1.2)
                
                    mode, hits = retrieve_hybrid_enhanced(query=offline_question, top = self.top, k = self.k, max_text_recall_size = self.max_text_recall_size)
                    ctx = build_context(hits)

                    user_msg = f"Question:\n{offline_question}\n\nContext snippets (numbered):\n{ctx}"

                    messages = [
                        {"role": "system", "content": default_gpt_prompt},
                        {"role": "user",   "content": user_msg},
                    ]
                    time.sleep(40)
                    resp_off_answer = self._web_off(messages=messages)
                    print('Done resp off')

                    time.sleep(1.2)
                    summary = summarizer(resp_on_answer, resp_off_answer, OPENAI_API_KEY, self.model)

                    return summary
        
        
        # 2. RETRIEVE
        mode, hits = retrieve_hybrid_enhanced(query=new_user_query, top = self.top, k = self.k, max_text_recall_size = self.max_text_recall_size)
        ctx = build_context(hits)

        # 3. Call GPT
        system_msg = default_gpt_prompt

        user_msg = f"Question:\n{new_user_query}\n\nContext snippets (numbered):\n{ctx}"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]
        
        answer_text = self._web_off(messages=messages)

        return answer_text