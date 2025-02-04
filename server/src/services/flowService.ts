import { AppDataSource } from "../data-source";
import { Flow } from "../entity/Flow";
import * as ScrapingService from "./scrapingService";

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

  return newFlow;
};
