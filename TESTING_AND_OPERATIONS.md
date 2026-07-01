# FinIntel — Testing & Operations Guide

A complete, practical guide to running the platform, understanding what every
service does, seeing its outputs, following a statement through the pipeline,
and knowing which API route maps to which service.

> Companion docs: [API_CONTRACT.md](API_CONTRACT.md) (frontend contract + examples) ·
> [BACKEND_GAP_ANALYSIS_AND_ROADMAP.md](BACKEND_GAP_ANALYSIS_AND_ROADMAP.md) (architecture & plan).

---

## 1. Architecture at a glance

```
                       Frontend / Swagger / curl
                                  │  HTTP (JSON envelope), CORS
                                  ▼
                    ┌──────────────────────────────┐
                    │  Rust API Gateway  :8080      │   /api/v1/... + /docs
                    │  envelope · errors · jobs     │
                    └──────────────────────────────┘
        upload→worker │                       │ proxy (analysis/reports)
                      ▼                       ▼
   OCR 8001 → Standardize 8002 → Validate 8004 → Entity 8003     Graph 8005
        │            │                │             │            Trail 8009
        └──────── persists ───────────┴─────────────┘            Report 8010
                      ▼                                            Anomaly 8007
                PostgreSQL :5432  (statements, transactions,       Temporal 8008
                                   entities, jobs, risk_profiles)
                      ▼
                Neo4j :7474/:7687  (legacy graph store — optional)
```

Two ways data is produced:
- **Ingestion pipeline** (push): the upload worker calls OCR → Standardize →
  Validate → Entity in sequence and persists to PostgreSQL.
- **Analysis services** (pull / DB-driven): Graph, Risk, Investigation,
  Explainability, Trail, Report read transactions straight from PostgreSQL on
  demand, so they always reflect the latest data.

---

## 2. Service & port reference

| Service | Port | Tech | Role |
|---|---|---|---|
| **API Gateway** | 8080 | Rust / axum | Public API, jobs, proxy, Swagger |
| OCR / Extraction | 8001 | FastAPI | Parse any format → structured rows |
| Standardize | 8002 | FastAPI | Map columns → canonical transactions |
| Entity | 8003 | FastAPI | Extract + resolve entities |
| Validation | 8004 | FastAPI | Duplicates / failed / balance checks |
| Graph | 8005 | FastAPI | Money-flow, round-trips, risk, investigation, explainability |
| Anomaly | 8007 | FastAPI | Isolation-forest statistical anomaly score |
| Temporal | 8008 | FastAPI | Burst / velocity / structuring score |
| Trail | 8009 | FastAPI | FIFO money-trail |
| Report | 8010 | FastAPI | PDF / Excel / DOCX / JSON reports |
| PostgreSQL | 5432 | — | Primary store (`finintel`, postgres/postgres) |
| Neo4j | 7474/7687 | — | Legacy graph store (optional now) |

> Gateway base URLs are env-overridable: `OCR_URL, STANDARDIZE_URL, ENTITY_URL,
> VALIDATION_URL, GRAPH_URL, ANOMALY_URL, TEMPORAL_URL, TRAIL_URL, REPORT_URL`.

---

## 3. Prerequisites & startup

### 3.1 One-time
- PostgreSQL running with DB `finintel` (user/pass `postgres`/`postgres`).
- Apply migrations (creates `statements, transactions, entities, risk_profiles,
  jobs, analysis_cache`):
  ```
  cd backend
  sqlx migrate run      # or: psql -U postgres -d finintel -f each migrations/*.sql
  ```
- Python env (conda `finintel`) with the project deps. Extra for reports:
  `pip install reportlab` (openpyxl + python-docx already present).
- Rust toolchain for the gateway.

### 3.1a Start everything with one command (recommended)
```
./scripts/start-all.ps1        # Windows / PowerShell
./scripts/start-all.sh         # Linux / macOS / Git-Bash
```
Launches all 9 ML services + the gateway. (Sections 3.2/3.3 below are the manual
equivalent.)

