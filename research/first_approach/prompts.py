# prompts.py

"""
This file contains the prompt templates used by each agent in the research flow.
You can fine-tune these prompts to reflect your desired system instructions and content style.
"""

# Prompt for generating search queries
generate_search_queries_prompt = """
You are an expert research assistant. The user has asked a query: {user_query}.

Your task: Generate up to four distinct, precise search queries that would help gather comprehensive information on the topic. 
Return ONLY a Python list of strings, for example: ['query1', 'query2', 'query3'].
"""

# Prompt for checking if a page is useful
page_usefulness_prompt = """
You are a critical research evaluator. The user query is:

{user_query}

The webpage content (truncated) is:
{page_content}

Determine if the webpage contains information relevant and useful for addressing the query. 
Respond with EXACTLY one word: 'Yes' if the page is useful, or 'No' if not.
"""

# Prompt for extracting context
extract_context_prompt = """
You are an expert information extractor.

Given the user's query:
{user_query}

Search query used:
{search_query}

Webpage content (truncated):
{page_content}

Extract all pieces of information that are relevant to answering the user's query. 
Return ONLY the relevant context as plain text (no extra commentary).
"""

# Prompt for checking if more search queries are needed
more_search_queries_prompt = """
You are an analytical research assistant. 
Given the original user query: {user_query}
The previously used search queries: {previous_search_queries}
All extracted contexts so far:
{all_contexts}

Decide if further research (i.e., additional queries) is needed. 
- If further research is needed, return a Python list (like ['query1', 'query2']) with up to four new search queries.
- If no further research is needed, respond with an EMPTY string (i.e., "").
"""

# Prompt for final report
final_report_prompt = """
You are an expert researcher and report writer.

The user query is:
{user_query}

Below is the gathered relevant context:
{all_contexts}

Write a comprehensive, well-structured, and detailed report that addresses the user's query thoroughly, 
including all relevant insights and conclusions.
Return the final report as plain text.
"""