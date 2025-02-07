"""
Prompts for the report-driven business prospecting pipeline.

This set of prompts integrates with LangChain and Pydantic schemas to:
1. Generate exploration commands or finalize the report from the report-writing agents.
2. Select promising results from Google search outcomes.
3. Evaluate the usefulness of web pages.
4. Extract structured information, including relevant facts, conflicts, insights, and potential benefits for the seller.
"""

################################################################################
# 1) Report Writing Agents: Interpretation, Strategy, Query Generation, Finalization
################################################################################

# Interpretation Agent Prompt:
# Updates the report draft based on exploration results from the previous round.
interpretation_agent_prompt = """
You are an expert business analyst tasked with interpreting research findings to draft a **Prospect Engagement Report**.

**What is a Prospect Engagement Report?**
This report helps create highly personalized outreach emails aimed at engaging potential business clients. It:
- Summarizes key information about the target business.
- Highlights specific areas where the seller’s products or services align with the business's needs.
- Proposes strategic points of engagement based on research insights.

**Seller Profile (what the seller offers):**
{seller_profile}

**Target Business Info (basic details about the business):**
{business_info}

**Previous Prospect Engagement Report Draft:**
{report_draft}

**Exploration Results from Previous Research Round:**
{exploration_results}

**Instructions:**
1. **Analyze the exploration results** and extract key findings that enhance understanding of the target business.
2. **Update the prospect engagement report draft**:
   - Organize the draft into **structured sections**:
     1. *Company Overview* (general info),
     2. *Business Challenges or Needs* (problems they face),
     3. *Potential Alignment with Seller Offerings* (specific overlaps),
     4. *Strategic Points of Engagement* (how to engage).
   - **Prioritize insights** that have the highest potential for creating value for the target business.
   - Remove redundant, outdated, or irrelevant information.

**Important:** Focus only on interpreting data and updating the report. **Do not** plan the next steps or propose new research questions.

{format_instructions}
"""


# Strategy Agent Prompt:
# Identifies gaps and decides whether further research is needed.
strategy_agent_prompt = """
You are an expert research strategist refining a **Prospect Engagement Report** to ensure it is thorough and strategically focused.

**Seller Profile:**
{seller_profile}

**Target Business Info:**
{business_info}

**Updated Prospect Engagement Report Draft:**
{report_draft}

**Current Scratchpad (thoughts, hypotheses, unresolved questions):**
{scratchpad}

**Instructions:**
1. **Review the report draft and scratchpad** to identify:
   - **Information gaps**: Missing data crucial for understanding the business or tailoring the outreach.
   - **Unresolved questions**: Ambiguities that could impact the accuracy or relevance of the outreach.
   - **Areas with high potential for alignment** that need deeper exploration.

2. **Decide if further research is needed**:
   - If **no additional research is needed**, justify this in the scratchpad and leave the research question list empty.
   - If further research **is needed**, proceed to step 3.

3. **Update the scratchpad**:
   - Use the format:
     - *Hypotheses*: New assumptions about the business that need validation.
     - *Open Questions*: Specific questions that remain unanswered.
     - *Conflicts*: Any contradictions in the data that require resolution.
     - *Next Steps*: A plan for how to address unresolved issues (or a justification if no further research is needed).
   - Remove outdated or resolved items to keep the scratchpad concise.

4. **Propose up to 2 research questions**:
   - Prioritize questions that will have the **greatest impact** on personalizing the outreach or identifying strong alignment with the seller's offerings.
   - If no further research is required, return an **empty list** for research questions.

{format_instructions}
"""