### 3.2 Start the Python services (each in its folder)
```
cd ml-services/ocr        && uvicorn main:app --reload --port 8001
cd ml-services/standardize&& uvicorn main:app --reload --port 8002
cd ml-services/entity     && uvicorn main:app --reload --port 8003
cd ml-services/validation && uvicorn main:app --reload --port 8004
cd ml-services/graph      && uvicorn main:app --reload --port 8005
cd ml-services/anomaly    && uvicorn main:app --reload --port 8007
cd ml-services/temporal   && uvicorn main:app --reload --port 8008
cd ml-services/trail      && uvicorn main:app --reload --port 8009
cd ml-services/report     && uvicorn main:app --reload --port 8010
```

### 3.3 Start the gateway
```
cd backend
cargo run        # http://localhost:8080
```

### 3.4 Confirm everything is up
- `GET http://localhost:8080/health` → backend healthy
- `GET http://localhost:8080/services/health` → status of upstream services
- Each service has `GET /health` (e.g. `http://localhost:8005/health`)
- Swagger UI: **http://localhost:8080/docs**

---

## 4. The end-to-end test pipeline (uploading a statement)

What happens when you upload a file:

```
POST /api/v1/statements/upload   (multipart: file, optional bank_name)
   │
   ├─ Gateway validates extension (pdf/csv/xlsx/xls/docx/txt/png/jpg/jpeg)
   ├─ Saves file to backend/storage/statements/<statement_id>/
   ├─ INSERT into statements (status=queued)
   ├─ INSERT into jobs (status=queued, progress=0)
   ├─ Enqueues the job, returns { job_id, statement_id, status:"queued" }
   ▼
Background worker (job → processing):
   10%  ocr         → POST 8001/extract        → rows[]
   30%  standardize → POST 8002/standardize    → canonical transactions
   45%  validate    → POST 8004/validate       → flags + summary
        save        → INSERT transactions (with validation columns)
   65%  entities    → POST 8003/resolve        → canonical_entities
        save        → UPSERT entities
   85%  graph       → GET 8005/flow/analyze/all?refresh=true  → recompute + PERSIST
                      (money-flow, round-trips, clusters cached in analysis_cache)
        risk        → GET 8005/risk/top?refresh=true          → recompute + PERSIST
                      (risk fusion pulls anomaly:8007 + temporal:8008 here)
   100% completed   (jobs.status=completed, statements.status=completed)
   on any error → jobs.status=failed, jobs.error set
```

> **Persistence:** the worker refreshes and caches the whole-network analysis +
> risk after every upload. Read endpoints (`/flow/*`, `/risk/*`,
> `/investigation/top-suspicious`) then serve the persisted `analysis_cache`
> result instantly; append `?refresh=true` to force a recompute. Anomaly and
> temporal are **consumed during the risk refresh step** (not separate worker
> stages).

### Step-by-step test
1. **Upload**
   ```powershell
   curl.exe -F "file=@C:\path\to\statement.pdf" http://localhost:8080/api/v1/statements/upload
   ```
   → note `job_id` and `statement_id`.
2. **Poll status** until `completed`:
   ```
   GET http://localhost:8080/api/v1/jobs/{job_id}/status
   → data.status: queued → processing (progress/stage) → completed | failed
   ```
   (The worker also prints each stage in the `cargo run` console.)
3. **See standardized + cleaned transactions**
   ```
   GET http://localhost:8080/api/v1/statements/{statement_id}/transactions?page=1&page_size=50
   ```
4. **See validation findings**
   ```
   GET http://localhost:8080/api/v1/statements/{statement_id}/validation-report
   ```
5. **See entities**
   ```
   GET http://localhost:8080/api/v1/entities?type=UPI_ID
   ```
6. **Run investigation analysis** (whole network = `all`)
   ```
   GET http://localhost:8080/api/v1/investigations/all/money-flow
   GET http://localhost:8080/api/v1/investigations/all/round-trips
   GET http://localhost:8080/api/v1/investigations/all/top-suspicious-accounts?limit=20
   ```
