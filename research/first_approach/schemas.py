# schemas.py

from typing import List, Optional
from pydantic import BaseModel, Field

################################################################################
# 1) Interpretation Agent Schema
################################################################################

class InterpretationOutput(BaseModel):
    report_draft: str = Field(
        description="The updated prospect engagement report draft, incorporating the latest exploration results. "
                    "It should be organized into structured sections such as Company Overview, Business Challenges, "
                    "Alignment with Seller Offerings, and Strategic Points of Engagement."
    )


################################################################################
# 2) Strategy Agent Schema
################################################################################

class PlannerOutput(BaseModel):
    scratchpad: str = Field(
        description="Updated scratchpad containing hypotheses, unresolved questions, conflicts, and next steps. "
                    "If no further research is needed, the scratchpad should justify this decision."
    )
    research_questions: List[str] = Field(
        description="A list of up to 2 research questions to guide further exploration. "
                    "If no additional research is needed, this list will be empty.",
        max_length=2,
    )


################################################################################
# 3) Query Generation Agent Schema
################################################################################

class QueryGenerationOutput(BaseModel):
    search_queries: List[str] = Field(
        description="A list of up to 2 distinct queries to address the research question. "
                    "Queries can be either:\n"
                    "- **Google Search Queries**: Phrases or keywords for Google search.\n"
                    "- **Direct URLs**: Full URLs (starting with 'http') if browsing a specific website is necessary.",
        max_length=2,
    )
    search_context: str = Field(
        description="A concise context derived from the report draft and scratchpad, guiding the evaluation of search results. "
                    "It should include the most critical facts and highlight specific terms relevant to the research question."
    )


################################################################################
# 4) Select Promising Search Results Agent Schema
################################################################################

class SelectedSearchResults(BaseModel):
    selected_results: List[str] = Field(
        description="A list of up to 2 URLs selected from Google search results that are most likely to provide relevant information for answering the research question.",
        max_length=2,
    )


################################################################################
# 5) Page Usefulness Check Agent Schema
################################################################################

class PageUsefulness(BaseModel):
    useful: bool = Field(
        description="Indicates whether the content of the webpage is useful for answering the research question. "
                    "True if useful, False otherwise."
    )


################################################################################
# 6) Extract Info Agent Schema
################################################################################

class ExtractedInfo(BaseModel):
    relevant_info: List[str] = Field(
        description="A list of information extracted from the webpage that is directly relevant to answering the research question."
    )
    conflicts: Optional[List[str]] = Field(
        default=[],
        description="List of contradictions or conflicts detected with previously known information. "
                    "Conflicts should be clearly flagged and explained."
    )
    interesting_insights: Optional[List[str]] = Field(
        default=[],
        description="Any additional interesting information about the company that could enhance the prospect engagement report."
    )
    seller_benefit_possibilities: Optional[List[str]] = Field(
        default=[],
        description="Specific ways the seller’s offerings could benefit the target company based on the extracted information."
    )


################################################################################
# 7) Finalization Agent Schema
################################################################################

class FinalReportOutput(BaseModel):
    final_report: str = Field(
        description="The final, refined version of the prospect engagement report. "
                    "It should be structured, concise, and actionable, focusing on the most valuable insights for outreach."
    )