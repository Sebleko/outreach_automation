import { Entity, PrimaryGeneratedColumn, Column } from "typeorm";
import { FlowStatus } from "../../../shared/models";

@Entity()
export class Flow {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column()
  status: FlowStatus;

  // Filters stored as JSON (website required, min reviews, etc.)
  @Column({ type: "jsonb", nullable: true })
  filters: any;

  // Default outreach template
  @Column({ type: "text", nullable: true })
  outreachTemplate: string;
}
