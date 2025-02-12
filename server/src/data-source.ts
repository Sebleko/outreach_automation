import "reflect-metadata";
import { DataSource } from "typeorm";
import { Business } from "./entity/Business";
import { BusinessPathEntity } from "./entity/BusinessPath";
import { OutreachEmail } from "./entity/OutreachEmail";
import { Flow } from "./entity/Flow";

export const AppDataSource = new DataSource({
  type: "postgres",
  host: "localhost",
  port: 5432,
  username: "myuser",
  password: "mypass",
  database: "business_outreach",
  synchronize: true,
  logging: false,
  entities: [Business, BusinessPathEntity, OutreachEmail, Flow],
  subscribers: [],
  migrations: [],
});
