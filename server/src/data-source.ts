import "reflect-metadata";
import { DataSource } from "typeorm";
import { Business } from "./entity/Business";
import { BusinessFlowMapping } from "./entity/BusinessFlowMapping";
import { OutreachEmail } from "./entity/OutreachEmail";
import { SearchFlow } from "./entity/SearchFlow";

export const AppDataSource = new DataSource({
  type: "postgres",
  host: "localhost",
  port: 5432,
  username: "myuser",
  password: "mypass",
  database: "business_outreach",
  synchronize: true,
  logging: false,
  entities: [Business, BusinessFlowMapping, OutreachEmail, SearchFlow],
  subscribers: [],
  migrations: [],
});
