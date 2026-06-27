# Fully Detailed Documentation

## Conda env setup
- ***nvidia-sim***
Wed Jun 10 12:28:19 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 581.95                 Driver Version: 581.95         CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 ...  WDDM  |   00000000:01:00.0 Off |                  N/A |
| N/A   48C    P8              3W /   90W |     554MiB /   8188MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A           11572    C+G   ....0.3967.96\msedgewebview2.exe      N/A      |
|    0   N/A  N/A           12784    C+G   ...2txyewy\CrossDeviceResume.exe      N/A      |
|    0   N/A  N/A           15292    C+G   ...aude\app-1.11187.4\claude.exe      N/A      |
|    0   N/A  N/A           16576    C+G   ..._cw5n1h2txyewy\SearchHost.exe      N/A      |
|    0   N/A  N/A           16588    C+G   ...y\StartMenuExperienceHost.exe      N/A      |
|    0   N/A  N/A           19404    C+G   ...lare WARP\Cloudflare WARP.exe      N/A      |
|    0   N/A  N/A           19652    C+G   ...\SubAgent\AlienFXSubAgent.exe      N/A      |
|    0   N/A  N/A           20812    C+G   ...5n1h2txyewy\TextInputHost.exe      N/A      |
|    0   N/A  N/A           27036    C+G   ...aude\app-1.11187.4\claude.exe      N/A      |
|    0   N/A  N/A           27056    C+G   ...8bbwe\PhoneExperienceHost.exe      N/A      |
|    0   N/A  N/A           28656    C+G   ...indows\System32\ShellHost.exe      N/A      |
|    0   N/A  N/A           30256    C+G   ...1g1gvanyjgm\WhatsApp.Root.exe      N/A      |
|    0   N/A  N/A           34040    C+G   ...yb3d8bbwe\WindowsTerminal.exe      N/A      |
|    0   N/A  N/A           36904    C+G   ...cord\app-1.0.9240\Discord.exe      N/A      |
+-----------------------------------------------------------------------------------------+
- ***conda --version***
conda 25.5.1

## Step 1 — Create Environment
***conda create -n finintel python=3.11 -y***
Activate:
***conda activate finintel***

## Step 2 — Upgrade Pip
python -m pip install --upgrade pip
Verify:
pip --version
Step 3 — Install CUDA PyTorch

Use the official CUDA 12.1 build:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

## Step 4 — Verify GPU Access
Run:
python
Then:
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

Expected:
True
NVIDIA GeForce RTX 4060 Laptop GPU

## Step 5 — Install Core ML Stack
Windows PowerShell alternative:
pip install numpy pandas scikit-learn matplotlib seaborn jupyter ipykernel scipy

## Step 6 — Install NLP Stack
pip install spacy sentence-transformers transformers accelerate
Then:
python -m spacy download en_core_web_sm

## Step 7 — Install OCR Stack
pip install paddleocr
For OpenCV:
pip install opencv-python
PDF tools:
pip install pdfplumber camelot-py pypdf
Excel:
pip install openpyxl xlrd

## Step 8 — Install Database Drivers
pip install neo4j psycopg2-binary sqlalchemy

## Step 9 — Install FastAPI Stack
pip install fastapi uvicorn python-multipart httpx

## Step 10 — Install Explainability Stack
pip install shap

## Step 11 — Install RAG Stack
pip install langchain langchain-community faiss-cpu

## Step 12 — Save Environment
After everything is installed:
conda env export > environment.yml
This will allow the entire team to reproduce the environment instantly.

## Step 13 — Install Rust
For the backend:
winget install Rustlang.Rustup
Verify:
rustc --version
cargo --version

# Phase 0: Infrastructure & Monorepo Setup
Our goal is:
Phase 0 Success Criteria

✅ Monorepo created
✅ Rust backend boots
✅ Python services boot
✅ PostgreSQL container runs
✅ Neo4j container runs
✅ Docker Compose starts everything
✅ Health checks work
✅ Service-to-service communication ready

## Step 1: Project structure
finintel/
│
├── backend/
│
├── ml-services/
│   ├── ocr/
│   ├── standardize/
│   ├── entity/
│   ├── anomaly/
│   ├── temporal/
│   ├── graph-ml/
│   └── explainer/
│
├── frontend/
├── graph-db/
├── storage/
├── scripts/
├── docs/
│
├── docker-compose.yml
├── .env
└── README.md

## Step 2: Initialize Rust Backend
backend/
├── Cargo.toml
└── src/
    └── main.rs

- ***cargo init***

## Step 3: Configure rust dependencies
- backend/Cargo.toml

