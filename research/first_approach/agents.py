import requests_cache
from datetime import timedelta
from termcolor import colored
import tiktoken  # For token counting
import asyncio
from typing import Dict, Any

# Install caching to optimize repeated requests
requests_cache.install_cache('cache', backend='sqlite', expire_after=timedelta(days=7))

# Import prompts and schemas
from prompts import (
    interpretation_agent_prompt,
    planner_agent_prompt,
    query_generation_agent_prompt,
    select_search_results_prompt,
    extract_info_prompt,
    finalization_agent_prompt
)

from schemas import (
    InterpretationOutput,
    PlannerOutput,
    QueryGenerationOutput,
    SelectedSearchResults,
    ExtractedInfo,
    FinalReportOutput
)

# LangChain components
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# Import your abstracted backends
from search_backends import search
from fetch_backends import fetch_page

# Configure LangChain LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def count_tokens(prompt_text: str, completion_text: str = "", model_name: str = "gpt-4o-mini") -> int:
    """
    Approximate token counting for the prompt and completion using tiktoken.
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    prompt_tokens = len(encoder.encode(prompt_text))
    completion_tokens = len(encoder.encode(completion_text))
    return prompt_tokens + completion_tokens

def call_llm(prompt_template, input_data, schema):
    """
    Calls the LLM with a prompt and parses the output using the specified Pydantic schema.
    Returns a tuple: (parsed_output, tokens_used).
    
    Note: This function does NOT update the state.
    """
    parser = JsonOutputParser(pydantic_object=schema)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=[k for k in input_data.keys() if k != "state"],  # exclude "state" key
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    formatted_input = {k: v for k, v in input_data.items() if k != "state"}
    prompt_text = prompt.format(**formatted_input)
    
    chain = prompt | llm | parser
    output_obj = chain.invoke(formatted_input)
    
    completion_text = output_obj.json()
    used_tokens = count_tokens(prompt_text, completion_text)
    return output_obj, used_tokens

###########################
# Agents (Defined for Each Step)
###########################

class InterpretationAgent:
    """
    Interprets exploration results and updates the prospect engagement report draft.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def invoke(self) -> Dict[str, Any]:
        input_data = {
            "seller_profile": self.state.get("seller_profile", ""),
            "business_info": self.state.get("business_info", {}),
            "report_draft": self.state.get("report_draft", ""),
            "exploration_results": self.state.get("exploration_results", "")
        }
        response, tokens_used = call_llm(interpretation_agent_prompt, input_data, InterpretationOutput)
        print(colored("Report draft updated with exploration results.", 'cyan'))
        # Return a partial state update:
        return {
            "report_draft": response.report_draft,
            "total_tokens_used": tokens_used
        }


class PlannerAgent:
    """
    Analyzes the report and scratchpad to decide if further research is needed.
    Updates the scratchpad and outputs research questions if necessary.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def invoke(self) -> Dict[str, Any]:
        input_data = {
            "seller_profile": self.state.get("seller_profile", ""),
            "business_info": self.state.get("business_info", {}),
            "report_draft": self.state.get("report_draft", ""),
            "scratchpad": self.state.get("scratchpad", "")
        }
        response, tokens_used = call_llm(planner_agent_prompt, input_data, PlannerOutput)
        if not response.research_questions:
            print(colored("No further research required (Planner).", 'green'))
        else:
            print(colored(f"(Planner) Research questions generated: {response.research_questions}", 'cyan'))
        return {
            "scratchpad": response.scratchpad,
            "research_questions": response.research_questions,
            "total_tokens_used": tokens_used
        }


class QueryGenerationAgent:
    """
    Generates Google search queries and a search context for each research question.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    async def invoke(self) -> Dict[str, Any]:
        async def process_question(question: str, state: Dict[str, Any]):
            input_data = {
                "seller_profile": state.get("seller_profile", ""),
                "business_info": state.get("business_info", {}),
                "report_draft": state.get("report_draft", ""),
                "scratchpad": state.get("scratchpad", ""),
                "research_question": question
            }
            response, tokens_used = await call_llm(query_generation_agent_prompt, input_data, QueryGenerationOutput)

            return ({
                "research_question": question,
                "search_queries": response.search_queries,
                "search_context": response.search_context,
            }, tokens_used)

        queries_contexts = []
        total_tokens_spent = 0

        # Ensure we have at most 2 research questions
        assert(len(self.state.get("research_questions", [])) <= 2)

        for question in self.state.get("research_questions", []):
            task = process_question(question, self.state)
            result, tokens_used = await task
            queries_contexts.append(result)
            total_tokens_spent += tokens_used

        print(colored("Generated search queries for research questions.", 'cyan'))
        return {
            "queries_contexts": queries_contexts,
            "total_tokens_used": total_tokens_spent
        }


