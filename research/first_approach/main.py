import uuid
import traceback
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
import requests

# Import your LangGraph workflow code
from research_graph import create_research_graph

# Pre-compile the workflow at startup
graph = create_research_graph()
workflow = graph.compile()

app = FastAPI()

# Simple in-memory storage for tasks (not persistent!)
TASKS: Dict[str, str] = {}

class TaskRequest(BaseModel):
    # You can adjust fields as needed
    callback_url: str
    seller_profile: str = "We offer AI-driven marketing automation solutions."
    business_info: dict = {
        "business_name": "Acme Corp",
        "website": "https://www.acmecorp.com"
    }
    report_draft: str = ""
    scratchpad: str = ""
    max_rounds: int = 1

@app.post("/submit-task")
async def submit_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Submits a task to run the LangGraph workflow in the background.
    Returns a task_id immediately.
    """
    task_id = str(uuid.uuid4())
    TASKS[task_id] = "pending"

    # Prepare initial state for the workflow
    initial_state = {
        "seller_profile": request.seller_profile,
        "business_info": request.business_info,
        "report_draft": request.report_draft,
        "scratchpad": request.scratchpad,
        "log_steps": True,
        "max_rounds": request.max_rounds,
        "round_count": 0,
    }

    # Add a background task to run the workflow
    background_tasks.add_task(run_workflow, task_id, request.callback_url, initial_state)
    
    return {"task_id": task_id, "status": "accepted"}

async def run_workflow(task_id: str, callback_url: str, state: dict):
    """
    Background task that runs the LangGraph workflow and then sends the result
    or an error to the callback URL.
    """
    try:
        TASKS[task_id] = "running"

        # Actually run the workflow
        final_state = await workflow.ainvoke(state)
        final_report = final_state.get("final_report")

        TASKS[task_id] = "completed"

        # Send final result to the callback
        requests.post(callback_url, json={
            "task_id": task_id,
            "status": "completed",
            "result": {"final_report": final_report}
        })
    except Exception as e:
        TASKS[task_id] = "error"
        error_message = f"{type(e).__name__}: {str(e)}\nTraceback: {traceback.format_exc()}"

        # Send error details to callback
        requests.post(callback_url, json={
            "task_id": task_id,
            "status": "error",
            "message": error_message
        })