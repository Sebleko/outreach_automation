"""
This file constructs the langgraph StateGraph for the research flow.
It wires together the interpretation, strategy, query generation, search selection,
information extraction, and finalization agents, including iterative loops.
"""

from langgraph.graph import StateGraph
from state import AgentGraphState

from agents import (
    InterpretationAgent,
    StrategyAgent,
    QueryGenerationAgent,
    SelectSearchResultsAgent,
    FetchPageAgent,
    ExtractInfoAgent,
    FinalizationAgent
)

def create_research_graph():
    graph = StateGraph(AgentGraphState)

    # Step 1: Interpret exploration results and update report
    graph.add_node("interpretation", lambda state: InterpretationAgent(state).invoke())

    # Step 2: Analyze the report and determine if further research is needed
    graph.add_node("strategy", lambda state: StrategyAgent(state).invoke())

    # Step 3: Generate search queries if further research is needed
    graph.add_node("query_generation", lambda state: QueryGenerationAgent(state).invoke())

    # Step 4: Perform search and select promising results
    graph.add_node("select_search_results", lambda state: SelectSearchResultsAgent(state).invoke())

    # Step 5: Fetch webpage content
    graph.add_node("fetch_page", lambda state: FetchPageAgent(state).invoke())

    # Step 6: Extract relevant information
    graph.add_node("extract_info", lambda state: ExtractInfoAgent(state).invoke())

    # Step 7: Finalize the report
    graph.add_node("finalization", lambda state: FinalizationAgent(state).invoke())

    ############################
    # Define the transitions (flow)
    ############################

    # Start with interpretation
    graph.set_entry_point("interpretation")

    # Move from interpretation to strategy
    graph.add_edge("interpretation", "strategy")

    # Based on strategy, decide whether to continue research or finalize the report
    def research_decision(state):
        if state.get("research_questions"):
            return "query_generation"
        else:
            return "finalization"

    graph.add_conditional_edges("strategy", research_decision)

    # Continue research: Generate queries, select results, fetch pages, extract info, and loop back to interpretation
    graph.add_edge("query_generation", "select_search_results")
    graph.add_edge("select_search_results", "fetch_page")
    graph.add_edge("fetch_page", "extract_info")
    graph.add_edge("extract_info", "interpretation")

    # Finalize the report when research is complete
    graph.add_edge("finalization", "end")
    graph.set_finish_point("end")

    return graph


def compile_workflow():
    graph = create_research_graph()
    return graph.compile()


if __name__ == "__main__":
    # Example workflow execution
    workflow = compile_workflow()

    initial_state = {
        "seller_profile": "We offer AI-driven marketing automation solutions.",
        "business_info": {"business_name": "Acme Corp", "website": "https://www.acmecorp.com"},
        "report_draft": "",
        "scratchpad": "",
        "known_info": []
    }

    final_state = workflow.run(initial_state)
    print("Workflow complete. Final report:", final_state.get("final_report"))