class SelectSearchResultsAgent:
    """
    Performs searches and selects promising results.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def invoke(self) -> Dict[str, Any]:
        selected_results = []
        total_tokens_spent = 0
        google_searches_made = 0

        

        for query_context in self.state.get("queries_contexts", []):
            all_search_results = []
            for query in query_context["search_queries"]:
                # Check if query is a URL
                if query.startswith("http"):
                    selected_results.append(query)
                    continue
                search_results = search(query)
                google_searches_made += 1
                all_search_results.extend(search_results)

            input_data = {
                "research_question": query_context["research_question"],
                "search_context": query_context["search_context"],
                "search_results": all_search_results
            }
            response, tokens_used = call_llm(select_search_results_prompt, input_data, SelectedSearchResults)
            total_tokens_spent += tokens_used
            selected_results.extend(response.selected_results)

        return {
            "selected_results": selected_results,
            "num_google_searches": google_searches_made,
            "total_tokens_used": total_tokens_spent
        }


class ExtractInfoAgent:
    """
    Fetches webpage content and extracts relevant information using the LLM.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def invoke(self) -> Dict[str, Any]:
        extracted_info_all = []
        exploration_summaries = []
        total_tokens_spent = 0
        page_fetches = 0

        first_query_context = {}
        if self.state.get("queries_contexts"):
            first_query_context = self.state["queries_contexts"][0]

        # Fetch pages first
        page_contents = {}
        for url in self.state.get("selected_results", []):
            content = fetch_page(url)
            page_fetches += 1
            page_contents[url] = content

        # Process fetched content
        for url, content in page_contents.items():
            if not content:
                continue

            input_data = {
                "seller_profile": self.state.get("seller_profile", ""),
                "business_info": self.state.get("business_info", {}),
                "research_question": first_query_context.get("research_question", ""),
                "search_context": first_query_context.get("search_context", ""),
                "known_info": "\n".join(self.state.get("known_info", [])),
                "page_content": content
            }
            response, tokens_used = call_llm(extract_info_prompt, input_data, ExtractedInfo)
            total_tokens_spent += tokens_used
            extracted_info_all.extend(response.relevant_info)

            summary_lines = []
            if response.relevant_info:
                summary_lines.append("**Relevant Info:**")
                summary_lines.extend(f"- {info}" for info in response.relevant_info)
            if response.conflicts:
                summary_lines.append("**Conflicts Detected:**")
                summary_lines.extend(f"- {c}" for c in response.conflicts)
            if response.interesting_insights:
                summary_lines.append("**Interesting Insights:**")
                summary_lines.extend(f"- {insight}" for insight in response.interesting_insights)
            if response.seller_benefit_possibilities:
                summary_lines.append("**Seller Benefit Possibilities:**")
                summary_lines.extend(f"- {possibility}" for possibility in response.seller_benefit_possibilities)

            if summary_lines:
                page_summary = f"### Extracted info from: {url}\n" + "\n".join(summary_lines)
                exploration_summaries.append(page_summary)

        previous_exploration = self.state.get("exploration_results", "")
        new_exploration = (previous_exploration + "\n\n" + "\n".join(exploration_summaries)).strip()

        print(colored(f"Extracted info from {len(extracted_info_all)} items.", 'cyan'))
        return {
            "known_info": extracted_info_all,
            "exploration_results": new_exploration,
            "num_page_fetches": page_fetches,
            "total_tokens_used": total_tokens_spent
        }


class FinalizationAgent:
    """
    Refines and finalizes the prospect engagement report.
    """
    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def invoke(self) -> Dict[str, Any]:
        input_data = {
            "seller_profile": self.state.get("seller_profile", ""),
            "business_info": self.state.get("business_info", {}),
            "report_draft": self.state.get("report_draft", ""),
            "scratchpad": self.state.get("scratchpad", "")
        }
        response, tokens_used = call_llm(finalization_agent_prompt, input_data, FinalReportOutput)
        print(colored("Final report refined and ready.", 'green'))
        return {
            "final_report": response.final_report,
            "total_tokens_used": tokens_used
        }