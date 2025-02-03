import { AppDataSource } from "../data-source";
import { SearchFlow } from "../entity/SearchFlow";
import * as ScrapingService from "./scrapingService";

export const getSearchFlows = async () => {
  const flowRepo = AppDataSource.getRepository(SearchFlow);
  return await flowRepo.find();
};

export const createSearchFlow = async (
  name: string,
  filters: any,
  outreachTemplate: any
) => {
  const flowRepo = AppDataSource.getRepository(SearchFlow);

  const newFlow = flowRepo.create({
    name,
    filters,
    outreachTemplate,
  });

  const id = (await flowRepo.save(newFlow)).id;

  ScrapingService.scrapeBusinesses(id);

  return newFlow;
};