7. **Risk + explanation**
   ```
   GET http://localhost:8080/api/v1/investigations/all/top-risks?limit=20
   GET http://localhost:8080/api/v1/entities/{entity_id}/explanation
   GET http://localhost:8080/api/v1/investigations/all/round-trips/0/explanation
   ```
8. **Money-trail (FIFO)** — pick a credit transaction id from step 3:
   ```
   GET http://localhost:8080/api/v1/investigations/all/money-trail/{transaction_id}
   ```
9. **Reports**
   ```
   GET http://localhost:8080/api/v1/reports/all/excel   (downloads .xlsx)
   GET http://localhost:8080/api/v1/reports/all/pdf     (downloads .pdf)
   GET http://localhost:8080/api/v1/reports/all/json
   GET http://localhost:8080/api/v1/cases/all/summary
   ```

> `case_id` = `all` analyses the whole network (where loops/accumulation appear).
> A statement UUID scopes round-trips / money-flow / clusters to that statement.

---

## 5. Per-service deep dive (what it does · I/O · how to view)

### 5.1 OCR / Extraction — :8001
**Does:** turns any supported file into structured transaction rows. PDF uses a
**table-first** strategy (`extract_tables`), falling back to a **balance-delta
text reconstructor**; CSV/XLS/XLSX/TXT use a **header-detecting / content-
inferring tabular reader** (handles metadata preambles, no-header files,
tab/pipe delimiters); scanned PDFs route to OCR.

**Key endpoint:** `POST /extract  {"file_path": "<abs path>"}`
**Output:**
```json
{ "source_type":"pdf", "extraction":"tables|text",
  "rows": [ { "date":"...", "narration":"...", "debit":..., "credit":..., "balance":... } ],
  "table_resolution": { "mode":"header_detected|content_inferred" } }
```
**View:** call `/extract` directly, or `POST /debug-table`, `/debug-normalized`.
**Offline tests:** `python -B test_text_reconstructor.py · test_pdf_table_extractor.py · test_tabular_reader.py · test_delimited_reader.py`

### 5.2 Standardize — :8002
**Does:** maps arbitrary bank headers → canonical fields using the **scored,
data-driven Column Intelligence resolver**; normalizes amounts (commas, ₹/INR,
`Cr`/`Dr`, parentheses), splits signed amounts, derives debit/credit.

**Key endpoint:** `POST /standardize  {"rows":[ ... ]}`
**Output:**
```json
{ "count":237,
  "transactions":[ { "date","amount","debit_credit","balance","narration","reference_number", ... } ],
  "column_resolution": { "column_mapping":{...}, "overall_confidence":0.95, "amount_mode":"split" } }
```
**View:** the `column_resolution` block shows exactly how columns were mapped + confidence.
**Offline test:** `python -B test_column_intelligence.py` (71 field cases).

### 5.3 Validation — :8004
**Does (Core Req 2):** duplicates (exact ledger lines), failed/reversed
(debit→credit-back pairs + keywords), running-balance consistency
(`balance[i]=balance[i-1]+credit-debit`), missing-data flags, per-txn confidence.

**Key endpoint:** `POST /validate  {"transactions":[ ... ]}`
**Output:**
```json
{ "count":237,
  "summary": { "total","duplicates","failed_or_reversed","balance_mismatches","missing_data","average_confidence" },
  "transactions":[ { ..., "is_duplicate","is_failed","is_valid","confidence_score","validation_notes":[...] } ] }
```
**View (gateway):** `GET /api/v1/statements/{id}/validation-report`.
**Offline test:** `python -B test_validation.py`.

### 5.4 Entity — :8003
**Does:** extracts UPI IDs, IFSC, banks (via IFSC prefix), accounts (context-
based), phones, persons, merchants/orgs; **type-aware deterministic resolution**
into canonical entities with aliases + occurrence counts (merges across
statements). spaCy is optional.

