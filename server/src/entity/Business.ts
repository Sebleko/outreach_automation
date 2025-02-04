// src/entity/Business.ts
import { Entity, PrimaryGeneratedColumn, Column } from "typeorm";

@Entity()
export class Business {
  @PrimaryGeneratedColumn()
  id: number;

  // We'll map "title" in CSV => this "name" field
  @Column()
  name: string;

  @Column({ nullable: true })
  category: string;

  @Column({ nullable: true })
  address: string;

  @Column({ nullable: true })
  phone: string;

  @Column({ nullable: true })
  website: string;

  // We'll store just the first email or raw string of emails
  @Column({ nullable: true })
  email: string;

  @Column("float", { nullable: true })
  rating: number;

  @Column("int", { nullable: true })
  review_count: number;
}
