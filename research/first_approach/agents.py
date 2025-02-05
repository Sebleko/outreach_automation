"""
This file defines the Agents used in the langgraph workflow. Each agent corresponds
to one step in your original asynchronous process (e.g., generating queries, searching,
fetching page content, judging usefulness, extracting context, deciding on more queries, final report).
This version uses LangChain’s community wrappers for LLM calls and consistently uses
LangChain message objects for prompts.
"""

import ast
import json
import requests
from termcolor import colored

# External configuration or environment variables
#OPENAI_API_KEY = "REDACTED"
#SERPAPI_API_KEY = "REDACTED"
#JINA_API_KEY = "REDACTED"

SERPAPI_URL = "https://serpapi.com/search"
JINA_BASE_URL = "https://r.jina.ai/"
DEFAULT_MODEL = "gpt-4o-mini"

# Prompts (from your prompts.py, assumed to be available)
from prompts import (
    generate_search_queries_prompt,
    page_usefulness_prompt,
    extract_context_prompt,
    more_search_queries_prompt,
    final_report_prompt
)

#############################
# LangChain LLM configuration
#############################
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Create a global LLM instance with LangChain
llm = ChatOpenAI(
    model_name=DEFAULT_MODEL,
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
)

def call_llm(system_text: str, user_text: str) -> str:
    """
    Helper function that takes system text and user text, constructs LangChain
    message objects, calls the LLM, and returns the LLM's response content.
    """
    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=user_text)
    ]
    try:
        response = llm(messages)
        return response.content
    except Exception as e:
        print("Error calling LLM via LangChain:", e)
        return ""

###########################
# Agents (one step each)
###########################