**Endpoints:** `POST /entities` (raw, deduped) · `POST /resolve` (canonical)
**Output (`/resolve`):**
```json
{ "raw_count":120,
  "canonical_entities":[ { "entity_type":"UPI_ID","canonical":"rahul@ybl",
                           "aliases":["rahul@ybl"],"confidence":0.97,"occurrence_count":4 } ] }
```
**View (gateway):** `GET /api/v1/entities`, `/entities/{id}`, `/entities/{id}/aliases`.
**Offline test:** `python -B test_entity.py` (18 cases).

### 5.5 Graph — :8005  (the analysis hub)
**Does (Core Req 3 & 4 + Phases 4–6):** builds the money-flow graph from DB
transactions (counterparty derived from narration for single-account
statements), detects round-trips, accumulation/sources/fan-in/out/layering,
communities, **risk fusion**, **investigation views**, **explainability**.

**DB-driven (GET):**
| Endpoint | Output |
|---|---|
| `/flow/money-flow/all` | `{summary, nodes, edges}` |
| `/flow/round-trips/all` | `{count, round_trips:[{id,nodes,min_amount,total_amount}]}` |
| `/flow/clusters/all` | `{communities}` |
| `/flow/analyze/all` | everything (summary+round_trips+communities+centrality+graph) |
| `/flow/analyze/statement/{id}` · `/flow/analyze/account/{acct}` | scoped variant |
| `/risk/top?limit=` · `/risk/account/{acct}` | fused risk + factors |
| `/investigation/top-suspicious` · `/investigation/timeline/{acct}` · `/investigation/counterparties/{acct}` · `/investigation/account/{acct}` | investigator views |
| `/explain/account/{acct}` · `/explain/round-trips` · `/explain/round-trip/{chain_id}` | narratives + evidence |

**Stateless (POST `{account?, transactions}`):** `/flow/analyze`, `/flow/money-flow`, `/flow/round-trips`, `/flow/clusters` — test without a DB.
**Persistence:** the whole-network `analyze` and `risk` are cached in
`analysis_cache`. All DB-driven GETs above accept **`?refresh=true`** to
recompute + re-cache (otherwise they serve the cached result instantly). The
upload worker refreshes both after each upload.
**Round-trips:** when the graph has many cycles, the detector scans a pool and
returns the **top `max_results` by bottleneck amount** (a `scan_capped` flag
marks when the pool limit was hit) — the most significant loops, not an
arbitrary subset.
**View:** Swagger at `http://localhost:8005/docs`.
**Offline tests:** `python -B test_flow.py · test_risk.py · test_investigation.py · test_explainability.py`.

### 5.6 Anomaly — :8007 / Temporal — :8008
**Does:** per-account statistical (isolation forest → `stat_score`) and temporal
(burst/velocity/structuring → `temporal_score`) signals. These are **merged into
risk fusion** by the graph service (`/risk/*`).
**Endpoints:** `GET /anomaly` (whole dataset), `/anomaly/latest`,
`/anomaly/account/{acct}`; `GET /temporal` (whole dataset), `/temporal/latest`,
`/temporal/account/{acct}` → `{results:[{account, stat_score|temporal_score, patterns}]}`.
**Coverage:** both now score **all accounts** — the whole-dataset loaders fill
`sender_account` with the statement holder when null, so real single-account
statements are covered (not just multi-account/investigation data). The graph
risk fusion consumes `GET /anomaly` + `GET /temporal`.

### 5.7 Trail — :8009  (Core Req 5, graded)
**Does:** **FIFO money-trail** — each credit opens a lot; debits consume oldest
lots first; reports, per credit, the ordered debits that spent it **and where**
(counterparty), with `spent`/`remaining`/`fully_traced`.
**Endpoints:** `GET /trail/transaction/{txn_id}` (a specific credit; reverse-
lookup for a debit) · `/trail/account/{acct}` · `/trail/statement/{id}` · `POST /trace`.
**View (gateway):** `GET /api/v1/investigations/all/money-trail/{transaction_id}`.
**Offline test:** `python -B test_fifo.py` (matches the documentation example).

