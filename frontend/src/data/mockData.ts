import { Case, Transaction, SuspiciousFinding, RoundTripLoop, TrailNode, DataValidationStats, EvidenceFile } from '../types';

export const mockCases: Case[] = [
  {
    id: 'CASE-2026-001',
    name: 'Project Apex-Delta Loop',
    description: 'Investigation into circular round-tripping flows from Apex Venture Corp to offshore shell corporations, designed to inflate corporate assets and minimize tax liabilities.',
    agency: 'Federal Financial Crime Intelligence Division',
    status: 'Active',
    riskLevel: 'Critical',
    uploadedFilesCount: 3,
    transactionsCount: 12042,
    lastUpdated: '2026-06-14 08:32',
    creationDate: '2026-05-10',
    notes: 'Primary targets: Apex Venture Corp (US), Delta Shell Holdings (Cayman), Vanguard Seychelles Trading. Student nominee Carlos Santana is identified in smurfing cash deposits.'
  },
  {
    id: 'CASE-2026-002',
    name: 'CEO Crypto Off-Ramp',
    description: 'Tracking high-value corporate treasury treasury transfers mapped to private OTC desks, routed to Ethereum smart contracts, and eventually laundered through coin blending protocols.',
    agency: 'Corporate Fraud Taskforce',
    status: 'Processing',
    riskLevel: 'High',
    uploadedFilesCount: 2,
    transactionsCount: 1405,
    lastUpdated: '2026-06-13 14:15',
    creationDate: '2026-06-01',
    notes: 'Linked to Ethereum wallet 0x7a84...38c9 which received $450,000 equivalent before piping into a sanctioned mixing protocol.'
  },
  {
    id: 'CASE-2026-003',
    name: 'Offshore Nominee Ring',
    description: 'Audit of registration papers in Caribbean registers resolving shared nominee directors and ultimate beneficial owners (UBO) behind 14 shell agencies.',
    agency: 'International Tax Compliance Group',
    status: 'Completed',
    riskLevel: 'Medium',
    uploadedFilesCount: 4,
    transactionsCount: 450,
    lastUpdated: '2026-05-24 11:05',
    creationDate: '2026-04-12',
    notes: 'Cayman registry search resolved multiple bearer shares assigned to proxies. Full corporate link chart generated.'
  },
  {
    id: 'CASE-2026-004',
    name: 'Sovereign Cargo Smurfing Ledger',
    description: 'Suspicious physical branch deposits made below the currency transaction report (CTR) threshold of $10,000, structured to buy cargo ship invoices.',
    agency: 'Customs & Port Enforcement Office',
    status: 'Active',
    riskLevel: 'High',
    uploadedFilesCount: 1,
    transactionsCount: 2311,
    lastUpdated: '2026-06-12 17:40',
    creationDate: '2025-12-18',
    notes: 'Identified structuring behavior in bank branch entries across 8 different US states over consecutive business days.'
  }
];

export const mockFindings: SuspiciousFinding[] = [
  {
    id: 'FIND-001',
    severity: 'Critical',
    title: 'Circular Capital Round-Tripping',
    description: 'Apex Venture Corp (US) routed $1,200,000 to Delta Shell Holdings (Cayman) as a "Consulting SLA SLA". Delta Holdings wired $1,180,000 to Seychelles Trade. Trade returned $1,150,000 as "Investment Equity" back to Apex Corp, finalizing an assets-inflation loop.',
    linkedEntities: ['Apex Venture Corp', 'Delta Shell Holdings', 'Vanguard Seychelles Trading']
  },
  {
    id: 'FIND-002',
    severity: 'Critical',
    title: 'AML Structuring / Smurfing Pattern',
    description: 'Nominee Carlos Santana (Account #39281) received 42 structured cash deposits valued between $9,500 and $9,800 over 8 days at different physical branches. These cash deposits were immediately consolidated and wire-transferred in a lump sum of $385,000.',
    linkedEntities: ['Carlos Santana (Account #39281)', 'Delta Shell Holdings']
  },
  {
    id: 'FIND-003',
    severity: 'Critical',
    title: 'USDT Fiat-to-Crypto Off-Ramp via Sanctioned Node',
    description: 'Delta Shell Holdings converted $450,000 USD to Tether (USDT) using smart contract routing. Funds were sent to a decentralized wallet which then initiated 4 sub-wires directly into sanitized Tornado Cash mixing pools.',
    linkedEntities: ['Delta Shell Holdings', 'ERC20 Mixer (0x7a84...)']
  },
  {
    id: 'FIND-004',
    severity: 'Medium',
    title: 'Shared Corporate Signature Alignment',
    description: 'Filing signature audit of Delta Shell Holdings LTD and Vanguard Seychelles Trading matches a single UK-based proxy legal coordinator registered under 42 dormant holding agencies.',
    linkedEntities: ['Delta Shell Holdings', 'Vanguard Seychelles Trading']
  }
];

