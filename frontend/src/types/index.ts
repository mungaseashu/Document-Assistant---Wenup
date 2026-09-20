export const FieldStatus = {
  UNKNOWN: 'UNKNOWN',
  PROPOSED: 'PROPOSED',
  NEEDS_CONFIRMATION: 'NEEDS_CONFIRMATION',
  CONFIRMED: 'CONFIRMED',
  CORRECTED: 'CORRECTED',
} as const;

export type FieldStatus = typeof FieldStatus[keyof typeof FieldStatus];

export interface StateField<T> {
  value: T | null;
  status: FieldStatus;
  confidence: number;
  source: string | null;
  last_updated: string | null;
  evidence: string | null;
}

export interface PersonalWishesState {
  full_name: StateField<string>;
  home_address: StateField<string>;
  covers_worldwide_assets: StateField<boolean>;
  has_children: StateField<boolean>;
  children_names: StateField<string[]>;
  executor_name: StateField<string>;
  executor_relationship: StateField<string>;
  specific_gifts: StateField<string[]>;
  additional_wishes: StateField<string[]>;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface OrchestrationAPIResponse {
  reply: string;
  document: string;
  state: PersonalWishesState;
  recent_audit?: any[];
  conflicts?: any[];
}

export interface FieldChange {
  field: string;
  proposed_value: any;
  confidence?: number;
  status?: FieldStatus;
  reason?: string;
  source_message_id?: string;
}