## Step 4: Backend API Health Rust
- backend/src/main.rs
- Working Fine

http://localhost:8080/health

## Step 5: Python Service tempelate
## Step 6: OCR Service
ml-services/ocr/
│
├── main.py
└── requirements.txt

***uvicorn main:app --reload --port 8001***
http://localhost:8001/health
- Working Fine

## Step 7: Create .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=finintel

POSTGRES_PORT=5432

NEO4J_USER=neo4j
NEO4J_PASSWORD=password

NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687

## Step 8: Docker Compose 
- ***docker compose up -d***
- verify ***docker ps***
- working fine
finintel-postgres
finintel-neo4j

## Step 9: Create PostgreSQL Schema

We want the database structure finalized before any ingestion code is written.
scripts/
└── init_postgres.sql

## Step 10: Neo4j Constraints
graph-db/
└── constraints.cypher

http://localhost:7474

## Step 11: Shared services contract model
ml-services/
└── shared/
    └── models.py

## Step 12: Remaining microservices skeleton
- standardize : port 8002
- entity : port 8003
- anomaly : 8004
- temporal : 8005
- graph ml : 8006
- explainer : 8007

## Step 13: Rust service registry
backend/src/config/services.rs
- Service Communication working fine

finintel/
│
├── backend/
│
├── ml-services/
│   │
│   ├── shared/
│   │   └── models.py
│   │
│   ├── ocr/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── standardize/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── entity/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── anomaly/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── temporal/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── graph-ml/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── explainer/
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── frontend/
├── graph-db/
├── storage/
├── scripts/
└── docker-compose.yml

## Step 14: Test
http://localhost:8080/services/health

- all the services working and reported to rust
{
  "backend": {
    "service": "finintel-backend",
    "status": "healthy"
  },
  "services": {
    "ocr": {
      "service": "ocr",
      "status": "healthy"
    },
    "standardize": {
      "service": "standardize",
      "status": "healthy"
    },
    "entity": {
      "service": "entity",
      "status": "healthy"
    },
    "anomaly": {
      "service": "anomaly",
      "status": "healthy"
    },
    "temporal": {
      "service": "temporal",
      "status": "healthy"
    },
    "graph_ml": {
      "service": "graph_ml",
      "status": "healthy"
    },
    "explainer": {
      "service": "explainer",
      "status": "healthy"
    }
  }
}

## Step 15: Refactoring the rust backend
- Done
src/
│
├── main.rs
│
├── config/
│   ├── mod.rs
│   └── services.rs
│
├── routes/
│   ├── mod.rs
│   └── health_routes.rs
│
├── handlers/
│   ├── mod.rs
│   └── health_handler.rs
│
├── services/
│   ├── mod.rs
│   └── service_checker.rs
│
├── models/
│   ├── mod.rs
│   └── health.rs
│
├── repositories/
│   └── mod.rs
│
└── state/
    ├── mod.rs
    └── app_state.rs

# Intermediate Chnages
- Switched to SQLx Migration for better bacckend axum handling
- backend structuree
routes/
│
├── health_routes.rs
└── statement_routes.rs

handlers/
│
├── health_handler.rs
└── statement_handler.rs

models/
│
├── health.rs
└── statement.rs

repositories/
│
├── statements.rs
└── mod.rs

services/
│
├── service_checker.rs
├── storage.rs
└── mod.rs

# Phase 1: Multi-Format Ingestion Pipeline
By the end of Phase 1, this flow should work:

Frontend
   ↓
Upload PDF/CSV/Image
   ↓
Rust Backend
   ↓
Validate File
   ↓
Store File
   ↓
Insert Statement Record
   ↓
Create Job
   ↓
Queue Job
   ↓
Return job_id

and:

Frontend
   ↓
Poll Status Endpoint
   ↓
queued
processing
complete
failed

- Just a bulletproof ingestion gateway

## Step 1: Statement models
- backend/src/models/statement.rs
- models/mod.rs

## Step 2: Queue Service
- backend/src/services/queue.rs
- services/mod.rs

## Step 3: Storage Service
backend/src/services/storage.rs
Add dependency
Cargo.toml
anyhow = "1"

## Step 4: Statement Repository
- backend/src/repositories/statements.rs
- repositories/mod.rs

## Step 5: Upgrade AppState
- state/app_state.rs

## Step 6: Create Upload Route Skeleton
- Create Upload Route Skeleton
- routes/mod.rs

## Step 7: Handler Skeleton
- handlers/statement_handler.rs
- handler/mod.rs

## Step 8: Register Routes
- main.rs

