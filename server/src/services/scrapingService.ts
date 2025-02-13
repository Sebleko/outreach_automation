/**
 * scrapingService.ts
 *
 * A simpler service that:
 * 1. Reads essential business data from CSV ("title", "category", etc.)
 * 2. Persists to the DB using TypeORM
 * 3. Creates a mapping to the given Flow
 */

import { createReadStream } from "fs";
import { join } from "path";
import csvParser from "csv-parser";

import { Business } from "../entity/Business";
import { BusinessPathEntity } from "../entity/BusinessPath";
import { PathStatus } from "../../../shared/models";
import { Flow } from "../entity/Flow";
import { AppDataSource } from "../data-source";

// --------------------------------------------------
// Define only the essential columns we want
// --------------------------------------------------
interface ScrapedBusiness {
  name: string; // from "title" in CSV
  category?: string;
  address?: string;
  phone?: string;
  website?: string;
  email?: string;
  rating?: number;
  review_count?: number;
}

// --------------------------------------------------
// CSV reading, extracting only essential fields
// --------------------------------------------------
async function readFromCSV(csvFilePath: string): Promise<ScrapedBusiness[]> {
  return new Promise((resolve, reject) => {
    const results: ScrapedBusiness[] = [];

    createReadStream(csvFilePath)
      .pipe(csvParser())
      .on("data", (row: any) => {
        // Log to see the row structure (optional)
        //console.log("Read row:", row);

        // Our CSV uses "title" for the business name
        const name = row.title ?? "Unknown Name";

        // We'll parse rating & review_count safely
        const rating = row.review_rating
          ? parseFloat(row.review_rating)
          : undefined;
        const review_count = row.review_count
          ? parseInt(row.review_count, 10)
          : undefined;

        // If you have multiple emails in 'row.emails', decide how to handle them
        const email = row.emails || ""; // or just store the raw string

        results.push({
          name,
          category: row.category ?? "",
          address: row.address ?? "",
          phone: row.phone ?? "",
          website: row.website ?? "",
          email,
          rating,
          review_count,
        });
      })
      .on("end", () => resolve(results))
      .on("error", (err) => reject(err));
  });
}

// --------------------------------------------------
// Main function: "scrape" businesses for a Flow
// --------------------------------------------------
/**
 * Scrapes businesses and links them to the specified Flow.
 *
 * @param flowId       The ID of the Flow entity
 * @param csvFilePath  Path to your CSV file (default "dummy_data.csv")
 */
export async function scrapeBusinesses(
  flowId: number,
  csvFilePath: string = "dummy_data.csv"
): Promise<void> {
  try {
    // 1. Fetch the Flow from DB
    const flowRepo = AppDataSource.getRepository(Flow);
    const flow = await flowRepo.findOneBy({ id: flowId });
    if (!flow) {
      throw new Error(`No Flow found with ID ${flowId}`);
    }
    console.log("Scraping businesses for flow:", flow);

    // 2. Read data from CSV
    const absolutePath = join(__dirname, csvFilePath);
    const scrapedData = await readFromCSV(absolutePath);

    // 3. Persist data in a transaction
    await AppDataSource.transaction(async (manager) => {
      for (const bizData of scrapedData) {
        //console.log("Inserting business:", bizData);
        // Check that the business does not already exist. Check if websites match. If website is undefined in both fall back to address, then name.
        let business: Business | null = await manager.findOne(Business, {
          where: {
            website: bizData.website,
            address: bizData.address,
            name: bizData.name,
          },
        });
        // If the business does not exist, create it.
        if (!business) {
          // Create a new Business entity
          const b = manager.create(Business, {
            name: bizData.name,
            category: bizData.category,
            address: bizData.address,
            phone: bizData.phone,
            website: bizData.website,
            email: bizData.email,
            rating: bizData.rating,
            review_count: bizData.review_count,
          });

          business = await manager.save(b);
        }
        console.log("Scraped Business:", business);

        // Create the mapping between Business and Flow
        const mapping = manager.create(BusinessPathEntity, {
          business,
          flow, // or "Flow: flow" if your relation is named "Flow" in the entity
          status: PathStatus.Pending,
        });
        console.log("Mapping:", mapping);

        await manager.save(mapping);
      }
    });

    console.log(
      `Scraping successful for flow #${flowId}. Inserted ${scrapedData.length} businesses.`
    );
  } catch (error) {
    console.error("Error scraping businesses:", error);
    throw error;
  }
}
