import { Entity, PrimaryGeneratedColumn, Column } from "typeorm";

@Entity()
export class Business {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column({ nullable: true })
  category: string;

  @Column({ nullable: true })
  website: string;

  @Column({ nullable: true })
  email: string;

  @Column({ nullable: true })
  phone: string;

  @Column({ nullable: true })
  address: string;

  @Column("float", { nullable: true })
  rating: number;

  @Column("int", { nullable: true })
  review_count: number;

  // Processing status in the main pipeline (optional if using mapping table for status)
  @Column({ nullable: true })
  status: string;
}