## Testing
http://localhost:8080/api/v1/statements/upload
- Post working

http://localhost:8080/api/v1/statements/123/status
- get working

## Phase 1: Real Upload Pipeline
The placeholder:
POST /api/v1/statements/upload

Upload File
    ↓
Validate MIME Type
    ↓
Generate UUIDs
    ↓
Create Storage Directory
    ↓
Save File
    ↓
Insert Statement Record
    ↓
Create Processing Job
    ↓
Push Into Queue
    ↓
Return Response

## Step 1: Add required dependencies
- cargo.toml

## Step 2: Create job status store
- src/state/job_status.rs
- // state/mod.rs

## Step 3: Upgrade AppState
- state/app_state.rs

## Step 4: Create statement status model
models/statement.rs

## Step 5: Update statement repository

## Step 6: Real Upload handler
- handlers/statement_handler.rs

## Step 7: Real Status Endpoint

## Step 8: Create worker
- services/worker.rs

## Step 9: Initialize queue in main.rs

## Step 10: Test 
- cargo run
    PostgreSQL Connected
    Background Worker Started
    FinIntel Backend running on http://localhost:8080


post: http://localhost:8080/api/v1/statements/upload
key : file -> file
value -> upload document
send
Expected response:

{
  "job_id": "b4a3....",
  "statement_id": "f7c2....",
  "status": "queued"
}

- Verify File Storage

After upload:

Check:

storage/
└── statements/
    └── <statement-id>/
        └── sample.pdf

Example:

storage/statements/
    f7c2f85d-...
        sample.pdf

- Verify PostgreSQL Insert

Open PostgreSQL:

docker exec -it finintel-postgres psql -U postgres -d finintel

Run:

SELECT * FROM statements;

Expected:

id
filename
bank_name
status
file_path
upload_time

You should see the uploaded file.

- Verify Worker

Look at the terminal where Rust is running.

Expected:

Processing statement: f7c2f85d-...

If you see that:

✅ Queue Works
✅ Worker Works

- Verify Status Endpoint

Use the job_id returned from upload.

Example:

GET http://localhost:8080/api/v1/statements/b4a3.../status

Expected:

{
  "job_id": "b4a3...",
  "status": "queued",
  "progress": 0,
  "error": null
}

- Everything working fine perfectly

## Endpoints
Rust Backend

In main.rs:

let listener =
    tokio::net::TcpListener::bind(
        "0.0.0.0:8080"
    )

So the backend runs on:

http://localhost:8080

Endpoints:

GET  http://localhost:8080/health

GET  http://localhost:8080/test-ocr

GET  http://localhost:8080/services/health

POST http://localhost:8080/api/v1/statements/upload

GET  http://localhost:8080/api/v1/statements/{job_id}/status
Python OCR Service

Started with:

uvicorn main:app --reload --port 8001

Runs on:

http://localhost:8001

Endpoint:

GET  http://localhost:8001/health

POST http://localhost:8001/extract
Standardize Service
uvicorn main:app --reload --port 8002

Runs on:

http://localhost:8002

Endpoints:

GET  http://localhost:8002/health

POST http://localhost:8002/standardize
Entity Service
http://localhost:8003
Anomaly Service
http://localhost:8004
Temporal Service
http://localhost:8005
Graph ML Service
http://localhost:8006
Explainer Service
http://localhost:8007
PostgreSQL

Docker exposes:

ports:
  - "5432:5432"

Connection:

localhost:5432

Connection string:

postgres://postgres:postgres@localhost:5432/finintel
Neo4j

Browser UI:

http://localhost:7474

Bolt Protocol:

bolt://localhost:7687

## Current status
Upload File
     ↓
Rust API
     ↓
Validate Request
     ↓
Store File
     ↓
Insert Statement Record
     ↓
Create Job
     ↓
Queue Job
     ↓
Worker Receives Job
     ↓
Status Endpoint

## Improvements of phase 1
1. MIME Type Validation
Allow only:

PDF
CSV
XLSX
XLS
DOCX
PNG
JPEG
JPG

Reject everything else.

2. Bank Name Support
Update Upload Endpoint
The multipart request should support:
file
bank_name

3. Status Lifecycle
Current: queued only.
Let's add:queued,processing,completed,failed

4. Remove Dangerous unwrap()
.expect("Useful Message")

- **Phase 1 Completed: Everything working fine**

# Phase 2: OCR & Intelligent Parsing Engine

- Extraction Architecture
Uploaded File
      ↓
Worker
      ↓
