import { Router } from "express";
import {
  handleSingleOutreachGetResult,
  handleSingleOutreachSubmit,
  handleSingleOutreachPoll,
  handleMicroserviceCallback,
} from "../controllers/singleOutreachController";

const router = Router();

router.post("/", handleSingleOutreachSubmit);
router.get("/:task_id", handleSingleOutreachGetResult);
router.get("/status/:task_id", handleSingleOutreachPoll);
router.get("/callback", handleMicroserviceCallback);

export default router;
