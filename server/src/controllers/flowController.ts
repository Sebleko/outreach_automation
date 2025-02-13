import { Request, Response } from "express";
import * as FlowService from "../services/flowService";
import { AppDataSource } from "../data-source";
import { Flow } from "../entity/Flow";
import { BusinessPathEntity } from "../entity/BusinessPath";
import { BusinessPath } from "../../../shared/models";

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

export const getBusinessPaths = async (req: Request, res: Response) => {
  try {
    const { id } = req.params; // Flow ID in the URL
    const flowId = parseInt(id, 10);

    // 1. Fetch all rows in BusinessPath with this Flow ID.
    //    We use the "relations" property so TypeORM also retrieves the "business" entity.
    const mappingRepo = AppDataSource.getRepository(BusinessPathEntity);
    const mappings = await mappingRepo.find({
      where: {
        flow: { id: flowId }, // Using the ManyToOne relation
      },
      relations: ["business"], // Eager-load the linked Business
    });
    console.log("Found", mappings.length, "business paths for flow", flowId);
    console.log("First path:", mappings[0]);
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
        } as BusinessPath)
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

export const approvePath = async (req: Request, res: Response) => {
  try {
    const { pathId: id, approvalType } = req.params;
    console.log("Approving path", id, "with type", approvalType);

    if (approvalType !== "report" && approvalType !== "outreach") {
      res.status(400).json({ error: "Invalid approval type" });
      return;
    }

    const pathRepo = AppDataSource.getRepository(BusinessPathEntity);
    const path = await pathRepo.findOneBy({ id: Number(id) });

    console.log("Found path:", path);
    if (!path) {
      res.status(404).json({ error: "Business path not found" });
      return;
    }

    await FlowService.approve(id, approvalType);

    res.json(path);
  } catch (error) {
    console.warn("approvePath error:", error);
    res.status(500).json({ error: error.message });
  }
};
