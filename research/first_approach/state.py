from operator import add
from typing import List, Dict, Optional, Annotated
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages

class URLWithContext(TypedDict):
    research_question: str
    search_urls: List[str]
    search_context: str


def add_urls_with_context(existing: list[URLWithContext], update: list[URLWithContext] | str):
    """
    Sometimes the query generator returns queries and urls at the same time.
    In this case we need to treat the urls and queries separately. Urls are ready
    to be explored but we need to find promising search results for queries first.
    We wait that we have gotten the urls for every query and finally recombine them
    with the initial urls.
    """
    if update == "DELETE":
        return []
    
    grouped = {}
    for item in (existing or []) + update:
        if item['research_question'] in grouped:
            grouped[item['research_question']]['search_urls'].extend(item['search_urls'])
        else:
            grouped[item['research_question']] = item.copy()

    return list(grouped.values())

def extend_with_delete(existing: list, update: list | str):
    if update == "DELETE":
        return []
    return (existing or []) + update


class ProspectingAgentState(TypedDict, total=False):
    """
    State that stores data flowing between nodes in the research pipeline
    for generating a Prospect Engagement Report.

    Fields:
        seller_profile (str): A description of what the seller offers.
        business_info (Dict): Basic info about the target business (e.g., name, website).
        report_draft (str): The evolving draft of the Prospect Engagement Report.
        scratchpad (str): Internal notes, hypotheses, conflicts, and next steps.
        
        research_questions (List[str]): Up to 2 research questions that guide further exploration.
        queries_contexts (List[Dict]): Search queries and contextual information for each question.
        exploration_results (str): Summarized extracted information to be interpreted in the next step.
        final_report (str): The final refined version of the prospect engagement report.

        round_count (int): Number of completed research rounds.
        max_rounds (int): Maximum allowed number of research rounds.
        total_tokens_used (int): Total tokens consumed by LLM calls.
        max_tokens (int): Maximum allowed tokens for all LLM calls combined.
        num_google_searches (int): Total number of Google searches performed.
        max_google_searches (int): Maximum allowed Google searches.
        num_page_fetches (int): Total number of pages fetched.
        max_page_fetches (int): Maximum allowed pages to fetch.
    """


    # Prospecting fields (optional with defaults)
    seller_profile: NotRequired[str]
    business_info: NotRequired[Dict]

    report_draft: NotRequired[str]
    scratchpad: NotRequired[str]

    research_questions: Annotated[List[str], extend_with_delete]
    queries_with_context: Annotated[List[Dict], extend_with_delete]
    urls_with_context: Annotated[List[Dict], add_urls_with_context]

    exploration_results: NotRequired[str]
    final_report: NotRequired[str]

    round_count: NotRequired[int]
    max_rounds: NotRequired[int]
    total_tokens_used:  Annotated[int, add]
    max_tokens: NotRequired[int]
    num_google_searches: Annotated[int, add]
    max_google_searches: NotRequired[int]
    num_page_fetches: Annotated[int, add]
    max_page_fetches: NotRequired[int]


# Factory function to initialize default values
def create_default_state(
    seller_profile: Optional[str] = "",
    business_info: Optional[Dict] = None
) -> ProspectingAgentState:
    """
    Initializes the ProspectingState with default values.
    
    Args:
        name (str): Name of the target.
        birthday (str): Birthday or foundation date of the target.
        seller_profile (str, optional): Description of the seller’s offerings.
        business_info (Dict, optional): Basic information about the target business.

    Returns:
        ProspectingState: A state dictionary with all fields initialized.
    """
    return {
        "messages": [],
        "seller_profile": seller_profile,
        "business_info": business_info if business_info else {},
        "report_draft": "",
        "scratchpad": "",
        "research_questions": [],
        "queries_contexts": [],
        "exploration_results": "",
        "final_report": "",

        "round_count": 0,
        "max_rounds": 3,
        "total_tokens_used": 0,
        "max_tokens": 120000,
        "num_google_searches": 0,
        "max_google_searches": 6,
        "num_page_fetches": 0,
        "max_page_fetches": 15
    }