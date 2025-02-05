export interface BusinessFlow {
  id: number;
  business: {
    id: number;
    name: string;
    website: string;
  };
  status: string;
  last_contacted: string;
  response_status: string;
}

export interface Business {
  id: number;
  name: string;
  website: string;
  category: string;
  email: string;
  phone: string;
  address: string;
  rating: number;
  review_count: number;
}