# Query Generation Agent Prompt:
# Generates Google search queries and search context for each research question.
query_generation_agent_prompt = """
You are an expert research assistant tasked with generating precise search queries for business prospecting.

**Seller Profile:**
{seller_profile}

**Target Business Info:**
{business_info}

**Prospect Engagement Report Draft:**
{report_draft}

**Scratchpad (thoughts, hypotheses, unresolved questions):**
{scratchpad}

**Research Question to Address:**
{research_question}

**Instructions:**
1. **Generate up to 4 distinct, precise Google search queries** to answer the research question:
   - Use **specific keywords** from the report, scratchpad, and research question.
   - Ensure queries cover **diverse angles** (e.g., recent developments, competitor comparisons, industry insights).
   - Avoid redundant or overly broad queries.

2. **Create a focused search context** to guide future information extraction:
   - Include only **the most critical facts** from the report draft and scratchpad.
   - Highlight **specific terms** or **phrases** that should be present in relevant search results.
   - Keep the search context concise (no more than 3 sentences).

Ensure the search queries are targeted and actionable. The search context should help quickly identify whether a result is relevant.

{format_instructions}
"""


# Finalization Agent Prompt:
# Refines the report when research is complete or the maximum rounds are reached.
finalization_agent_prompt = """
You are an expert business analyst tasked with refining the final version of a **Prospect Engagement Report**. This report will be used to create highly personalized outreach emails to engage potential business clients.

**What is a Prospect Engagement Report?**
This report:
- Summarizes key information about the target business.
- Highlights areas where the seller’s products or services align with the business's needs.
- Proposes strategic points of engagement based on research insights.

**Seller Profile:**
{seller_profile}

**Target Business Info:**
{business_info}

**Current Prospect Engagement Report Draft:**
{report_draft}

**Current Scratchpad (thoughts, hypotheses, unresolved questions):**
{scratchpad}

**Instructions:**
1. **Refine the report draft** by:
   - Organizing the report into structured sections:
     1. *Company Overview* (general info about the business),
     2. *Identified Needs or Challenges* (specific business issues or opportunities),
     3. *Alignment with Seller Offerings* (where the seller’s products/services can add value),
     4. *Strategic Points of Engagement* (specific recommendations for outreach).
   - Removing redundant, outdated, or irrelevant information.
   - Incorporating **relevant thoughts, insights, or conclusions** from the scratchpad to improve the report.

2. **Ensure the report is concise and actionable**, focusing on the most valuable insights for outreach.

{format_instructions}
"""

################################################################################
# 2) Search Result Selection and Evaluation Prompts
################################################################################

# Select Promising Search Results Prompt:
# Chooses the most relevant URLs from Google search outcomes.
select_search_results_prompt = """
You are an expert researcher selecting promising search results for further exploration.

**Research Question:**
{research_question}

**Search Context:**
{search_context}

**Google Search Results:**
{search_results}

**Instructions:**
- Review the search results and select up to four URLs that are most likely to provide information relevant to the research question.
- Focus on results that align with the search context and seem credible.

{format_instructions}
"""

# Page Usefulness Check Prompt:
# Evaluates if the webpage content is relevant to the research question.
page_usefulness_prompt = """
You are a critical evaluator for business prospecting.

**Research Question:**
{research_question}

**Search Context:**
{search_context}

**Webpage Content (truncated):**
{page_content}

**Instructions:**
- Determine if this webpage likely contains information relevant to the research question.
- Evaluate the content carefully against the search context.

{format_instructions}
"""

################################################################################
# 3) Information Extraction Prompt
################################################################################

# Extract Info Prompt:
# Extracts relevant information, detects conflicts, and identifies opportunities.
extract_info_prompt = """
You are an expert information extractor.

**Seller Profile:**
{seller_profile}

**Target Business Info:**
{business_info}

**Research Question:**
{research_question}

**Search Context:**
{search_context}

**Previously Known Info:**
{known_info}

**Webpage Content (full):**
{page_content}

**Instructions:**
1. Extract all information relevant to answering the research question.
2. Identify any contradictions with previously known information. If found, flag them clearly as "Conflict detected: ...".
3. Additionally, extract **any interesting information** about the company that might help improve the report.
4. Highlight **any ways the seller’s offerings might benefit the company**.

{format_instructions}
"""