Parser Router
      ↓
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ PDF Parser   │ CSV Parser   │ Excel Parser │ DOCX Parser  │ Image Parser │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
      ↓
Raw Extracted Rows
      ↓
Field Detection
      ↓
Standardized Transactions
      ↓
PostgreSQL

Uploaded File
      ↓
Worker
      ↓
Parser Router
      ↓
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ PDF Parser   │ CSV Parser   │ Excel Parser │ DOCX Parser  │ Image Parser │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
      ↓
Raw Extracted Rows
      ↓
Field Detection
      ↓
Standardized Transactions
      ↓
PostgreSQL

and so onn

## Step 1: Dependencies
- ***pip install pdfplumber pandas openpyxl python-docx***

## Step 2: OCR Structure
ocr/
│
├── main.py
│
├── parsers/
│   ├── __init__.py
│   ├── parser_registry.py
│   ├── pdf_parser.py
│   ├── csv_parser.py
│   ├── excel_parser.py
│   ├── docx_parser.py
│   └── image_parser.py
│
├── services/
│   ├── __init__.py
│   └── extraction_service.py
│
└── models/
    ├── __init__.py
    └── extraction_models.py

## Step 3: Extraction models
- models/extraction_models.py

## Step 4: Multiformat parsers
- parsers/pdf_parser.py etc
- PDF
- CSV
- Excel
- DOCX
- Temporary Image parser

## Step 5: Parser registry
- parser/parser_registry.py

## Step 6: Extraction Service
- services/extraction_service.py

## Step 7: OCR Endpoint
- ocr/main.py

## Test
- uvicorn main:app --reload --port 8001
http://localhost:8001/docs
- upload the file path
- working fine

## Phase 2.2: OCR Integration
Goal:

Scanned PDF
      ↓
OCR
      ↓
Text
      ↓
Raw Rows

and

PNG/JPG
      ↓
OCR
      ↓
Text
      ↓
Raw Rows

- we'll do proper ocr
Image/PDF
      ↓
Preprocessing
      ↓
OCR
      ↓
Text Cleanup
      ↓
Raw Rows

- What we have now:
PDF
 ↓
Text Extraction

Scanned PDF
 ↓
OCR

PNG
 ↓
OCR

JPEG
 ↓
OCR

CSV
 ↓
Direct Parse

Excel
 ↓
Direct Parse

DOCX
 ↓
Direct Parse

## Step 1: OCR Dependencies

## Step 2: OCR Service layer

## Step 3: OCR Service
- services/ocr_service.py

## Step 4: Image parser OCR

## Step 5: Detect scanned pdf

## Step 6: Create pdf ocr parser

## Step 7: Update extraction service

## Test
- Both scanned and normal pdf getting extracted properly
- Scanned images getting extracted properly

## Phase 2.3: Standardize bank statement
Convert:

[
    {
        "Txn Date": "01/05/2025",
        "Description": "UPI PAYMENT",
        "Amount": "-500",
        "Balance": "9500"
    }
]

into:

[
    {
        "date": "01/05/2025",
        "narration": "UPI PAYMENT",
        "transaction_id": None,
        "debit": 500,
        "credit": None,
        "balance": 9500
    }
]

## Step 1: standard transaction model
- standardize/models/transaction.py

## Step 2: Header detection engine
- standardize/services/header_mapper.py

## Step 3: Header mapper
- standardize/services/header_mapper.py

## Step 4: Row standardizer
- standardize/services/row_standardizer.py

## Step 5: Standardizer service
- standardize/services/standardization_service.py

- Complete 
Somethings left
- Enhancement of ocr intelligence
- transaction quality filter


# Phase 3: Transaction Standardization & Entity Intelligence

ml-services/
└── standardize/
    ├── main.py
    ├── services/
    │   ├── date_normalizer.py
    │   ├── amount_normalizer.py
    │   ├── narration_parser.py
    │   └── standardization_service.py
    └── models/
        └── transaction.py

Raw Transaction
↓
Header Mapping
↓
Canonical Transaction
↓
Date Normalization
↓
Amount Normalization
↓
Transaction Classification
↓
Standardized Transaction

✅ Header Mapping
✅ Row Standardization
✅ Date Normalization
✅ Amount Normalization
✅ Transaction Classification

## Phase 3.3A: Entity extraction service
- localhost:8003

## Step 1: Service structure
- ml-services/entity/
entity/
│
├── main.py
│
├── models/
│   └── entity.py
│
└── services/
    ├── entity_extractor.py
    ├── upi_extractor.py
    ├── account_extractor.py
    ├── organization_extractor.py
    └── bank_extractor.py

Test payload:

