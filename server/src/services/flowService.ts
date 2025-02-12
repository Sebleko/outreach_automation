import { AppDataSource } from "../data-source";
import { Business } from "../entity/Business";
import { BusinessPathEntity } from "../entity/BusinessPath";
import { Flow } from "../entity/Flow";
import * as ScrapingService from "./scrapingService";
import { FlowExecutor } from "../utils/FlowExecutor";
import { FlowStatus } from "../../../shared/models";

// In-memory registry of FlowExecutors, keyed by flow id.
const FlowExecutors: Record<string, FlowExecutor> = {};

enum Priority {
  Initial = 1,
  ReportApproved = 2,
  OutreachApproved = 3,
}

/**
 * Returns all existing flows.
 */
export const getFlows = async (): Promise<Flow[]> => {
  const flowRepo = AppDataSource.getRepository(Flow);
  return await flowRepo.find();
};

/**
 * Creates a new flow, kicks off scraping to collect associated businesses,
 * and then initializes a FlowExecutor to load and process all paths for the flow.
 */
export const createFlow = async (
  name: string,
  filters: any,
  outreachTemplate: any
): Promise<Flow> => {
  const flowRepo = AppDataSource.getRepository(Flow);

  const newFlow = flowRepo.create({
    name,
    filters,
    outreachTemplate,
    status: FlowStatus.InProgress,
  });

  const savedFlow = await flowRepo.save(newFlow);

  // Scrape and persist businesses for this flow.
  await ScrapingService.scrapeBusinesses(savedFlow.id);

  // Create and initialize a FlowExecutor for this flow.
  const executor = new FlowExecutor();
  await executor.load(savedFlow.id);
  executor.start();

  // Save the FlowExecutor instance in our registry for later reference.
  FlowExecutors[savedFlow.id.toString()] = executor;

  return savedFlow;
};

/**
 * Approves a pending stage (either "report" or "outreach") for a given path.
 * The function first finds the corresponding BusinessPath (and its flow),
 * then relays the approval to the corresponding FlowExecutor instance.
 */
export const approve = async (
  pathId: string,
  approvalType: "report" | "outreach"
): Promise<void> => {
  // Look up the BusinessPath record by id.
  const mappingRepo = AppDataSource.getRepository(BusinessPathEntity);
  const mapping = await mappingRepo.findOne({
    where: { id: Number(pathId) },
    relations: ["flow"],
  });

  if (!mapping) {
    throw new Error(`No BusinessPath found with id ${pathId}`);
  }

  // Determine the flow id from the mapping.
  const flowId = mapping.flow.id.toString();
  const executor = FlowExecutors[flowId];
  if (!executor) {
    throw new Error(`FlowExecutor not found for flow id ${flowId}`);
  }

  // Relay the approval to the FlowExecutor, which updates the DB and schedules
  // a new task to continue processing the path.
  await executor.approve(pathId, approvalType);
  console.log(`Approved ${approvalType} for path ${pathId} (flow ${flowId})`);
};
