import { Request, Response } from "express";

interface TaskCallback {
  task_id: string;
  status: "completed" | "error";
  result?: {
    final_report: any;
  };
  message?: string;
}

export const handleTaskCompleted = async (req: Request, res: Response) => {
  const { task_id, status, result, message } = req.body as TaskCallback;

  try {
    switch (status) {
      case "completed":
        console.log(`Task ${task_id} completed successfully.`);
        console.log("Final Report:", result?.final_report);
        break;

      case "error":
        console.error(`Task ${task_id} failed!`);
        console.error("Error details:", message);
        break;

      default:
        console.warn(`Task ${task_id} has unknown status: ${status}`);
    }

    res.status(200).json({ received: true });
  } catch (error) {
    console.error("Error processing callback:", error);
    res.status(200).json({ received: true });
  }
};

export default handleTaskCompleted;
