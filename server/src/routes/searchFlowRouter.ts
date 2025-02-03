import { Router } from "express";
import * as searchFlowController from "../controllers/searchFlowController";

const router = Router();

/**
 * GET /api/search-flows
 * Returns all search flows
 */
router.get("/", searchFlowController.getAllSearchFlows);

/**
 * GET /api/search-flows/:id
 * Returns a single search flow detail
 */
router.get("/:id", searchFlowController.getSearchFlowById);

/**
 * POST /api/search-flows
 * Create a new search flow
 */
router.post("/", searchFlowController.createSearchFlow);

/**
 * (OPTIONAL) Additional routes, e.g.:
 *  - /api/search-flows/:id/businesses  (list businesses in that flow)
 *  - /api/search-flows/:id/scrape      (trigger scraping job)
 */

export default router;
