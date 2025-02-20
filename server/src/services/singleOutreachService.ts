// singleOutreachService.ts

/**
 * Define the shape of the task data we keep in memory.
 */
interface InMemoryTask {
  taskId: string;
  status: "pending" | "completed" | "error";
  sellerProfile: string;
  website: string;
  finalReport?: string; // The result from the microservice
  message?: string; // Error message if something goes wrong
}

/**
 * Our in-memory store of tasks.
 * Key is the taskId (string).
 */
const tasks: Record<string, InMemoryTask> = {};

/**
 * Submit a new outreach task to our microservice.
 * - Generate a new unique taskId
 * - Create a record in memory with `pending` status
 * - Call the external microservice, providing a callback URL
 * - Return the taskId so the client can poll.
 */
export async function submitOutreachTask(
  sellerProfile: string,
  website: string
): Promise<string> {
  // Create a unique ID for this task

  // Example callback URL. This should be publicly accessible by the microservice.
  // Adjust accordingly for your environment (e.g. https://your-domain.com/api/callback).
  const callbackUrl = `http://localhost:3000/api/single-outreach/callback`;

  // Example call to the external microservice that handles LLM logic
  try {
    const response = await fetch("http://localhost:8000/submit-task", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        seller_profile: sellerProfile,
        website,
        callback_url: callbackUrl,
      }),
    });

    const { task_id } = await response.json();

    // Save an initial record in memory
    tasks[task_id] = {
      taskId: task_id,
      status: "pending",
      sellerProfile,
      website,
    };

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return task_id;
  } catch (error) {
    throw new Error("Error calling external microservice:" + error);
  }
}

/**
 * Check the current status of a task.
 * Return "done" if completed, "error" if error, or "pending" otherwise.
 */
export function pollOutreachTask(taskId: string) {
  const task = tasks[taskId];
  if (!task) {
    throw new Error(`Task with ID ${taskId} not found.`);
  }

  switch (task.status) {
    case "pending":
      return { state: "pending" as const };
    case "completed":
      return { state: "done" as const };
    case "error":
      return {
        state: "error" as const,
        message: task.message || "Unknown error occurred",
      };
    default:
      // Should never happen, but just in case.
      return { state: "error" as const, message: "Invalid task state" };
  }
}

/**
 * Retrieve the final result (the outreach email text) for a completed task.
 */
export function getOutreachResult(taskId: string) {
  const task = tasks[taskId];
  if (!task) {
    throw new Error(`Task with ID ${taskId} not found.`);
  }

  if (task.status !== "completed") {
    throw new Error(
      `Task ${taskId} is not completed yet. Current status: ${task.status}`
    );
  }

  // Return the final report from the microservice
  return task.finalReport || "";
}

/**
 * Handle the callback from the microservice when it finishes the task.
 * The microservice calls us back with the status, final report, etc.
 */
export function handleTaskCompleted(
  taskId: string,
  status: string,
  result?: { final_report?: string },
  message?: string
) {
  // Safeguard if we don't have this task
  if (!tasks[taskId]) {
    console.warn(`Received callback for unknown taskId: ${taskId}`);
    return;
  }

  switch (status) {
    case "completed":
      tasks[taskId].status = "completed";
      tasks[taskId].finalReport = result?.final_report || "";
      break;

    case "error":
      tasks[taskId].status = "error";
      tasks[taskId].message = message || "Task failed for unknown reason.";
      break;

    default:
      console.warn(`Unknown status from microservice: ${status}`);
      break;
  }
}
