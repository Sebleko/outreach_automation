export enum PathStatus {
  Pending = "Pending", // Ready but not started
  ExplorationInProgress = "ExplorationInProgress", // Actively exploring the prospect
  AwaitingReportApproval = "AwaitingReportApproval", // Report is generated, pending review
  ReportApproved = "ReportApproved", // Report reviewed and accepted
  OutreachGenerationInProgress = "OutreachGenerationInProgress", // Drafting outreach
  AwaitingOutreachApproval = "AwaitingOutreachApproval", // Outreach draft pending review
  OutreachApproved = "OutreachApproved", // Outreach approved and ready to send
  Sent = "Sent", // Outreach sent successfully
  Done = "Done", // Entire process completed
  Failed = "Failed", // General failure state for retries/debugging
  Paused = "Paused", // Manually paused by user/admin
}

export enum FlowStatus {
  InProgress = "InProgress",
  Paused = "Paused",
  Done = "Done",
}

export interface BusinessPath {
  id: number;
  business: {
    id: number;
    name: string;
    website: string;
  };
  status: PathStatus;
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
