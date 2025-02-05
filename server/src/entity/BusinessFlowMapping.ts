import { Entity, PrimaryGeneratedColumn, ManyToOne, Column } from "typeorm";
import { Business } from "./Business";
import { Flow } from "./Flow";

// Enum for different statuses.
export enum BusinessFlowStatus {
  READY = "ready",
  REPORT_WAITING_FOR_APPROVAL = "report_waiting_for_approval",
  REPORT_APPROVED = "report_approved",
  OUTREACH_WAITING_FOR_APPROVAL = "outreach_waiting_for_approval",
  OUTREACH_APPROVED = "outreach_approved",
  OUTREACH_SENT = "outreach_sent",
  RESPONSE_RECEIVED = "response_received",
}

@Entity()
export class BusinessFlowMapping {
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

  // e.g. (, profiled, outreach_ready, outreach_sent, response_received)
  @Column({ nullable: true })
  status: BusinessFlowStatus;

  @Column({ type: "timestamp", nullable: true })
  last_contacted: Date;

  // e.g. (no_response, interested, not_interested)
  @Column({ nullable: true })
  response_status: string;
}
