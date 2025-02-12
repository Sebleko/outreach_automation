import requests_cache
from datetime import timedelta
from termcolor import colored
import tiktoken  # For token counting
import asyncio
from typing import Dict, Any

from state import ProspectingAgentState

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

async def call_llm(prompt_template, input_data, schema):
    """
    Calls the LLM with a prompt and parses the output using the specified Pydantic schema.
    Returns a tuple: (parsed_output, tokens_used).
    
    Note: This function does NOT update the state.
    """
    parser = JsonOutputParser(pydantic_object=schema)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=[k for k in input_data.keys()],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    formatted_input = {k: v for k, v in input_data.items() if k != "state"}
    prompt_text = prompt.format(**formatted_input)
    
    chain = prompt | llm | parser
    output_obj = await chain.ainvoke(formatted_input)
    
    completion_text = str(output_obj)
    used_tokens = count_tokens(prompt_text, completion_text)
    return output_obj, used_tokens

###########################
# Refactored Agents as Async Functions
###########################

async def interpretation_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Interprets exploration results and updates the prospect engagement report draft.
    """
    input_data = {
        "seller_profile": state.get("seller_profile", ""),
        "business_info": state.get("business_info", {}),
        "report_draft": state.get("report_draft", ""),
        "exploration_results": state.get("exploration_results", "")
    }
    response, tokens_used = await call_llm(interpretation_agent_prompt, input_data, InterpretationOutput)
    print(colored("Report draft updated with exploration results.", 'cyan'))
    # Return a partial state update:
    return {
        "report_draft": response["report_draft"],
        "total_tokens_used": tokens_used
    }

async def planner_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Analyzes the report and scratchpad to decide if further research is needed.
    Updates the scratchpad and outputs research questions if necessary.
    """
    input_data = {
        "seller_profile": state.get("seller_profile", ""),
        "business_info": state.get("business_info", {}),
        "report_draft": state.get("report_draft", ""),
        "scratchpad": state.get("scratchpad", "")
    }
    
    response, tokens_used = await call_llm(planner_agent_prompt, input_data, PlannerOutput)
    print("Response", response, tokens_used)
    return {
        "scratchpad": response["scratchpad"],
        "research_questions": response["research_questions"],
        "total_tokens_used": tokens_used
    }

async def query_generation_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Generates Google search queries and a search context for each research question.
    """
    async def process_question(question: str, s: Dict[str, Any]):
        input_data = {
            "seller_profile": s.get("seller_profile", ""),
            "business_info": s.get("business_info", {}),
            "report_draft": s.get("report_draft", ""),
            "scratchpad": s.get("scratchpad", ""),
            "research_question": question
        }
        print("QG: Calling llm with, Input data", input_data)
        response, tokens_used = await call_llm(query_generation_agent_prompt, input_data, QueryGenerationOutput)
        return ({
            "research_question": question,
            "search_queries": response["search_queries"],
            "search_context": response["search_context"],
        }, tokens_used)

    queries_with_contexts = []
    urls_with_contexts = []
    total_tokens_spent = 0

    # Ensure we have at most 2 research questions
    assert(len(state.get("research_questions", [])) <= 2)

    tasks = [process_question(question, state) for question in state.get("research_questions", [])]
    
    for task in asyncio.as_completed(tasks):
        result, tokens_used = await task
        
        queries = [q for q in result["search_queries"] if not q.startswith("http")]
        urls = [u for u in result["search_queries"] if u.startswith("http")]
        
        queries_with_contexts.append({
            "research_question": result["research_question"],
            "search_queries": queries,
            "search_context": result["search_context"]
        })
        urls_with_contexts.append({
            "research_question": result["research_question"],
            "search_urls": urls,
            "search_context": result["search_context"]
        })

        total_tokens_spent += tokens_used

    print(colored("Generated search queries for research questions.", 'cyan'))

    return {
        "queries_with_contexts": queries_with_contexts,
        "urls_with_contexts": urls_with_contexts,
        "total_tokens_used": total_tokens_spent
    }

async def select_search_results_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Performs searches and selects promising results.
    """
    urls_with_contexts = []
    total_tokens_spent = 0
    google_searches_made = 0

    async def process_query_context(query_context: Dict[str, Any]):
        # Create tasks for parallel searches
        search_tasks = [search(q) for q in query_context["search_queries"]]
        
        # Execute searches in parallel
        all_search_results = []
        for coro in asyncio.as_completed(search_tasks):
            results = await coro
            nonlocal google_searches_made
            google_searches_made += 1
            all_search_results.extend(results)

        # Process results with LLM
        input_data = {
            "research_question": query_context["research_question"],
            "search_context": query_context["search_context"],
            "search_results": all_search_results
        }
        response, tokens_used = await call_llm(select_search_results_prompt, input_data, SelectedSearchResults)
        urls_and_context = {
            "research_question": query_context["research_question"],
            "search_urls": response["selected_results"],
            "search_context": query_context["search_context"]
        }
        return urls_and_context, tokens_used

    tasks = [process_query_context(qc) for qc in state.get("queries_with_contexts", [])]
    
    for task in asyncio.as_completed(tasks):
        result, tokens = await task
        urls_with_contexts.append(result)
        total_tokens_spent += tokens

    return {
        "urls_with_contexts": urls_with_contexts,
        "num_google_searches": google_searches_made,
        "total_tokens_used": total_tokens_spent
    }