### 5.8 Report — :8010  (Core Req 6, graded)
**Does:** assembles the report model (DB + graph) and renders **JSON / Excel /
PDF / DOCX** with Executive Summary, Top Suspicious Accounts, Round-Trips, Money
Flow, Entities, Recommendations.
**Endpoints:** `GET /report/{case_id}/{json|excel|pdf|docx}`.
**Scoping (all 4 formats):** every format calls the same `build(case_id)` —
`case_id="all"` = whole network; a **statement UUID** scopes counts/validation to
that statement and pulls `/flow/analyze/statement/{id}`. So JSON, Excel, PDF and
DOCX are all scoped consistently by `case_id`.
**Persistence:** the assembled report is cached in `analysis_cache` per
`case_id`; append `?refresh=true` to rebuild.
**View (gateway):** `GET /api/v1/reports/{case_id}/{json|pdf|excel|docx}` (binary
formats download via `Content-Disposition`).

---

## 6. Gateway API route → service map

| Gateway route (`:8080`) | Proxies / reads | Core Req |
|---|---|---|
| `POST /api/v1/statements/upload` | worker → OCR→Std→Val→Entity, DB | 1 |
| `GET /api/v1/jobs/{job_id}/status` | `jobs` table | 1 |
| `GET /api/v1/statements[/{id}]` | `statements` table | 1 |
| `GET /api/v1/statements/{id}/transactions` | `transactions` table | 1,2 |
| `GET /api/v1/statements/{id}/validation-report` | `transactions` (validation cols) | 2 |
| `GET /api/v1/entities[/{id}][/aliases]` | `entities` table | — |
| `GET /api/v1/entities/{id}/risk-profile` | Graph `/risk/account` | 4 |
| `GET /api/v1/entities/{id}/explanation` | Graph `/explain/account` | 6 |
| `GET /api/v1/investigations/{case}/round-trips` | Graph `/flow/round-trips` | 3 |
| `GET /api/v1/investigations/{case}/round-trips/{chain}/explanation` | Graph `/explain/round-trip` | 6 |
| `GET /api/v1/investigations/{case}/money-flow` | Graph `/flow/money-flow` | 4 |
| `GET /api/v1/investigations/{case}/graph/clusters` | Graph `/flow/clusters` | 3 |
| `GET /api/v1/investigations/{case}/money-trail/{txn}` | Trail `/trail/transaction` | 5 |
| `GET /api/v1/investigations/{case}/timeline?account=` | Graph `/investigation/timeline` | 5 |
| `GET /api/v1/investigations/{case}/top-suspicious-accounts` | Graph `/investigation/top-suspicious` | 5 |
| `GET /api/v1/investigations/{case}/top-risks` | Graph `/risk/top` | 4 |
| `GET /api/v1/investigations/{case}/counterparties?account=` | Graph `/investigation/counterparties` | — |
| `GET /api/v1/cases/{case}/summary` | DB + Graph | 6 |
| `GET /api/v1/reports/{case}/{json,pdf,excel,docx}` | Report service | 6 |

---

## 7. How to view results (three ways)

1. **Swagger UI** — `http://localhost:8080/docs` (gateway) or each service's
   `:<port>/docs`. Click "Try it out".
2. **HTTP client** — curl / PowerShell `Invoke-RestMethod` / Postman.
   ```powershell
   Invoke-RestMethod http://localhost:8080/api/v1/investigations/all/money-flow | ConvertTo-Json -Depth 8
   ```
3. **Database** — inspect persisted data directly:
   ```
   psql -U postgres -d finintel
   SELECT id, filename, status FROM statements ORDER BY upload_time DESC LIMIT 5;
   SELECT date, amount, debit_credit, balance, is_valid FROM transactions LIMIT 20;
   SELECT entity_type, identifier FROM entities LIMIT 20;
   SELECT id, status, progress, stage, error FROM jobs ORDER BY updated_at DESC LIMIT 5;
   ```

