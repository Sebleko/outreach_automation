import { Router, Request, Response } from "express";
import handleTaskCompleted from "../controllers/callbackController";

const router = Router();

router.post("/task-completed", handleTaskCompleted);

export default router;