async def extract_info_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Fetches webpage content and extracts relevant information using the LLM.
    """
    extracted_info_all = []
    exploration_summaries = []
    total_tokens_spent = 0
    page_fetches = 0

    async def process_url_context(url_context: Dict[str, Any]):
        nonlocal page_fetches
        
        fetches = [fetch_page(url) for url in url_context.get("search_urls", [])]
        
        # Wait for all fetches to complete
        fetch_results = await asyncio.gather(*fetches)
        page_fetches += len(fetch_results)
        
        processing_tasks = []
        for url, content_coro in zip(url_context["search_urls"], fetch_results):
            content = await content_coro
            if not content:
                continue

            input_data = {
                "seller_profile": state.get("seller_profile", ""),
                "business_info": state.get("business_info", {}),
                "research_question": url_context["research_question"],
                "search_context": url_context["search_context"],
                "page_content": content
            }
            processing_tasks.append(call_llm(extract_info_prompt, input_data, ExtractedInfo))

        # Process all pages in parallel
        results = await asyncio.gather(*processing_tasks)
        
        local_summaries = []
        local_info = []
        
        for (response, tokens_used), url in zip(results, url_context["search_urls"]):
            nonlocal total_tokens_spent
            total_tokens_spent += tokens_used
            local_info.extend(response["relevant_info"])

            summary_lines = []
            if response["relevant_info"]:
                summary_lines.append("**Relevant Info:**")
                summary_lines.extend(f"- {info}" for info in response["relevant_info"])
            if response["conflicts"]:
                summary_lines.append("**Conflicts Detected:**")
                summary_lines.extend(f"- {c}" for c in response["conflicts"])
            if response["interesting_insights"]:
                summary_lines.append("**Interesting Insights:**")
                summary_lines.extend(f"- {insight}" for insight in response["interesting_insights"])
            if response["seller_benefit_possibilities"]:
                summary_lines.append("**Seller Benefit Possibilities:**")
                summary_lines.extend(f"- {possibility}" for possibility in response["seller_benefit_possibilities"])

            if summary_lines:
                page_summary = (
                    f"### Extracted info from: {url}\n"
                    f"### Trying to research: {url_context['research_question']}\n"
                    + "\n".join(summary_lines)
                )
                local_summaries.append(page_summary)
        
        return local_info, local_summaries

    tasks = [process_url_context(uc) for uc in state.get("urls_with_contexts", [])]
    results = await asyncio.gather(*tasks)
    
    for info, summaries in results:
        extracted_info_all.extend(info)
        exploration_summaries.extend(summaries)

    print(colored(f"Extracted info from {len(extracted_info_all)} items.", 'cyan'))
    return {
        "exploration_results": exploration_summaries, 
        "num_page_fetches": page_fetches,
        "total_tokens_used": total_tokens_spent
    }

async def finalization_agent(state: ProspectingAgentState) -> Dict[str, Any]:
    """
    Refines and finalizes the prospect engagement report.
    """
    input_data = {
        "seller_profile": state.get("seller_profile", ""),
        "business_info": state.get("business_info", {}),
        "report_draft": state.get("report_draft", ""),
        "scratchpad": state.get("scratchpad", "")
    }
    response, tokens_used = await call_llm(finalization_agent_prompt, input_data, FinalReportOutput)
    print(colored("Final report refined and ready.", 'green'))
    return {
        "final_report": response["final_report"],
        "total_tokens_used": tokens_used
    }