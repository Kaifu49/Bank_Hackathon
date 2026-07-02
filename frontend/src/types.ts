export interface Case {
  id: string;
  name: string;
  description: string;
  agency: string;
  status: 'Active' | 'Processing' | 'Completed';
  riskLevel: 'Critical' | 'High' | 'Medium' | 'Low';
  uploadedFilesCount: number;
  transactionsCount: number;
  lastUpdated: string;
  notes?: string;
  creationDate: string;
}

export interface Transaction {
  id: string;
  sender: string;
  senderAccount: string;
  receiver: string;
  receiverAccount: string;
  amount: number;
  currency: string;
  timestamp: string;
  type: string;
  riskScore: number; // 0 to 100
  method: 'Wire' | 'UPI' | 'Crypto' | 'Cash Drop';
  status: 'Cleared' | 'Flagged' | 'Interdicted';
}

export interface SuspiciousFinding {
  id: string;
  severity: 'Critical' | 'High' | 'Medium';
  title: string;
  description: string;
  linkedEntities: string[];
}

export interface RoundTripLoop {
  id: string;
  accounts: string[];
  totalAmount: number;
  duration: string;
  hops: number;
  riskLevel: 'Critical' | 'High' | 'Medium';
  timeline: {
    step: number;
    from: string;
    to: string;
    amount: number;
    date: string;
  }[];
}

export interface TrailNode {
  id: string;
  label: string;
  account: string;
  type: 'Source' | 'Intermediary' | 'Destination';
  amount: number;
  percentage: number;
  date: string;
  suspicious: boolean;
  notes?: string;
}

export interface DataValidationStats {
  duplicatesRemoved: number;
  failedTransactionsDetected: number;
  missingValuesCorrected: number;
  balanceMismatches: number;
  qualityScore: number; // 0 to 100
  duplicates: { rowNum: number; field: string; value: string }[];
  anomalies: { rowNum: number; description: string; resolvedValue: string }[];
}

export interface EvidenceFile {
  id: string;
  name: string;
  size: string;
  type: string; // 'CSV' | 'PDF' | 'JSON' etc
  status: 'Ready' | 'Processing' | 'Failed';
  rowCount: number;
  uploadDate: string;
}