{
  "transactions": [
    {
      "narration":
      "UPI/rahul@ybl/PAYTM PAYMENT",

      "reference_number":
      "817716113199"
    }
  ]
}

{
  "count": 3,
  "entities": [
    {
      "entity_type": "UPI_ID",
      "identifier": "rahul@ybl"
    },
    {
      "entity_type": "ACCOUNT_NO",
      "identifier": "817716113199"
    },
    {
      "entity_type": "ORGANIZATION",
      "identifier": "PAYTM"
    }
  ]
}

## Phase 3.3B: Entity Resolution
- services/entity_resolver.py

## Phase 3.3C: Advanced entity intelligence
This is where we move beyond regex extraction and start identifying:

PERSON
ORGANIZATION
MERCHANT
BANK
ACCOUNT
UPI_ID

from transaction narrations.

- ml-services/entity/services/spacy_entity_extractor.py


**DB connected to local postgres : psql -U postgres -h localhost -p 5432 -d finintel**

## Phase 3.5: Service development - data validation
ml-services/
└── validation/
    │
    ├── main.py
    │
    ├── models/
    │   └── validated_transaction.py
    │
    └── services/
        ├── validation_service.py
        ├── duplicate_detector.py
        ├── failed_transaction_detector.py
        └── balance_validator.py

port 8004

test:
{
  "transactions": [
    {
      "date": "2025-01-05",
      "amount": 500,
      "reference_number": "123"
    },
    {
      "date": "2025-01-05",
      "amount": 500,
      "reference_number": "123"
    }
  ]
}

- {
  "is_duplicate": true
}


- working fine

# Phase 4: Neo4j Graph Construction
## Phase 4A
## Step 1: verify neo4j
- docker ps
open: http://localhost:7474
login: neo4j
password

## Step 2: structure
ml-services/
└── graph/
    │
    ├── main.py
    │
    └── services/
        ├── neo4j_client.py
        └── graph_builder.py

## Step 4: neo4j client
## Step 5: Graph builder
## Step 6: API layer
## Step 7: test
- uvicorn main:app --reload --port 8005
- http://localhost:8005/docs

## Step 8: test with dataset
using rows from money_flow_graph.csv

## Step 9: verify graph
in neo4j graph
MATCH (n)
RETURN n
LIMIT 25
- nodes visible

MATCH (a)-[r]->(b)
RETURN a,r,b
LIMIT 25
- edges visible

## Phase 4B: Round trip detection
## Phase 4B.1: Graph Aggregation

update graph_builder
- clear neo4j
MATCH (n)
DETACH DELETE n;

- rebuiold graph:
load master_investigation.csv
through post/build-graph

- verify node count
MATCH (n)
RETURN count(n)

- verify relationship count
MATCH ()-[r]->()
RETURN count(r)

- visual verification
MATCH (a)-[r]->(b)
RETURN a,r,b
LIMIT 100

- find most active account
MATCH (a)-[r:TRANSFERRED_TO]->()
RETURN
a.id,
SUM(r.transaction_count) AS txns,
SUM(r.total_amount) AS amount
ORDER BY amount DESC
LIMIT 10

- find biggest money receivers
MATCH ()-[r:TRANSFERRED_TO]->(a)
RETURN
a.id,
SUM(r.total_amount) AS received
ORDER BY received DESC
LIMIT 10

- MATCH ()-[r:TRANSFERRED_TO]->()
WHERE r.transaction_count > 1
RETURN count(r)

- MATCH ()-[r:TRANSFERRED_TO]->()
RETURN
MAX(r.transaction_count),
AVG(r.transaction_count)


## Phase 4C: Money flow analysis
- ml-services/graph/services/money_flow_analyzer.py
- GET /money-flow/ACC008

Before Round Trip Detection

I recommend we upgrade the Money Flow Analyzer first.

Why?

Because the problem statement says:

Track how money flows from one account
to multiple suspect accounts.

Identify destination account where
funds accumulate.

That's literally Money Flow Analysis.

## Phase 4C.1: Investigation Summary API
- GET /investigation/account/{id}

{
  "account": "ACC050",

  "total_outflow": 5304187,

  "direct_receivers": 14,

  "top_receivers": [
    {
      "account": "ACC065",
      "amount": 544947
    },
    {
      "account": "ACC046",
      "amount": 490417
    }
  ],

  "reachable_accounts": 63,

  "accumulation_accounts_reached": [
    "ACC082",
    "ACC047",
    "ACC011"
  ]
}

