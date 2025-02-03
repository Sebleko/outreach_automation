/**
 * scrapingService.ts
 *
 * A dummy service that "scrapes" (reads) business data from a local CSV file,
 * then persists the data into the database using TypeORM, creating
 * a mapping to the given SearchFlow.
 *
 * HOW TO USE:
 *
 *   import { scrapeBusinesses } from "./scrapingService";
 *
 *   async function run() {
 *     await dataSource.initialize();
 *     await scrapeBusinesses(flowId, dataSource, "dummy_data.csv");
 *   }
 */

import { DataSource } from "typeorm";
import { createReadStream } from "fs";
import { join } from "path";
import csvParser from "csv-parser";

import { Business } from "../entity/Business";
import { BusinessFlowMapping } from "../entity/BusinessFlowMapping";
import { SearchFlow } from "../entity/SearchFlow";
import { AppDataSource } from "../data-source";

// --------------------------------------------------
// 1. Define the shape of the data we expect from CSV
// --------------------------------------------------
interface ScrapedBusiness {
  name: string;
  category?: string;
  website?: string;
  email?: string;
  phone?: string;
  address?: string;
  rating?: number;
  review_count?: number;
}

// --------------------------------------------------
// 2. Read data from CSV (placeholder for real scraping)
// --------------------------------------------------
async function readFromCSV(csvFilePath: string): Promise<ScrapedBusiness[]> {
  return new Promise((resolve, reject) => {
    const results: ScrapedBusiness[] = [];

    createReadStream(csvFilePath)
      .pipe(csvParser())
      .on("data", (row: any) => {
        console.log("Read row:", row);
        // Adjust column names to match your CSV structure
        results.push({
          name: row.name,
          category: row.category,
          website: row.website,
          email: row.email,
          phone: row.phone,
          address: row.address,
          rating: parseFloat(row.rating) || undefined,
          review_count: parseInt(row.review_count, 10) || undefined,
        });
      })
      .on("end", () => resolve(results))
      .on("error", (err) => reject(err));
  });
}

// --------------------------------------------------
// 3. Main function to "scrape" businesses for a flow
// --------------------------------------------------
/**
 * Scrapes businesses and links them to the specified flow.
 * - flowId: the ID of the SearchFlow entity
 * - dataSource: an initialized TypeORM DataSource
 * - csvFilePath: path to your dummy CSV file (default "dummy_data.csv")
 *
 * Usage:
 *    await scrapeBusinesses(flow.id, dataSource);
 */
export async function scrapeBusinesses(flowId: number): Promise<void> {
  try {
    // 1. Fetch the SearchFlow (to get any filters, name, etc. if needed)
    const flowRepo = AppDataSource.getRepository(SearchFlow);
    const flow = await flowRepo.findOneBy({ id: flowId });
    if (!flow) {
      throw new Error(`No SearchFlow found with ID ${flowId}`);
    }

    // 2. Read data from CSV (this is our dummy "scraping" source)
    const scrapedData = await readFromCSV(join(__dirname, "dummy_data.csv"));

    // 3. Persist all data + create mappings in a single transaction
    await AppDataSource.transaction(async (manager) => {
      for (const biz of scrapedData) {
        // Create and save the Business
        const business = manager.create(Business, {
          name: biz.name,
          category: biz.category,
          website: biz.website,
          email: biz.email,
          phone: biz.phone,
          address: biz.address,
          rating: biz.rating,
          review_count: biz.review_count,
        });

        await manager.save(business);

        // Create the link (BusinessFlowMapping) between Business & Flow
        const mapping = manager.create(BusinessFlowMapping, {
          business,
          searchFlow: flow,
          status: "pending", // or any default status you'd like
        });

        await manager.save(mapping);
      }
    });

    console.log(
      `Scraping (CSV read) successful for flow #${flowId}. Inserted ${scrapedData.length} businesses.`
    );
  } catch (error) {
    console.error("Error scraping businesses:", error);
    // Throw to signal that the operation failed
    throw error;
  }
}
