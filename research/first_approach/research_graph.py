# research_graph.py

"""
This file constructs the langgraph StateGraph for the research flow. It wires the Agents
together with the transitions, including the iterative loop for continuing research.
"""

from langgraph.graph import StateGraph
from state import AgentGraphState  # or however you define your custom state class

# Import all the agents
from agents import (
    GenerateSearchQueriesAgent,
    SearchAgent,
    FetchPageAgent,
    UsefulnessAgent,
    ExtractContextAgent,
    CheckIfMoreSearchNeededAgent,
    FinalReportAgent,
    EndNodeAgent
)

def create_research_graph():
    graph = StateGraph(AgentGraphState)

    # Node: GenerateSearchQueries
    graph.add_node(
        "generate_search_queries",
        lambda state: GenerateSearchQueriesAgent(state).invoke()
    )

    # Node: Search
    graph.add_node(
        "search",
        lambda state: SearchAgent(state).invoke()
    )

    # Node: FetchPage
    graph.add_node(
        "fetch_page",
        lambda state: FetchPageAgent(state).invoke()
    )

    # Node: Usefulness
    graph.add_node(
        "usefulness",
        lambda state: UsefulnessAgent(state).invoke()
    )

    # Node: ExtractContext
    graph.add_node(
        "extract_context",
        lambda state: ExtractContextAgent(state).invoke()
    )

    # Node: CheckIfMoreSearchNeeded
    graph.add_node(
        "check_if_more",
        lambda state: CheckIfMoreSearchNeededAgent(state).invoke()
    )

    # Node: FinalReport
    graph.add_node(
        "final_report",
        lambda state: FinalReportAgent(state).invoke()
    )

    # Node: End
    graph.add_node(
        "end",
        lambda state: EndNodeAgent(state).invoke()
    )

    ############################
    # Define the edges (flow)
    ############################

    # 1) Start with generate_search_queries
    graph.set_entry_point("generate_search_queries")

    # 2) Then search -> fetch -> usefulness -> extract -> check_if_more
    graph.add_edge("generate_search_queries", "search")
    graph.add_edge("search", "fetch_page")
    graph.add_edge("fetch_page", "usefulness")
    graph.add_edge("usefulness", "extract_context")
    graph.add_edge("extract_context", "check_if_more")

    # 3) Next step depends on whether we continue research
    def continue_research_condition(state):
        # If "continue_research" is True, go back to "search"
        # else go to "final_report"
        if state.get("continue_research", False):
            return "search"
        else:
            return "final_report"

    graph.add_conditional_edges("check_if_more", continue_research_condition)

    # 4) Once final_report is done, go to end
    graph.add_edge("final_report", "end")
    graph.set_finish_point("end")

    return graph


def compile_workflow():
    graph = create_research_graph()
    return graph.compile()


if __name__ == "__main__":
    # Example usage:
    workflow = compile_workflow()

    # Provide an initial state with the user query:
    initial_state = {
        "user_query": "What are the latest breakthroughs in quantum computing?",
        "aggregated_contexts": [],
        "all_search_queries": []
    }

    final_state = workflow.run(initial_state)
    print("Workflow complete. Final report:", final_state.get("final_report"))