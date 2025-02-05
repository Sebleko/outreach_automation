import { AppDataSource } from "../data-source";
import { Business } from "../entity/Business";
import { BusinessFlowMapping } from "../entity/BusinessFlowMapping";
import { Flow } from "../entity/Flow";
import { Task, TaskScheduler } from "../utils/task_scheduling";
import * as ScrapingService from "./scrapingService";

enum Priority {
  Initial = 1,
  ReportApproved = 2,
  OutreachApproved = 3,
}

export const getFlows = async () => {
  const flowRepo = AppDataSource.getRepository(Flow);
  return await flowRepo.find();
};

export const createFlow = async (
  name: string,
  filters: any,
  outreachTemplate: any
) => {
  const flowRepo = AppDataSource.getRepository(Flow);

  const newFlow = flowRepo.create({
    name,
    filters,
    outreachTemplate,
  });

  const id = (await flowRepo.save(newFlow)).id;
  console.log("Created new search flow:", newFlow, id);

  await ScrapingService.scrapeBusinesses(id);
  console.log("ScrapingService done");

  // Next, trigger the processing of the first job.
  // First let us not concider the orchestration of the jobs
  // Just process the first business fully in one swoop.
  const taskScheduler = new TaskScheduler();

  // Create tasks for each business in the flow.
  const businessFlowMappings = await AppDataSource.getRepository(
    BusinessFlowMapping
  ).find({
    where: { flow: { id } },
    relations: ["business"],
  });

  for (const mapping of businessFlowMappings) {
    const business = mapping.business;

    const task = new Task(mapping.id.toString(), Priority.Initial, async () => {
      console.log(`Processing Business ${business.id}`);
      // Do the processing here
      console.log(`Business ${business.id} processed!`);
    });

    taskScheduler.addTask(task);
  }

  return newFlow;
};