---

## 8. Offline test suite (no DB / no services needed)

The core logic of every service has a pure-Python test that runs standalone:

| Service | Folder | Run |
|---|---|---|
| OCR | ml-services/ocr | `python -B test_text_reconstructor.py` etc. |
| Standardize | ml-services/standardize | `python -B test_column_intelligence.py` |
| Validation | ml-services/validation | `python -B test_validation.py` |
| Entity | ml-services/entity | `python -B test_entity.py` |
| Graph/Risk/Inv/Explain | ml-services/graph | `python -B test_flow.py` / `test_risk.py` / `test_investigation.py` / `test_explainability.py` |
| Trail (FIFO) | ml-services/trail | `python -B test_fifo.py` |

(`-B` avoids `__pycache__` write issues on OneDrive. Use `PYTHONIOENCODING=utf-8`
if the console chokes on the ₹ symbol.)

---

## 9. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Upload returns 415 | Unsupported extension — only pdf/csv/xlsx/xls/docx/txt/png/jpg/jpeg |
| Job stuck at `queued` | Worker not running (rebuild/restart `cargo run`) |
| Job `failed` | Check `jobs.error` and the `cargo run` console; usually an upstream service is down |
| `/standardize` 422 / 500 | An upstream parser returned no/odd rows — check `/extract` output for that file |
| Graph endpoints empty | No transactions in DB yet, or graph service (8005) down |
| `/risk/*` missing temporal/anomaly factors | Services 8007/8008 not running |
| `GET /anomaly` 500 (`no attribute 'process'`) | Fixed — restart the anomaly service to pick it up |
| Stale analysis after new upload | Cache serves last snapshot; append `?refresh=true`, or the worker refreshes on the next upload |
| Report `/pdf` returns 501 | `pip install reportlab` in the report service env |
| Report shows whole-network for a specific case | Fixed — pass a **statement UUID** as `case_id` (all 4 formats scope) |
| `/services/health` shows graph degraded | Cosmetic: legacy `config/services.rs` ports differ from real ports |
| Round-trips seem truncated | Detector keeps top `max_results` by amount (`scan_capped=true` when the scan pool was hit); raise `max_results`/`scan_limit` if needed |

---

## 10. Data model (PostgreSQL)

- **statements** — id, filename, bank_name, status, file_path, upload_time, account_number, account_holder, ifsc_code, opening/closing_balance, statement_start/end_date
- **transactions** — id, statement_id, date, sender/receiver_account, amount, txn_type, upi_id, narration, narration_normalized, balance, bank_name, reference_number, debit_credit, platform, **is_duplicate, is_failed, is_valid, confidence_score, validation_notes**, raw_row
- **entities** — id, entity_type, identifier (unique), display_name, metadata (aliases+confidence)
- **jobs** — id, statement_id, status, progress, stage, error, created/updated_at
- **risk_profiles** — entity_id, rule/stat/temporal/graph/gnn/final scores, risk_level, patterns
- **analysis_cache** — scope (`all`|statement-uuid), kind (`analyze`|`risk`|`report`), payload (JSONB), computed_at — persisted analysis so results aren't recomputed each request

---

## 11. Notes & current state
- Analysis results (graph/risk/report) are now **persisted** in `analysis_cache`
  and refreshed by the upload worker; append `?refresh=true` to force recompute.
- Anomaly/temporal now score **all accounts** (whole-dataset loaders fill the
  holder account), and are consumed by risk fusion.
- Reports are **scoped by `case_id`** across all formats (JSON/Excel/PDF/DOCX).
- Neo4j is **optional** — all current analysis is in-memory/DB-driven; the legacy
  `/build-graph` Neo4j routes remain but are not in the pipeline.
- `case_id`: use `all` for the whole network; a statement UUID scopes
  round-trips/money-flow/clusters and reports.
- Known follow-up: anomaly `feature_builder` yields `NaN` std for single-txn
  accounts — add `fillna(0)` in the isolation detector if it surfaces.
```
