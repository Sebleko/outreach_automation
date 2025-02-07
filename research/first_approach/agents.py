"""
This file defines the Agents used in the langgraph workflow. Each agent corresponds
to one step in the business prospecting process (e.g., interpreting exploration results,
generating queries, selecting search results, extracting information, and refining the final report).
It uses LangChain's community wrappers and Pydantic schemas for structured output.
"""

import requests
import requests_cache
from datetime import timedelta
from termcolor import colored

# Install caching to optimize repeated requests
requests_cache.install_cache('cache', backend='sqlite', expire_after=timedelta(days=7))

# External API keys (replace with your actual keys)
SERPAPI_KEY = "YOUR_SERPAPI_KEY"
JINA_API_KEY = "YOUR_JINA_API_KEY"

# Import prompts and schemas
from prompts import (
    interpretation_agent_prompt,
    strategy_agent_prompt,
    query_generation_agent_prompt,
    select_search_results_prompt,
    extract_info_prompt,
    finalization_agent_prompt
)

from schemas import (
    InterpretationOutput,
    StrategyOutput,
    QueryGenerationOutput,
    SelectedSearchResults,
    ExtractedInfo,
    FinalReportOutput
)

# LangChain components
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# Configure LangChain LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def call_llm(prompt_template, input_data, schema):
    """
    Calls the LLM with a prompt and parses the output using the specified Pydantic schema.
    """
    parser = JsonOutputParser(pydantic_object=schema)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=list(input_data.keys()),
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm | parser
    return chain.invoke(input_data)

###########################
# Agents (Defined for Each Step)
###########################

class InterpretationAgent:
    """
    Interprets exploration results and updates the prospect engagement report draft.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        input_data = {
            "seller_profile": self.state["seller_profile"],
            "business_info": self.state["business_info"],
            "report_draft": self.state.get("report_draft", ""),
            "exploration_results": self.state.get("exploration_results", "")
        }

        response = call_llm(interpretation_agent_prompt, input_data, InterpretationOutput)
        self.state["report_draft"] = response.report_draft

        print(colored("Report draft updated with exploration results.", 'cyan'))
        return self.state


class StrategyAgent:
    """
    Analyzes the report and scratchpad to decide if further research is needed.
    Updates the scratchpad and outputs research questions if necessary.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        input_data = {
            "seller_profile": self.state["seller_profile"],
            "business_info": self.state["business_info"],
            "report_draft": self.state["report_draft"],
            "scratchpad": self.state.get("scratchpad", "")
        }

        response = call_llm(strategy_agent_prompt, input_data, StrategyOutput)
        self.state["scratchpad"] = response.scratchpad
        self.state["research_questions"] = response.research_questions

        if not response.research_questions:
            print(colored("No further research required.", 'green'))
        else:
            print(colored(f"Research questions generated: {response.research_questions}", 'cyan'))

        return self.state


class QueryGenerationAgent:
    """
    Generates Google search queries and a search context for each research question.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        queries_contexts = []

        for question in self.state["research_questions"]:
            input_data = {
                "seller_profile": self.state["seller_profile"],
                "business_info": self.state["business_info"],
                "report_draft": self.state["report_draft"],
                "scratchpad": self.state["scratchpad"],
                "research_question": question
            }

            response = call_llm(query_generation_agent_prompt, input_data, QueryGenerationOutput)
            queries_contexts.append({
                "research_question": question,
                "search_queries": response.search_queries,
                "search_context": response.search_context
            })

        self.state["queries_contexts"] = queries_contexts
        print(colored(f"Generated search queries for research questions.", 'cyan'))
        return self.state


class SelectSearchResultsAgent:
    """
    Performs Google searches using SERPAPI and selects promising results.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        selected_results = []

        for query_context in self.state["queries_contexts"]:
            search_results = []
            for query in query_context["search_queries"]:
                params = {
                    "q": query,
                    "api_key": SERPAPI_KEY,
                    "engine": "google"
                }
                try:
                    response = requests.get("https://serpapi.com/search", params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    search_results.extend(data.get("organic_results", []))
                except Exception as e:
                    print(f"Error performing SERPAPI search for '{query}':", e)

            input_data = {
                "research_question": query_context["research_question"],
                "search_context": query_context["search_context"],
                "search_results": search_results
            }

            response = call_llm(select_search_results_prompt, input_data, SelectedSearchResults)
            selected_results.extend(response.selected_results)

        self.state["selected_results"] = selected_results
        return self.state


class FetchPageAgent:
    """
    Fetches webpage content using Jina.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        page_contents = {}
        for url in self.state.get("selected_results", []):
            headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
            try:
                response = requests.get(f"https://r.jina.ai/{url}", headers=headers, timeout=30)
                if response.status_code == 200:
                    page_contents[url] = response.text
                else:
                    page_contents[url] = ""
            except Exception as e:
                print(f"Error fetching page {url} using Jina:", e)
                page_contents[url] = ""

        self.state["page_contents"] = page_contents
        return self.state


class ExtractInfoAgent:
    """
    Extracts relevant information from the fetched pages using the LLM.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        extracted_info = []

        for url, content in self.state.get("page_contents", {}).items():
            if not content:
                continue

            input_data = {
                "seller_profile": self.state["seller_profile"],
                "business_info": self.state["business_info"],
                "research_question": self.state["queries_contexts"][0]["research_question"],
                "search_context": self.state["queries_contexts"][0]["search_context"],
                "known_info": "\n".join(self.state.get("known_info", [])),
                "page_content": content
            }

            response = call_llm(extract_info_prompt, input_data, ExtractedInfo)
            extracted_info.extend(response.relevant_info)
            self.state["known_info"].extend(response.relevant_info)

            if response.conflicts:
                self.state["scratchpad"] += "\nConflicts:\n" + "\n".join(response.conflicts)

        print(colored(f"Extracted info from {len(extracted_info)} items.", 'cyan'))
        return self.state


class FinalizationAgent:
    """
    Refines and finalizes the prospect engagement report when research is complete.
    """
    def __init__(self, state):
        self.state = state

    def invoke(self):
        input_data = {
            "seller_profile": self.state["seller_profile"],
            "business_info": self.state["business_info"],
            "report_draft": self.state["report_draft"],
            "scratchpad": self.state.get("scratchpad", "")
        }

        response = call_llm(finalization_agent_prompt, input_data, FinalReportOutput)
        self.state["final_report"] = response.final_report

        print(colored("Final report refined and ready.", 'green'))
        return self.state