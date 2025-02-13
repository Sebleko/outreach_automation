import { Router } from "express";
import * as FlowController from "../controllers/flowController";

const router = Router();

/**
 * GET /api/flows
 * Returns all search flows
 */
router.get("/", FlowController.getAllFlows);

/**
 * GET /api/flows/:id
 * Returns a single search flow detail
 */
router.get("/:id", FlowController.getFlowById);

/**
 * GET /api/flows/:id/businesses
 * Get all businesses in a flow
 */
router.get("/:id/businesses", FlowController.getBusinessPaths);

/** /api/flows/:flowId/:businessId
 * Control how a business is handled in a flow.
 */

/**
 * POST /api/flows
 * Create a new search flow
 */
router.post("/", FlowController.createFlow);

/**
 * PUT /api/flows/approve/:pathId/:approvalType
 * Approve a report or outreach for a specific path
 */
router.put("/approve/:pathId/:approvalType", FlowController.approvePath);

/**
 * (OPTIONAL) Additional routes, e.g.:
 *  - /api/flows/:id/businesses  (list businesses in that flow)
 *  - /api/flows/:id/scrape      (trigger scraping job)
 */

export default router;
