# agents.py

"""
This file defines the Agents used in the langgraph workflow. Each agent corresponds
to one step in your original asynchronous process (e.g., generating queries, searching,
fetching page content, judging usefulness, extracting context, deciding on more queries, final report).
Adapt the exact LLM calls, SerpAPI usage, Jina usage, or other integrations to match your environment.
"""

import json
import requests  # or httpx, or any library you prefer
from termcolor import colored

# You might store or load these from environment variables or a config file.
OPENROUTER_API_KEY = "REDACTED"
SERPAPI_API_KEY = "REDACTED"
JINA_API_KEY = "REDACTED"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPAPI_URL = "https://serpapi.com/search"
JINA_BASE_URL = "https://r.jina.ai/"
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"

# Prompts
from prompts import (
    generate_search_queries_prompt,
    page_usefulness_prompt,
    extract_context_prompt,
    more_search_queries_prompt,
    final_report_prompt
)

##################
# Helper LLM call
##################

def call_openrouter(messages, model=DEFAULT_MODEL):
    """
    Calls OpenRouter's chat completion endpoint with the provided messages.
    Returns the content of the assistant's reply or None on error.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "OpenDeepResearcher, by Matt Shumer",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"OpenRouter error: {resp.status_code}, {resp.text}")
    except Exception as e:
        print("Error calling OpenRouter:", e)
    return None

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
        messages = [
            {"role": "system", "content": "You are a helpful and precise research assistant."},
            {"role": "user", "content": prompt}
        ]
        response = call_openrouter(messages)
        if response:
            try:
                # Expect exactly a Python list (e.g., "['query1', 'query2']")
                search_queries = eval(response.strip())
                if isinstance(search_queries, list):
                    self.state["search_queries"] = search_queries
                else:
                    print("LLM did not return a list. Response:", response)
                    self.state["search_queries"] = []
            except Exception as e:
                print("Error parsing search queries:", e, "\nResponse:", response)
                self.state["search_queries"] = []
        else:
            self.state["search_queries"] = []

        print(colored(f"GenerateSearchQueriesAgent => {self.state['search_queries']}", 'cyan'))
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
    For each link, call the LLM to see if it is relevant ("Yes") or not ("No").
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
            messages = [
                {"role": "system", "content": "You are a strict and concise evaluator of research relevance."},
                {"role": "user", "content": prompt}
            ]
            response = call_openrouter(messages)
            if response:
                answer = response.strip()
                # Try to handle minor misformat
                if answer not in ["Yes", "No"]:
                    if "Yes" in answer:
                        answer = "Yes"
                    elif "No" in answer:
                        answer = "No"
                    else:
                        answer = "No"
            else:
                answer = "No"

            usefulness_map[link] = answer

        self.state["usefulness"] = usefulness_map
        return self.state


class ExtractContextAgent:
    """
    For each link that is "Yes", extract relevant context using the LLM.
    Appends each extracted context to state["aggregated_contexts"].
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
                messages = [
                    {"role": "system", "content": "You are an expert in extracting relevant information."},
                    {"role": "user", "content": prompt}
                ]
                response = call_openrouter(messages)
                if response:
                    extracted_text = response.strip()
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
        # The newly used queries are in self.state["search_queries"]. Merge them:
        for q in self.state["search_queries"]:
            if q not in all_search_queries:
                all_search_queries.append(q)

        prompt = more_search_queries_prompt.format(
            user_query=user_query,
            previous_search_queries=all_search_queries,
            all_contexts="\n".join(all_contexts)
        )

        messages = [
            {"role": "system", "content": "You are a systematic research planner."},
            {"role": "user", "content": prompt}
        ]
        response = call_openrouter(messages)
        new_queries = []
        if response is not None:
            cleaned = response.strip()
            if cleaned:
                try:
                    new_queries = eval(cleaned)
                    if not isinstance(new_queries, list):
                        new_queries = []
                except Exception as e:
                    print("Error parsing new search queries:", e, "\nResponse:", cleaned)

        # Update the state
        self.state["all_search_queries"] = all_search_queries
        self.state["search_queries"] = new_queries
        self.state["continue_research"] = bool(new_queries)  # True if we got more queries

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
        messages = [
            {"role": "system", "content": "You are a skilled report writer."},
            {"role": "user", "content": prompt}
        ]
        response = call_openrouter(messages)
        final_report = response if response else "No report generated."
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