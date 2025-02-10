from langgraph.graph import StateGraph
from state import ProspectingAgentState
from agents import (
    PlannerAgent,
    InterpretationAgent,
    QueryGenerationAgent,
    SelectSearchResultsAgent,
    ExtractInfoAgent,
    FinalizationAgent
)

def create_research_graph():
    graph = StateGraph(ProspectingAgentState)

    # 1) Add the Planner node (replaces Strategy as the first step)
    graph.add_node("planner", lambda s: PlannerAgent(s).invoke())

    # 2) Interpretation node
    graph.add_node("interpretation", lambda s: InterpretationAgent(s).invoke())

    # 3) Standard research steps
    graph.add_node("query_generation", lambda s: QueryGenerationAgent(s).invoke())
    graph.add_node("select_search_results", lambda s: SelectSearchResultsAgent(s).invoke())
    graph.add_node("extract_info", lambda s: ExtractInfoAgent(s).invoke())

    # 4) Finalization
    graph.add_node("finalization", lambda s: FinalizationAgent(s).invoke())

    # -------------------------
    # Define the edges (flow)
    # -------------------------
    # Start with Planner
    graph.set_entry_point("planner")

    # After Interpretation, conditionally decide next step
    def round_check(state):
        """
        If there are research questions and we haven't reached the max number of rounds,
        continue with query generation. Otherwise, proceed to finalization.
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

    graph.add_conditional_edges("interpretation", round_check)
    graph.add_conditional_edges("planner", ready_check)

    # Research loop: queries -> select -> extract -> re-interpret
    graph.add_edge("query_generation", "select_search_results")
    graph.add_edge("select_search_results", "extract_info")
    # After extracting info, we go back to interpretation and recheck the rounds
    graph.add_edge("extract_info", "interpretation")

    # Finalization when research rounds are complete or no research questions remain
    graph.add_edge("finalization", "end")
    graph.set_finish_point("end")

    # Optional: log node execution if a flag is set in state
    def on_node_start(state, node_name):
        if state.get("log_steps"):
            print(f"[LOG] Running node: {node_name}")

    graph.on_node_start = on_node_start

    return graph

def compile_graph():
    graph = create_research_graph()
    return graph.compile()

if __name__ == "__main__":
    workflow = compile_graph()

    initial_state = {
        "seller_profile": "We offer AI-driven marketing automation solutions.",
        "business_info": {
            "business_name": "Acme Corp",
            "website": "https://www.acmecorp.com"
        },
        "report_draft": "",
        "scratchpad": "",
        "known_info": [],
        "log_steps": True,        # Enable logging of graph steps
        "max_rounds": 3,
        "round_count": 0,
    }

    final_state = workflow.run(initial_state)

    # Summarize results
    print("\n--- Workflow Complete ---")
    print("Final report:\n", final_state.get("final_report"))
    print(f"Research rounds completed: {final_state.get('round_count', 0)} / {final_state.get('max_rounds', 0)}")