import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { Business } from "../entity/Business";
import { Business as SharedBusiness } from "../../../shared/models";

export const getAllBusinesses = async (req: Request, res: Response) => {
  try {
    const businessRepo = AppDataSource.getRepository(Business);
    const businesses = await businessRepo.find();

    // Convert to shared model
    const sharedBusinesses = businesses.map((b) => {
      const sharedBusiness: SharedBusiness = {
        id: b.id,
        name: b.name,
        website: b.website,
        category: b.category,
        email: b.email,
        phone: b.phone,
        address: b.address,
        rating: b.rating,
        review_count: b.review_count,
      };
      return sharedBusiness;
    });
    res.json(sharedBusinesses);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getBusinessById = async (req: Request, res: Response) => {
  try {
    console.log("GET /api/businesses/:id", req.params.id);
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
