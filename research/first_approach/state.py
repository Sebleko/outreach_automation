from operator import add
from typing import List, Dict, Optional, Annotated
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages


class QueryWithContext(TypedDict):
    pass

class ProspectingAgentState(TypedDict, total=False):
    """
    State that stores data flowing between nodes in the research pipeline
    for generating a Prospect Engagement Report.

    Fields:
        messages (List): Conversation history messages. Integrated with LangGraph's message system.
        name (str): The name of the target person or business.
        birthday (str): The birthday of the target person or business foundation date.
        
        seller_profile (str): A description of what the seller offers.
        business_info (Dict): Basic info about the target business (e.g., name, website).
        report_draft (str): The evolving draft of the Prospect Engagement Report.
        scratchpad (str): Internal notes, hypotheses, conflicts, and next steps.
        
        research_questions (List[str]): Up to 2 research questions that guide further exploration.
        queries_contexts (List[Dict]): Search queries and contextual information for each question.
        selected_results (List[str]): URLs selected as promising from Google search results.
        page_contents (Dict[str, str]): Maps URLs to fetched webpage content.
        known_info (List[str]): Bullet points of relevant information extracted so far.
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

    # Required fields
    messages: Annotated[List, add_messages]
    name: str
    birthday: str

    # Prospecting fields (optional with defaults)
    seller_profile: NotRequired[str]
    business_info: NotRequired[Dict]
    report_draft: NotRequired[str]
    scratchpad: NotRequired[str]

    research_questions: NotRequired[List[str]]

    queries_contexts: NotRequired[List[Dict]]

    ready_for_fetching: Annotated[List[Dict], add]



    selected_results: NotRequired[List[str]]

    page_contents: NotRequired[Dict[str, str]]
    known_info: NotRequired[List[str]]
    exploration_results: NotRequired[str]
    final_report: NotRequired[str]

    round_count: NotRequired[int]
    max_rounds: NotRequired[int]
    total_tokens_used:  Annotated[int, add]
    max_tokens: NotRequired[int]
    num_google_searches: NotRequired[int]
    max_google_searches: NotRequired[int]
    num_page_fetches: NotRequired[int]
    max_page_fetches: NotRequired[int]


# Factory function to initialize default values
def create_default_state(
    name: str,
    birthday: str,
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
        "name": name,
        "birthday": birthday,
        "seller_profile": seller_profile,
        "business_info": business_info if business_info else {},
        "report_draft": "",
        "scratchpad": "",
        "research_questions": [],
        "queries_contexts": [],
        "selected_results": [],
        "page_contents": {},
        "known_info": [],
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