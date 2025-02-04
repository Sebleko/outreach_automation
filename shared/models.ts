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
