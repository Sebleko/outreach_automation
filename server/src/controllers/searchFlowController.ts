import { Request, Response } from "express";
import * as searchFlowService from "../services/flowService";
import { AppDataSource } from "../data-source";
import { SearchFlow } from "../entity/SearchFlow";

export const getAllSearchFlows = async (req: Request, res: Response) => {
  try {
    const flowRepo = AppDataSource.getRepository(SearchFlow);
    const flows = await flowRepo.find();
    res.json(flows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const createSearchFlow = async (req: Request, res: Response) => {
  try {
    const { name, filters, outreachTemplate } = req.body;
    const newFlow = await searchFlowService.createSearchFlow(
      name,
      filters,
      outreachTemplate
    );
    console.log("Created new search flow:", newFlow);
    res.status(201).json(newFlow);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getSearchFlowById = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const flowRepo = AppDataSource.getRepository(SearchFlow);
    const flow = await flowRepo.findOneBy({ id: Number(id) });

    if (flow) {
      res.json(flow);
    } else {
      res.status(404).json({ error: "Search flow not found" });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
