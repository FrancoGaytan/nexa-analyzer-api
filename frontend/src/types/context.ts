// Type definitions aligned with backend app.models.context.ClientContext
export interface ClientContext {
  client_name: string | null;
  industry: string | null;
  location: string | null;
  engagement_age: number; // years
  business_overview: string | null;
  objectives: string[];
  company_info: string | null;
  additional_context_questions: string[];
  potential_future_opportunities: string[];
  // The backend may include evidence pointers or notes in future; keep index signature optional
  [key: string]: unknown;
}

export interface AnalyzeResponse {
  analysis_id: string;
  status: string; // "completed" | "error" | other future states
  summary: ClientContext;
  // Backend might send additional keys (e.g., log) later
  [key: string]: unknown;
}
