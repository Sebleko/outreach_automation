import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { Business } from "../entity/Business";

export const getAllBusinesses = async (req: Request, res: Response) => {
  try {
    const businessRepo = AppDataSource.getRepository(Business);
    const businesses = await businessRepo.find();
    res.json(businesses);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getBusinessById = async (req: Request, res: Response) => {
  try {
    const businessRepo = AppDataSource.getRepository(Business);
    const business = await businessRepo.findOneBy({
      id: Number(req.params.id),
    });
    if (!business) {
      res.status(404).json({ error: "Business not found" });
      return;
    }
    res.json(business);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const createBusiness = async (req: Request, res: Response) => {
  try {
    const {
      name,
      category,
      website,
      email,
      phone,
      address,
      rating,
      review_count,
    } = req.body;

    const businessRepo = AppDataSource.getRepository(Business);
    const newBusiness = businessRepo.create({
      name,
      category,
      website,
      email,
      phone,
      address,
      rating,
      review_count,
    });
    await businessRepo.save(newBusiness);

    res.status(201).json(newBusiness);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