class GenerateSearchQueriesAgent:
    """
    Ask the LLM to produce up to four precise search queries (in a Python list format).
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        user_query = self.state["user_query"]
        prompt = generate_search_queries_prompt.format(user_query=user_query)

        llm_response = call_llm(
            system_text="You are a helpful and precise research assistant.",
            user_text=prompt
        )

        search_queries = []
        if llm_response:
            try:
                # Safely parse the returned string as a Python list.
                parsed = ast.literal_eval(llm_response.strip())
                if isinstance(parsed, list):
                    search_queries = parsed
                else:
                    print("LLM did not return a list. Response:", llm_response)
            except Exception as e:
                print("Error parsing search queries:", e, "\nResponse:", llm_response)

        self.state["search_queries"] = search_queries
        print(colored(f"GenerateSearchQueriesAgent => {search_queries}", 'cyan'))
        return self.state


class SearchAgent:
    """
    Perform a Google search for each query using SERPAPI.
    Aggregates all unique links into state["links"] as a dict: { link: producing_query }.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        all_queries = self.state.get("search_queries", [])
        unique_links = {}

        for query in all_queries:
            params = {
                "q": query,
                "api_key": SERPAPI_API_KEY,
                "engine": "google"
            }
            try:
                resp = requests.get(SERPAPI_URL, params=params, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    if "organic_results" in data:
                        for item in data["organic_results"]:
                            link = item.get("link")
                            if link and link not in unique_links:
                                unique_links[link] = query
                    else:
                        print("No organic results in SERPAPI response.")
                else:
                    print(f"SERPAPI error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print("Error performing SERPAPI search:", e)

        self.state["links"] = unique_links
        print(colored(f"SearchAgent => Found {len(unique_links)} unique links", 'cyan'))
        return self.state


class FetchPageAgent:
    """
    Fetch the text content of each link using Jina, store the result in state["page_texts"] as { link: text }.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        links_dict = self.state.get("links", {})
        page_texts = {}

        for link in links_dict.keys():
            full_url = f"{JINA_BASE_URL}{link}"
            headers = {
                "Authorization": f"Bearer {JINA_API_KEY}"
            }
            try:
                resp = requests.get(full_url, headers=headers, timeout=60)
                if resp.status_code == 200:
                    page_texts[link] = resp.text
                else:
                    print(f"Jina fetch error for {link}: {resp.status_code} - {resp.text}")
                    page_texts[link] = ""
            except Exception as e:
                print(f"Error fetching webpage text with Jina for {link}:", e)
                page_texts[link] = ""

        self.state["page_texts"] = page_texts
        return self.state


class UsefulnessAgent:
    """
    For each link, ask the LLM if it is relevant ("Yes") or not ("No").
    Store the result in state["usefulness"] as { link: "Yes"|"No" }.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        user_query = self.state["user_query"]
        page_texts = self.state.get("page_texts", {})
        usefulness_map = {}

        for link, content in page_texts.items():
            if not content:
                usefulness_map[link] = "No"
                continue

            truncated = content[:20000]
            prompt = page_usefulness_prompt.format(
                user_query=user_query,
                page_content=truncated
            )

            llm_response = call_llm(
                system_text="You are a strict and concise evaluator of research relevance.",
                user_text=prompt
            )

            answer = llm_response.strip()
            # Normalize the answer
            if answer not in ["Yes", "No"]:
                if "Yes" in answer:
                    answer = "Yes"
                elif "No" in answer:
                    answer = "No"
                else:
                    answer = "No"

            usefulness_map[link] = answer

        self.state["usefulness"] = usefulness_map
        return self.state


class ExtractContextAgent:
    """
    For each link that is "Yes", extract relevant context using the LLM.
    Append each extracted context to state["aggregated_contexts"].
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        user_query = self.state["user_query"]
        links_dict = self.state.get("links", {})
        page_texts = self.state.get("page_texts", {})
        usefulness_map = self.state.get("usefulness", {})
        aggregated_contexts = self.state.get("aggregated_contexts", [])

        for link, query_used in links_dict.items():
            if usefulness_map.get(link) == "Yes":
                content = page_texts.get(link, "")
                if not content:
                    continue

                truncated = content[:20000]
                prompt = extract_context_prompt.format(
                    user_query=user_query,
                    search_query=query_used,
                    page_content=truncated
                )

                llm_response = call_llm(
                    system_text="You are an expert in extracting relevant information.",
                    user_text=prompt
                )
                extracted_text = llm_response.strip()
                if extracted_text:
                    aggregated_contexts.append(extracted_text)

        self.state["aggregated_contexts"] = aggregated_contexts
        return self.state


class CheckIfMoreSearchNeededAgent:
    """
    Ask the LLM if more searches are needed. If so, store them in state["search_queries"] and loop again.
    If no more searches are needed, store an empty list (or skip).
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        user_query = self.state["user_query"]
        all_contexts = self.state.get("aggregated_contexts", [])
        all_search_queries = self.state.get("all_search_queries", [])

        # Merge the newly used queries into all_search_queries
        for q in self.state.get("search_queries", []):
            if q not in all_search_queries:
                all_search_queries.append(q)

        prompt = more_search_queries_prompt.format(
            user_query=user_query,
            previous_search_queries=all_search_queries,
            all_contexts="\n".join(all_contexts)
        )

        llm_response = call_llm(
            system_text="You are a systematic research planner.",
            user_text=prompt
        )

        new_queries = []
        if llm_response:
            cleaned = llm_response.strip()
            if cleaned:
                try:
                    parsed = ast.literal_eval(cleaned)
                    if isinstance(parsed, list):
                        new_queries = parsed
                except Exception as e:
                    print("Error parsing new search queries:", e, "\nResponse:", cleaned)

        # Update the state
        self.state["all_search_queries"] = all_search_queries
        self.state["search_queries"] = new_queries
        self.state["continue_research"] = bool(new_queries)

        return self.state


class FinalReportAgent:
    """
    Generates the final report from all accumulated contexts.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        user_query = self.state["user_query"]
        all_contexts = self.state.get("aggregated_contexts", [])
        prompt = final_report_prompt.format(
            user_query=user_query,
            all_contexts="\n".join(all_contexts)
        )

        llm_response = call_llm(
            system_text="You are a skilled report writer.",
            user_text=prompt
        )
        final_report = llm_response if llm_response else "No report generated."
        self.state["final_report"] = final_report

        print(colored("==== FINAL REPORT ====", 'green'))
        print(colored(final_report, 'green'))
        return self.state


class EndNodeAgent:
    """
    Graph end. Just a pass-through or final display.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        print(colored("End of research flow.", 'magenta'))
        return self.state