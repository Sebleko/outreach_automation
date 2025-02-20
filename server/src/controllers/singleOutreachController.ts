// singleOutreachController.ts
import { Request, Response } from "express";
import {
  submitOutreachTask,
  pollOutreachTask,
  getOutreachResult,
  handleTaskCompleted,
} from "../services/singleOutreachService";

/**
 * POST /api/single-outreach
 * Submit the initial outreach request, return the newly created taskId.
 */
export const handleSingleOutreachSubmit = async (
  req: Request,
  res: Response
) => {
  try {
    const { sellerProfile, website } = req.body;

    if (!sellerProfile || !website) {
      res.status(400).json({ message: "Missing sellerProfile or website" });
      return;
    }

    const taskId = await submitOutreachTask(sellerProfile, website);
    if (!taskId) {
      res
        .status(500)
        .json({ message: "Could not create a new outreach task." });
      return;
    }

    res.json({ taskId });
    return;
  } catch (error: any) {
    console.error("Error in handleSingleOutreachSubmit:", error);

    res.status(500).json({ message: error.message });
    return;
  }
};

/**
 * GET /api/single-outreach/status/:task_id
 * Poll the status of a given task.
 */
export const handleSingleOutreachPoll = async (req: Request, res: Response) => {
  try {
    const { task_id } = req.params;
    if (!task_id) {
      res.status(400).json({ message: "Missing task_id" });
      return;
    }

    const status = pollOutreachTask(task_id);
    res.json(status);
  } catch (error: any) {
    console.error("Error in handleSingleOutreachPoll:", error);
    res.status(500).json({ message: error.message });
  }
};

/**
 * GET /api/single-outreach/:task_id
 * Retrieve the final email (if completed).
 */
export const handleSingleOutreachGetResult = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const { task_id } = req.params;
    if (!task_id) {
      res.status(400).json({ message: "Missing task_id" });
      return;
    }

    const email = getOutreachResult(task_id);
    res.json({ email });
  } catch (error: any) {
    console.error("Error in handleSingleOutreachGetResult:", error);
    res.status(500).json({ message: error.message });
  }
};

/**
 * POST /api/callback
 * The microservice calls this URL when the task is done or fails.
 */
export const handleMicroserviceCallback = async (
  req: Request,
  res: Response
) => {
  const { task_id, status, result, message } = req.body;

  try {
    // Update our in-memory store
    handleTaskCompleted(task_id, status, result, message);

    // Respond to the microservice that we received the callback
    res.status(200).json({ received: true });
  } catch (error) {
    console.error("Error processing callback:", error);
    // Even if there's an error, let the microservice know we got it
    res.status(200).json({ received: true });
  }
};