export const mockTransactions: Transaction[] = [
  {
    id: 'TX-2026-9401',
    sender: 'Apex Venture Corp',
    senderAccount: 'Vanguard Comms #5502',
    receiver: 'Delta Shell Holdings',
    receiverAccount: 'Cayman Secrecy #9910',
    amount: 1200000,
    currency: 'USD',
    timestamp: '2026-10-12 10:14:02',
    type: 'Consulting SLA SLA',
    riskScore: 89,
    method: 'Wire',
    status: 'Cleared'
  },
  {
    id: 'TX-2026-9402',
    sender: 'Delta Shell Holdings',
    senderAccount: 'Cayman Secrecy #9910',
    receiver: 'Vanguard Seychelles Trading',
    receiverAccount: 'Seychelles Trust #1102',
    amount: 1180000,
    currency: 'USD',
    timestamp: '2026-10-14 11:25:30',
    type: 'Sub-Consultancy Export Invoice',
    riskScore: 92,
    method: 'Wire',
    status: 'Cleared'
  },
  {
    id: 'TX-2026-9403',
    sender: 'Vanguard Seychelles Trading',
    senderAccount: 'Seychelles Trust #1102',
    receiver: 'Apex Venture Corp',
    receiverAccount: 'Vanguard Comms #5502',
    amount: 1150000,
    currency: 'USD',
    timestamp: '2026-10-15 15:44:11',
    type: 'Equity Investment Capital Injection',
    riskScore: 95,
    method: 'Wire',
    status: 'Cleared'
  },
  {
    id: 'TX-2026-9410',
    sender: 'Cash Inflow Structure',
    senderAccount: 'Internal Branch ATM Cash Vaults',
    receiver: 'Carlos Santana',
    receiverAccount: 'Mule Acct #39281',
    amount: 9500,
    currency: 'USD',
    timestamp: '2026-10-10 09:12:00',
    type: 'Branch ATM Deposit',
    riskScore: 94,
    method: 'Cash Drop',
    status: 'Flagged'
  },
  {
    id: 'TX-2026-9411',
    sender: 'Cash Inflow Structure',
    senderAccount: 'Internal Branch ATM Cash Vaults',
    receiver: 'Carlos Santana',
    receiverAccount: 'Mule Acct #39281',
    amount: 9800,
    currency: 'USD',
    timestamp: '2026-10-10 11:45:00',
    type: 'Branch ATM Deposit',
    riskScore: 94,
    method: 'Cash Drop',
    status: 'Flagged'
  },
  {
    id: 'TX-2026-9412',
    sender: 'Cash Inflow Structure',
    senderAccount: 'Internal Branch ATM Cash Vaults',
    receiver: 'Carlos Santana',
    receiverAccount: 'Mule Acct #39281',
    amount: 9600,
    currency: 'USD',
    timestamp: '2026-10-11 10:20:00',
    type: 'Branch Teller Cash Drop',
    riskScore: 94,
    method: 'Cash Drop',
    status: 'Flagged'
  },
  {
    id: 'TX-2026-9430',
    sender: 'Carlos Santana',
    senderAccount: 'Mule Acct #39281',
    receiver: 'Delta Shell Holdings',
    receiverAccount: 'Cayman Secrecy #9910',
    amount: 385000,
    currency: 'USD',
    timestamp: '2026-10-12 14:02:15',
    type: 'Personal Loan Repayment',
    riskScore: 91,
    method: 'Wire',
    status: 'Cleared'
  },
  {
    id: 'TX-2026-9440',
    sender: 'Delta Shell Holdings',
    senderAccount: 'Cayman Secrecy #9910',
    receiver: 'ERC20 Mixer (0x7a84...)',
    receiverAccount: 'OTC Exchange Wallet',
    amount: 450050,
    currency: 'USD',
    timestamp: '2026-10-13 18:22:11',
    type: 'Smart Contract Swap',
    riskScore: 98,
    method: 'Crypto',
    status: 'Interdicted'
  }
];

export const mockRoundTrips: RoundTripLoop[] = [
  {
    id: 'LOOP-001',
    accounts: ['Apex Venture Corp', 'Delta Shell Holdings', 'Vanguard Seychelles Trading', 'Apex Venture Corp'],
    totalAmount: 1150000,
    duration: '3 Days',
    hops: 3,
    riskLevel: 'Critical',
    timeline: [
      { step: 1, from: 'Apex Venture Corp', to: 'Delta Shell Holdings', amount: 1200000, date: '2026-10-12' },
      { step: 2, from: 'Delta Shell Holdings', to: 'Vanguard Seychelles Trading', amount: 1180000, date: '2026-10-14' },
      { step: 3, from: 'Vanguard Seychelles Trading', to: 'Apex Venture Corp', amount: 1150000, date: '2026-10-15' }
    ]
  },
  {
    id: 'LOOP-002',
    accounts: ['CEO Shell Account', 'Offshore Trust Panama', 'Vanguard Seychelles Trading', 'CEO Shell Account'],
    totalAmount: 320000,
    duration: '24 Hours',
    hops: 3,
    riskLevel: 'High',
    timeline: [
      { step: 1, from: 'CEO Shell Account', to: 'Offshore Trust Panama', amount: 350000, date: '2026-10-18' },
      { step: 2, from: 'Offshore Trust Panama', to: 'Vanguard Seychelles Trading', amount: 330000, date: '2026-10-18' },
      { step: 3, from: 'Vanguard Seychelles Trading', to: 'CEO Shell Account', amount: 320000, date: '2026-10-19' }
    ]
  }
];