## Step 1:
- ml-services/graph/services/investigation_service.py
- add endpoint
{
  "account": "ACC050",
  "total_outflow": 5304187,
  "total_inflow": 1287344,
  "reachable_accounts": 73,

  "top_receivers": [
    {
      "account": "ACC065",
      "amount": 544947
    }
  ],

  "top_senders": [
    {
      "account": "ACC011",
      "amount": 300000
    }
  ]
}

- after some modifications:
Result becomes

{
  "account": "ACC050",

  "total_outflow": 5304187,

  "total_inflow": 1849203,

  "direct_receivers": 14,

  "direct_senders": 10,

  "top_receivers": [...],

  "top_senders": [...]
}

=========================================================
✅ Neo4j Graph Construction
✅ Graph Aggregation
✅ Investigation Account API
✅ Money Flow Foundation

- we already have
Source Account
↓
Direct Receivers
↓
Top Receivers

## Phase 4C: Accumulation Detection
Given:
ACC050
 ↓
ACC046
 ↓
ACC082

If:
ACC082
received 5.7M
from many accounts

then:
ACC082
is an accumulation account.

- ml-services/graph/services/accumulation_detector.py
{
  "accounts": [
    {
      "account": "ACC082",
      "total_received": 5793659,
      "sender_count": 14
    },
    {
      "account": "ACC047",
      "total_received": 5272035,
      "sender_count": 12
    }
  ]
}

## Phase 4D: Round trip/ circular money movement detection
- ml-services/graph/services/round_trip_detector.py
- endpoint: round-trips

Complete

# Phase to complete requirements of the hackathon by judges: FIFO Money trail analysis

| Txn | Type   | Amount | Balance |
| --- | ------ | -----: | ------: |
| T1  | CREDIT |  50000 |   60000 |
| T2  | DEBIT  |  10000 |   50000 |
| T3  | DEBIT  |  15000 |   35000 |
| T4  | DEBIT  |   5000 |   30000 |


Investigator asks:

What happened to the 50,000 that came in?

FIFO says:

Credit(50,000)
   ↓
Debit(10,000)
   ↓
Debit(15,000)
   ↓
Debit(5,000)

Remaining = 20,000

- What The Problem Statement Wants

When a credit amount is received, track how that money is spent until it reaches the previous balance.

This means:

Credit Event
       ↓
Follow subsequent debits
       ↓
Until credit exhausted


ml-services/
└── trail/
    │
    ├── main.py
    │
    ├── models/
    │    └── trail_models.py
    │
    └── services/
         └── fifo_tracker.py


Now we have 3 independent engines:
Engine 1 — Validation
Duplicate
Failed Transaction
Balance Mismatch

Stored in:

transactions.is_duplicate
transactions.is_failed
transactions.is_valid
validation_notes
Engine 2 — Graph Intelligence
Money Flow
Accumulation
Round Trip

Stored in:

Neo4j
Engine 3 — FIFO Trail
Credit
 ↓
Debit
 ↓
Debit

Stored in:

Trail Service

