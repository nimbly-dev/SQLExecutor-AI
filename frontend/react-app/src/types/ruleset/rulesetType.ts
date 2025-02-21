export interface ColumnRule {
  allow: string | string[];
  deny: string[];
}

export interface Criteria {
  matching_criteria: Record<string, any>;
  condition?: string;
}

export interface GlobalAccessPolicy {
  tables: Record<string, TableRule>;
}

export interface GroupAccessColumnRule {
  allow: string[];
  deny: string[];
}

export interface GroupAccessPolicy {
  description: string;
  criteria: Criteria;
  tables: Record<string, GroupAccessTableRule>;
}

export interface GroupAccessTableRule {
  columns: GroupAccessColumnRule;
}

export interface InjectorTableRule {
  filters: string;
}

export interface Injector {
  enabled: boolean;
  condition: string;
  tables: Record<string, InjectorTableRule>;
}

export interface Ruleset {
  _id?: string;
  tenant_id: string;
  ruleset_name: string;
  connected_schema_name: string;
  description: string;
  is_ruleset_enabled: boolean;
  conditions?: Record<string, string>;
  global_access_policy: GlobalAccessPolicy;
  group_access_policy?: Record<string, GroupAccessPolicy>;
  user_specific_access_policy?: UserSpecificAccessPolicy[];
  injectors?: Record<string, Injector>;
}

export interface TableRule {
  columns: ColumnRule;
  condition: string;
}

export interface UserSpecificAccessPolicy {
  user_identifier: string;
  tables: Record<string, UserSpecificTableRule>;
}

export interface UserSpecificTableRule {
  columns: ColumnRule;
}

export interface RulesetSummary {
  ruleset_name: string;
  description: string;
  connected_schema_name: string;
  is_ruleset_enabled: boolean;
  has_injectors: boolean;
}

//---------------------------------------------- Response Types ----------------------------------------------


export interface RulesetResponse {
  rulesets: RulesetSummary[];
  total: number;
  page: number;
  page_size: number;
}


//---------------------------------------------- Request Types ----------------------------------------------

export interface RulesetFilters {
  name?: string;
  filterName?: string;  // Added this field
  isRulesetEnabled?: boolean;
  hasInjectors?: boolean;
  page?: number;
  pageSize?: number;
}

export interface AddUpdateRulesetRequest {
  ruleset_name: string;
  connected_schema_name: string;
  description: string;
  is_ruleset_enabled: boolean;
  conditions?: Record<string, string>;
  global_access_policy: GlobalAccessPolicy;
  group_access_policy?: Record<string, GroupAccessPolicy>;
  user_specific_access_policy?: UserSpecificAccessPolicy[];
  injectors?: Record<string, Injector>;
}