export const mockTrailNodes: TrailNode[] = [
  {
    id: 'TNODE-001',
    label: 'Main Credited Transaction Inflow',
    account: 'Apex Venture Corp #5502',
    type: 'Source',
    amount: 500000,
    percentage: 100,
    date: '2026-10-11',
    suspicious: false,
    notes: 'Trigger credit amount loaded'
  },
  {
    id: 'TNODE-002',
    label: 'Branch Layer Account A',
    account: 'Acct-9901 (Carlos Santana)',
    type: 'Intermediary',
    amount: 100000,
    percentage: 20,
    date: '2026-10-12',
    suspicious: true,
    notes: 'Student courier mule transfer'
  },
  {
    id: 'TNODE-003',
    label: 'Offshore Layer Account B',
    account: 'Acct-7740 (Cayman Nominee Custody)',
    type: 'Intermediary',
    amount: 200000,
    percentage: 40,
    date: '2026-10-12',
    suspicious: true,
    notes: 'Layered offshore shell corporation wire'
  },
  {
    id: 'TNODE-004',
    label: 'Cryptocurrency Wallet Interrogator',
    account: 'Acct-1200 (BitBridge OTC Ex)',
    type: 'Intermediary',
    amount: 200000,
    percentage: 40,
    date: '2026-10-13',
    suspicious: true,
    notes: 'Fiat converted to USDT instantly'
  },
  {
    id: 'TNODE-005',
    label: 'Alpha Real-Estate Hold',
    account: 'UK Escrow Account',
    type: 'Destination',
    amount: 95000,
    percentage: 19,
    date: '2026-10-14',
    suspicious: false,
    notes: 'Integration phase: Luxury asset acquisition'
  },
  {
    id: 'TNODE-006',
    label: 'High-Secrecy Panama Vault',
    account: 'Banco Pan-Espanola #4001',
    type: 'Destination',
    amount: 195000,
    percentage: 39,
    date: '2026-10-14',
    suspicious: true,
    notes: 'Secrecy state integration'
  },
  {
    id: 'TNODE-007',
    label: 'COINHAWK Sanctioned Mixer',
    account: 'Ethereum Address: 0x7a84...',
    type: 'Destination',
    amount: 190000,
    percentage: 38,
    date: '2026-10-15',
    suspicious: true,
    notes: 'Anonymity protocol entry point'
  },
  {
    id: 'TNODE-008',
    label: 'ATM Physical Draft Cash Out',
    account: 'ATM Terminal 88A London',
    type: 'Destination',
    amount: 20000,
    percentage: 4,
    date: '2026-10-15',
    suspicious: true,
    notes: 'Physical liquid dispersion'
  }
];

export const mockValidationStats: DataValidationStats = {
  duplicatesRemoved: 142,
  failedTransactionsDetected: 41,
  missingValuesCorrected: 284,
  balanceMismatches: 8,
  qualityScore: 97.4,
  duplicates: [
    { rowNum: 104, field: 'tx_hash', value: '0x88f29c91a7001b238' },
    { rowNum: 4051, field: 'audit_invoice_no', value: 'INV-8842-OCT26' },
    { rowNum: 9142, field: 'wire_reference', value: 'WIRE-APEX-DELTA-LOOP' }
  ],
  anomalies: [
    { rowNum: 88, description: 'Negative Transaction Value (-$20,000)', resolvedValue: 'Absolute Value Applied (+$20,000)' },
    { rowNum: 294, description: 'Missing ISO Country Code on Seychelles entity', resolvedValue: 'Country resolved to SC (Seychelles)' },
    { rowNum: 1205, description: 'Balance Mismatch: Inflows exceed accounts liquidity', resolvedValue: 'Flagged for Off-book financing inspection' }
  ]
};

export const mockFileList: EvidenceFile[] = [
  {
    id: 'EVID-001',
    name: 'MegaCorp_Bank_Statement_Oct2026.csv',
    size: '1.8 MB',
    type: 'CSV',
    status: 'Ready',
    rowCount: 12042,
    uploadDate: '2026-06-14 05:30'
  },
  {
    id: 'EVID-002',
    name: 'CEO_Crypto_Wallet_Trace.pdf',
    size: '430 KB',
    type: 'PDF',
    status: 'Ready',
    rowCount: 45,
    uploadDate: '2026-06-14 05:32'
  },
  {
    id: 'EVID-003',
    name: 'Offshore_Holdings_LTD_Registry.pdf',
    size: '1.2 MB',
    type: 'PDF',
    status: 'Ready',
    rowCount: 140,
    uploadDate: '2026-06-14 05:40'
  }
];