"trails": [
    {
      "credit_amount": 50000,
      "remaining": 0,
      "consumed_by": [
        {
          "debit_amount": 11657
        },
        {
          "debit_amount": 5425
        },
        {
          "debit_amount": 11091
        },
        {
          "debit_amount": 14241
        },
        {
          "debit_amount": 7586
        }
      ]
    },

- working fine


=========================================================
Next agreed roadmap:
Graph Enrichment
        ↓
Temporal Intelligence
        ↓
Statistical Anomaly Detection
        ↓
Risk Fusion
        ↓
Explainable AI
        ↓
Reporting

# Phase 5: Graph enrichment layer
- Current graph
(Account)
    |
TRANSFERRED_TO
    |
(Account)

this is good for flow analysis but not good enough for:
GNN
Community Detection
Shared Merchant Detection
Hidden Networks

Now we want:
(Account)
    |
PERFORMED
    |
(Transaction)
    |
INVOLVES
    |
(Entity)

ACC050
    |
PERFORMED
    |
TXN123
    |
INVOLVES
    |
PAYTM

After enrichment neo4j will know:
Money moved
through PAYTM
to HDFC
using user@paytm
via UPI

## Phase 5A: entity graph enrichment
- ml-services/graph/services/entity_graph_builder.py

2things: - account graph
         - transaction graph

Long term integratio plan:
Upload
 ↓
OCR
 ↓
Standardize
 ↓
Validate
 ↓
Save Transactions
 ↓
Entity Extraction
 ↓
Build Account Graph
 ↓
Build Entity Graph
 ↓
Graph Analytics
 ↓
Temporal Analysis
 ↓
Anomaly Detection
 ↓
Risk Fusion
 ↓
Explainable AI

## Phase 5A.1: Statement metadata model for better entity graph creation

## New phase: Connecting transaction to graph builder
1. Connect Statement Pipeline → Graph Pipeline
   (MOST IMPORTANT)

2. Complete Investigation Knowledge Graph

3. Temporal Intelligence

4. Anomaly Detection

5. Risk Fusion

6. Explainable AI

7. Reporting

Upload Statement
      ↓
Transactions Saved In PostgreSQL
      ❌
      ❌ (currently stops here)
      ❌
Neo4j Investigation Graph
      ↓
Money Flow
Round Trip
Accumulation
Risk Analysis

we need:
Upload Statement
      ↓
Transactions Saved
      ↓
Graph Builder
      ↓
Neo4j
      ↓
Investigation Engines

- ml-services/graph/services/transaction_graph_builder.py

========================================================
originally: we built separately
Round Trip Detector
Money Flow Analyzer
Accumulation Detector
Money Trail Analyzer
Entity Extraction
Graph Builder

                Upload
                   ↓
             OCR Pipeline
                   ↓
          Standardized Transactions
                   ↓
             PostgreSQL
                   ↓
                Neo4j
                   ↓
        Investigation Engines
where: Round Trip
Money Flow
Money Trail
Accumulation
Risk Scoring
Temporal Analysis

all operate on the same data.

Round Trip Detection
Currently:
GET /round-trips
uses graph data.
We keep it
Later:
Investigation Report
will internally call:
round_trip_detector.detect_cycles()
and include findings automatically


Future Investigation Engine
Eventually we'll have:
class InvestigationEngine:
Internally:
round_trip_results
money_flow_results
money_trail_results
accumulation_results
risk_results
all get combined

Example

User uploads:

master_investigation.csv

System automatically:

Build Graph
Detect Cycles
Find Beneficiaries
Run Money Trail
Extract Entities
Calculate Risk

and returns:

{
  "risk_score": 87,

  "round_trips": [...],

  "money_trails": [...],

  "top_accumulation_accounts": [...],

  "suspicious_entities": [...]
}

## Phase 5B: Integration of neo4j to worker.rs
OCR
 ↓
Standardize
 ↓
Validate
 ↓
Save Transactions
 ↓
Extract Entities
 ↓
Save Entities
 ↓
Call Graph Service

- user uploads statement.pdf
backend automatically
1. OCR
2. Standardize
3. Validate
4. Store transactions
5. Extract entities
6. Store entities
7. Build Neo4j graph
8. Update investigation network

**Test**
upload:phase3_manual_smoke.csv
OCR OUTPUT

STANDARDIZED OUTPUT

VALIDATION OUTPUT

ENTITY OUTPUT

Parsed 9 canonical entities

Entities saved successfully

GRAPH OUTPUT

{
  "status": "success"
}

**Verify Neo4j**
- MATCH (t:Transaction)
RETURN count(t);
== 3

-MATCH (e:Entity)
RETURN count(e);
==9

-MATCH (t:Transaction)-[:INVOLVES]->(e:Entity)
RETURN count(*);
==9

Upload: master_investigation.csv
backend output same

check neo4j:
- 

integration working properly
- upload statement -> check neo4j graph
for both account and transaction


====================================================================================================================

# Phase 6: Statistical anomaly and temporal intelligence engine

First:
Anomaly Service V1

Feature Builder
+
Isolation Forest
+
Stat Score API

Next:
Temporal Service V1

Rapid Propagation
+
Structuring
+
Burst

## Phase 6A: Statistical anomaly engine V1
Transactions
      ↓
Feature Builder
      ↓
Isolation Forest
      ↓
Stat Score

ml-services/
└── anomaly/
    ├── main.py
    ├── models/
    │   └── anomaly_result.py
    └── services/
        ├── feature_builder.py
        ├── isolation_detector.py
        └── anomaly_service.py


{
  "count": 6,
  "results": [
    {
      "account": "ACC001",
      "stat_score": 0.01843638364560475
    },
    {
      "account": "ACC002",
      "stat_score": 0.022451190038558434
    },
    {
      "account": "ACC003",
      "stat_score": 0
    },
    {
      "account": "ACC004",
      "stat_score": 0.20655140229690522
    },
    {
      "account": "ACC005",
      "stat_score": 0.21954550691116825
    },
    {
      "account": "ACC099",
      "stat_score": 0.9999999974828114
    }
  ]
}

## Integration with postgres directly
3 Features:
- load_latest_statement_transactions()
- load_statement_transactions(statement_id)
- load_account_transactions(account)


**Test**
test latest upload
GET/anomaly/latest

Get latest statement ID
SELECT
    id,
    filename,
    upload_time
FROM statements
ORDER BY upload_time DESC
LIMIT 5;

{
  "count": 100,
  "results": [
    {
      "account": "ACC008",
      "stat_score": 0.5043089920402887,
      "patterns": []
    },
    {
      "account": "ACC031",
      "stat_score": 0.5404359737197509,
      "patterns": []
    },
    {
      "account": "ACC038",
      "stat_score": 0.36135105006036145,
      "patterns": []
    },
    {
      "account": "ACC088",
      "stat_score": 0.07534671400411488,
      "patterns": []
    },

test statement scoped
GET /anomaly/statement/<statement_id>
- same output

Test account scoped
SELECT
    sender_account,
    SUM(amount)
FROM transactions
GROUP BY sender_account
ORDER BY SUM(amount) DESC
LIMIT 10;

- GET /anomaly/account/ACC050
{
  "account": "ACC012",
  "stat_score": 0.9999999971657039,
  "patterns": []
}

Fixed the patter issue 
{
  "account": "ACC061",
  "stat_score": 0.25270537484939637,
  "patterns": [
    "high_transaction_frequency",
    "high_counterparty_activity"
  ]
}

## Temporal intelligence
Temporal Intelligence

1. Burst Activity
2. Velocity Spike
3. Structuring
4. Rapid Propagation
5. Dormancy Spike
6. Night Activity

1. Burst Activity
Reason:

Easy
Fast
Highly explainable
Works on synthetic and real datasets

Logic:
For each account:
txn_count(account)

Compute:
mean(txn_count)
std(txn_count)

Then:
burst_score =
(txn_count - mean)
/
std

Accounts with large positive scores:
burst_activity

{
  "account": "ACC050",
  "temporal_score": 0.91,
  "patterns": [
    "burst_activity"
  ]
}

2. Velocity Detector
Example:
ACC050

Normal:
₹50,000/day

Suddenly:
₹9,00,000/day
Even if individual transactions aren't anomalous:
10 × ₹90,000
the total movement is suspicious.

{
        "account": "ACC010",
        "velocity_score": 0.7004512515236324,
        "patterns": [
          "velocity_spike"
        ]
      },

3. Structuring Detector
Example:

ACC050

₹49,000
₹49,000
₹48,500
₹49,500

within short period
instead of:

₹196,000

- working fine on **new aml master dataset**

Current FinIntel Status
Ingestion Layer
PDF Upload          ✅
CSV Upload          ✅
Excel Upload        ✅
OCR Pipeline        ✅
Statement Parsing   ✅
Processing Layer
Standardization     ✅
Validation          ✅
Entity Resolution   ✅
Storage Layer
PostgreSQL          ✅
Neo4j               ✅
Investigation Layer
Money Flow          ✅
Round Trip          ✅
Accumulation        ✅
Intelligence Layer
Statistical Engine  ✅
Temporal Engine     ✅

# Phase 7: Restructuring the pipeline to fit the data
1. Harden Investigation
2. Update entity intelligence
3. Upgrade graph intelligence
4. Add risk fusion
5. Add investigation layer
6. Add reports

Current pipeline
Upload
 ↓
OCR
 ↓
Standardize
 ↓
Validate
 ↓
Entities
 ↓
Graph
 ↓
Statistics
 ↓
Temporal

New changed:
Upload
 ↓
OCR
 ↓
Statement Profile
 ↓
Standardize
 ↓
Validate
 ↓
Narration Intelligence
 ↓
Entity Intelligence
 ↓
Graph Intelligence
 ↓
Statistical Engine
 ↓
Temporal Engine
 ↓
Risk Fusion
 ↓
Investigation Report

## Phase 7A: Data hardening
## Step 1: Statement Profile Service

OCR
      ↓
Statement Profile
      ↓
{
    bank: SBI,

    format: PDF,

    header_row: 17,

    transaction_start: 18,

    transaction_end: 249,

    metadata:
    {
        account_number: "...",
        account_holder: "...",
        ifsc: "...",
        statement_period: "..."
    }
}

- bank detection
- document type
- metadata
- transaction header row
- transaction start row
- transaction end


ml-services/
└── statement-profile/
    ├── main.py
    ├── models/
    │   └── statement_profile.py
    ├── services/
    │   ├── bank_detector.py
    │   ├── metadata_extractor.py
    │   ├── table_detector.py
    │   └── profile_builder.py
    └── requirements.txt

    