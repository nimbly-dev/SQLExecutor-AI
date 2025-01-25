export interface ExternalContextUserRow {
  user_identifier: string;
  custom_fields: {
    [key: string]: string;
  };
}

export interface GetUserContextsResponse {
    data: ExternalContextUserRow[];
    page: number;
    limit: number;
    total_count: number;
}