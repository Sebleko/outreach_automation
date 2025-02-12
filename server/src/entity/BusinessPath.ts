import { Entity, PrimaryGeneratedColumn, ManyToOne, Column } from "typeorm";
import { Business } from "./Business";
import { Flow } from "./Flow";
import { PathStatus } from "../../../shared/models";

@Entity()
export class BusinessPathEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => Business)
  business: Business;

  @ManyToOne(() => Flow)
  flow: Flow;

  @Column({ nullable: true })
  report: string;

  @Column("boolean", { default: false })
  report_approved: boolean = false;

  @Column({ nullable: true })
  outreach_mail: string;

  @Column("boolean", { default: false })
  outreach_mail_approved: boolean = false;

  @Column({ nullable: true })
  status: PathStatus;

  @Column({ type: "timestamp", nullable: true })
  last_contacted: Date;

  // e.g. (no_response, interested, not_interested)
  @Column({ nullable: true })
  response_status: string;
}
