import { Entity, PrimaryGeneratedColumn, ManyToOne, Column } from "typeorm";
import { Business } from "./Business";
import { SearchFlow } from "./SearchFlow";

@Entity()
export class BusinessFlowMapping {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => Business)
  business: Business;

  @ManyToOne(() => SearchFlow)
  searchFlow: SearchFlow;

  // e.g. (pending, profiled, outreach_ready, outreach_sent, response_received)
  @Column({ nullable: true })
  status: string;

  @Column({ type: "timestamp", nullable: true })
  last_contacted: Date;

  // e.g. (no_response, interested, not_interested)
  @Column({ nullable: true })
  response_status: string;
}
