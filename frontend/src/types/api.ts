export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: null | {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  meta: {
    request_id: string;
    timestamp: string;
    pagination?: {
      page: number;
      page_size: number;
      total_items: number;
      total_pages: number;
    } | null;
  };
}

export interface UploadResponse {
  job_id: string;
  statement_id: string;
  status: "queued" | "processing" | "completed" | "failed";
}

export interface JobStatus {
  job_id: string;
  statement_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  stage: string | null;
  error: string | null;
}

export interface Statement {
  id: string;
  filename: string;
  bank_name?: string | null;
  status: "queued" | "processing" | "completed" | "failed";
  created_at?: string;
  [key: string]: any;
}

export interface ValidationSummary {
  total: number;
  duplicates: number;
  failed_or_reversed: number;
  invalid: number;
  average_confidence: number | null;
}

export interface ValidationIssue {
  id: string;
  date: string | null;
  amount: number | null;
  debit_credit: string | null;
  narration: string | null;
  is_duplicate: boolean | null;
  is_failed: boolean | null;
  is_valid: boolean | null;
  validation_notes: string[] | unknown;
}

export interface ValidationReport {
  statement_id: string;
  summary: ValidationSummary;
  issues: ValidationIssue[];
}

export interface BackendTransaction {
  id: string;
  date: string | null;
  sender_account: string | null;
  receiver_account: string | null;
  amount: number | null;
  txn_type: string | null;
  upi_id: string | null;
  narration: string | null;
  narration_normalized: string | null;
  balance: number | null;
  bank_name: string | null;
  reference_number: string | null;
  debit_credit: "CREDIT" | "DEBIT" | string | null;
  platform: string | null;
  is_duplicate: boolean | null;
  is_failed: boolean | null;
  is_valid: boolean | null;
  confidence_score: number | null;
  validation_notes: string[] | unknown;
}

export interface MoneyFlowResponse {
  summary: Record<string, any> | null;
  nodes: Array<{
    id: string;
    type?: string;
    total_in?: number;
    total_out?: number;
    is_accumulation?: boolean;
    [key: string]: any;
  }>;
  edges: Array<{
    source: string;
    target: string;
    total_amount?: number;
    txn_count?: number;
    [key: string]: any;
  }>;
}

export interface RoundTrip {
  id?: string | number;
  nodes?: string[];
  accounts?: string[];
  min_amount?: number;
  total_amount?: number;
  totalAmount?: number;
  duration?: string;
  hops?: number;
  [key: string]: any;
}

export interface RoundTripsResponse {
  count?: number;
  round_trips: RoundTrip[];
}

export interface RoundTripExplanation {
  chain_id?: string | number;
  explanation?: string;
  details?: string;
  why_flagged?: string;
  [key: string]: any;
}

export interface MoneyTrailResponse {
  kind?: string;
  trail?: {
    credit_amount?: number;
    spent?: number;
    remaining?: number;
    fully_traced?: boolean;
    consumed_by?: Array<{
      debit_txn_id?: string;
      amount?: number;
      destination?: string;
      date?: string;
      [key: string]: any;
    }>;
    [key: string]: any;
  };
  [key: string]: any;
}

export interface CaseSummary {
  statements: number;
  transactions: number;
  entities: number;
  duplicates: number;
  failed_or_reversed: number;
  total_credit: number;
  total_debit: number;
  top_risks?: any[];
  money_flow_summary?: any;
}
