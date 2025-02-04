import { Request, Response } from "express";
import * as FlowService from "../services/flowService";
import { AppDataSource } from "../data-source";
import { Flow } from "../entity/Flow";
import { BusinessFlowMapping } from "../entity/BusinessFlowMapping";
import { BusinessFlow } from "../../../shared/models";

export const getAllFlows = async (req: Request, res: Response) => {
  try {
    const flowRepo = AppDataSource.getRepository(Flow);
    const flows = await flowRepo.find();
    res.json(flows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const createFlow = async (req: Request, res: Response) => {
  try {
    const { name, filters, outreachTemplate } = req.body;
    const newFlow = await FlowService.createFlow(
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

export const getBusinessFlows = async (req: Request, res: Response) => {
  try {
    const { id } = req.params; // Flow ID in the URL
    const flowId = parseInt(id, 10);

    // 1. Fetch all rows in BusinessFlowMapping with this Flow ID.
    //    We use the "relations" property so TypeORM also retrieves the "business" entity.
    const mappingRepo = AppDataSource.getRepository(BusinessFlowMapping);
    const mappings = await mappingRepo.find({
      where: {
        flow: { id: flowId }, // Using the ManyToOne relation
      },
      relations: ["business"], // Eager-load the linked Business
    });

    // 2. Extract just the Business entities from those mappings
    const businessFlows = mappings.map(
      (m) =>
        ({
          id: m.id,
          business: {
            id: m.business.id,
            name: m.business.name,
            website: m.business.website,
          },
          status: m.status,
          last_contacted: m.last_contacted?.toString(),
          response_status: m.response_status,
        } as BusinessFlow)
    );

    // 3. Return the businesses
    res.json(businessFlows);
  } catch (error) {
    console.error("getBusinessesInFlow error:", error);
    res.status(500).json({ error: error.message });
  }
};

export const getFlowById = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const flowRepo = AppDataSource.getRepository(Flow);
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
