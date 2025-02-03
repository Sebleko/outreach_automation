import { Entity, PrimaryGeneratedColumn, Column, ManyToOne } from "typeorm";
import { Business } from "./Business";

@Entity()
export class OutreachEmail {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => Business)
  business: Business;

  @Column({ type: "text" })
  email_body: string;

  @Column({ type: "timestamp", nullable: true })
  sent_at: Date;

  // e.g. (pending_review, sent, opened, replied)
  @Column({ nullable: true })
  status: string;

  @Column({ type: "timestamp", nullable: true })
  follow_up_due: Date;
}
