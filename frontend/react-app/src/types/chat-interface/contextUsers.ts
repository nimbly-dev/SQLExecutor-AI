export interface ExternalContextUserRow {
  context_identifier: string;
  context_type: string;
  custom_fields: Record<string, string>;
  [key: string]: any; 
}

export interface GetUserContextsResponse {
  data: ExternalContextUserRow[];
  total_count: number;
  page: number;
  page_size: number;
}