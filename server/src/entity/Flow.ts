import { Entity, PrimaryGeneratedColumn, Column } from "typeorm";

@Entity()
export class Flow {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  // Filters stored as JSON (website required, min reviews, etc.)
  @Column({ type: "jsonb", nullable: true })
  filters: any;

  // Default outreach template
  @Column({ type: "text", nullable: true })
  outreachTemplate: string;
}
