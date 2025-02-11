from langgraph.graph import StateGraph, END, START
from state import ProspectingAgentState
# Import the newly refactored agent functions
from agents import (
    planner_agent,
    interpretation_agent,
    query_generation_agent,
    select_search_results_agent,
    extract_info_agent,
    finalization_agent
)

def create_dummy_graph():
    graph = StateGraph(ProspectingAgentState)
    
    def dummy_fn(name: str):
        def fn(state):
            print("Dummy function called with name:", name)
            return state
        return fn

    graph.add_node("a", dummy_fn("A"))
    graph.add_node("b", dummy_fn("B"))
    graph.add_edge("a", "b")
    graph.add_edge(START, "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", END)

    return graph

def create_research_graph():
    graph = StateGraph(ProspectingAgentState)

    # 1) Add the Planner node (replaces Strategy as the first step)
    graph.add_node("planner", planner_agent)

    # 2) Interpretation node
    graph.add_node("interpretation", interpretation_agent)

    # 3) Standard research steps
    graph.add_node("query_generation", query_generation_agent)
    graph.add_node("select_search_results", select_search_results_agent)
    graph.add_node("extract_info", extract_info_agent)

    # 4) Finalization
    graph.add_node("finalization", finalization_agent)

    # -------------------------
    # Define the edges (flow)
    # -------------------------
    # Start with Planner
    graph.set_entry_point("planner")

    # After Interpretation, conditionally decide next step
    def round_check(state):
        """
        If there are research questions and we haven't reached the max number of rounds,
        continue with planner again. Otherwise, proceed to finalization.
        """
        state["round_count"] += 1
        if state.get("research_questions") and state["round_count"] < state["max_rounds"]:
            return "planner"
        else:
            return "finalization"
        
    def ready_check(state):
        """
        If there are no more research questions, we can proceed to finalization.
        Else we need to continue with query generation.
        """
        research_questions = state.get("research_questions")
        if research_questions and len(research_questions) > 0:
            return "query_generation"
        else:
            return "finalization"

    # Planner -> ready_check -> either query_generation or finalization
    graph.add_conditional_edges("planner", ready_check)

    # Interpretation -> round_check -> either planner or finalization
    graph.add_conditional_edges("interpretation", round_check)

    # Research loop: queries -> select -> extract -> re-interpret
    graph.add_edge("query_generation", "select_search_results")
    graph.add_edge("select_search_results", "extract_info")
    graph.add_edge("extract_info", "interpretation")

    # Finalization
    graph.add_edge("finalization", END)

    # Optional: log node execution if a flag is set in state
    def on_node_start(state, node_name):
        if state.get("log_steps"):
            print(f"[LOG] Running node: {node_name}")

    graph.on_node_start = on_node_start

    return graph

if __name__ == "__main__":
    graph = create_dummy_graph()
    workflow = graph.compile()

    initial_state = {
        "seller_profile": "We offer AI-driven marketing automation solutions.",
        "business_info": {
            "business_name": "Acme Corp",
            "website": "https://www.acmecorp.com"
        },
        "report_draft": "",
        "scratchpad": "",
        "log_steps": True,        # Enable logging of graph steps
        "max_rounds": 3,
        "round_count": 0,
    }

    final_state = workflow.invoke(initial_state)

    # Summarize results
    print("\n--- Workflow Complete ---")
    print("Final report:\n", final_state.get("final_report"))
    print(f"Research rounds completed: {final_state.get('round_count', 0)} / {final_state.get('max_rounds', 0)}")