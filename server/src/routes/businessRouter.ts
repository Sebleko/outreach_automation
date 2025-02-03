import { Router } from "express";
import * as businessController from "../controllers/businessController";

const router = Router();

/**
 * GET /api/businesses
 * Return all businesses
 */
router.get("/", businessController.getAllBusinesses);

/**
 * GET /api/businesses/:id
 * Return details about a single business
 */
router.get("/:id", businessController.getBusinessById);

/**
 * POST /api/businesses
 * Create / Insert new businesses
 */
router.post("/", businessController.createBusiness);

export default router;
