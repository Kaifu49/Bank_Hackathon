# FinIntel V2 — Backend Gap Analysis & Production Roadmap

> **Status:** Authoritative engineering plan for the "Real Dataset Generalization + Production Backend" phase.
> **Scope:** Backend only (Rust gateway + Python ML services + PostgreSQL + Neo4j). Frontend is owned by a separate teammate and consumes this backend purely through the versioned HTTP API contract defined here.
> **Source of truth for data:** `docs/docs/Consolidated_Bank_Data.xlsx` (162 real evaluation files). Every parsing/standardization/validation decision is justified against this, not against synthetic data.

---

## 1. Executive Summary

The platform already has a working **architecture and a near-complete feature skeleton** (per `documentation.md`, the team reached ~Phase 7A): Rust/axum gateway orchestrating 9 Python FastAPI services (ocr, standardize, entity, validation, graph, anomaly, temporal, trail, explainer), backed by PostgreSQL and Neo4j. The money-flow / round-trip / accumulation / FIFO-trail engines exist in some form.

**The architecture is sound and will be kept and hardened, not rewritten.** The work now is two-fold:

1. **Generalize ingestion to the real 162-file dataset** — replace any layout/bank-specific assumptions with a *data-driven* column/layout/metadata intelligence layer that works across all banks and formats.
2. **Make the backend a production-grade, self-sufficient API product** — consistent response envelope, real error handling (the current code panics on bad input), CORS, OpenAPI/Swagger, pagination, true async job status, and the full mandated endpoint surface — so the frontend teammate can integrate against a stable contract immediately.

The single biggest risk today is **not a missing feature — it is fragility**: the Rust handler uses `.expect()`/`panic!()` on every upload path, job status is never updated (always returns `queued`), and only 2 of ~20 mandated endpoints exist. These are fixed in Phase 0.

---

## 2. Current-State Inventory (evidence-based)

### 2.1 Rust gateway (`backend/`)
| Area | State | Evidence |
|---|---|---|
| Framework | axum 0.8, sqlx (Postgres), tokio mpsc queue, in-memory job map | `Cargo.toml`, `main.rs` |
| Endpoints live | **Only 2**: `POST /api/v1/statements/upload`, `GET /api/v1/statements/{job_id}/status` | `routes/statement_routes.rs` |
| Error handling | `.expect()` / `panic!()` on every branch of upload | `handlers/statement_handler.rs` |
| Response shape | Raw ad-hoc structs (`UploadResponse`, `StatusResponse`) — no envelope | `models/statement.rs` |
| Job status | In-memory `HashMap`, **never updated** by worker → status is always `queued` | `worker.rs` only `println!`s |
| Worker orchestration | Deeply nested OCR→standardize→validate→entity→graph; errors swallowed with `continue`; jobs never marked `failed` | `worker.rs` |
| Service URLs | Hardcoded `localhost:800x` in worker, **conflicting** with `config/services.rs` registry (stale/unused) | `worker.rs` vs `config/services.rs` |
| CORS | `tower-http` cors dependency present but **not wired** into the router | `main.rs` |
| OpenAPI/Swagger | **None** | — |
| Pagination | **None** | — |
| DB schema | `statements`, `transactions`, `entities`, `risk_profiles` + migrations for validation columns & statement metadata | `backend/migrations/*` |

### 2.2 Python ML services (`ml-services/`)
Present (file-level): `ocr/` (parsers for pdf/scanned-pdf/csv/excel/docx/image + header/table/row/metadata/statement-understanding services), `standardize/` (header_mapper, date/amount normalizers, narration parser, enricher), `entity/` (upi/account/bank/merchant/org/person + spaCy + resolver), `validation/` (duplicate, failed-txn, balance), `graph/` (neo4j client, account/transaction/entity graph builders, money-flow, accumulation, round-trip, investigation), `anomaly/` (isolation forest + features), `temporal/` (burst/velocity/structuring), `trail/` (FIFO tracker), `explainer/`. **All must be re-audited against the real dataset; presence ≠ correctness on real files.**

### 2.3 Environment constraints (this build environment)
- **No Rust toolchain** (`cargo`/`rustc` absent) → Rust changes are written to be correct-by-construction; final compile happens on the developer's device.
- **No raw dataset binaries on disk** — only `Consolidated_Bank_Data.xlsx` text extracts → pure-Python parsing/mapping logic is validated against those extracts here; full OCR/DB/end-to-end runs happen on the developer's device.

---

## 3. Dataset Reality (from `Consolidated_Bank_Data.xlsx`)

- **162 files.** Formats: **PDF 103, XLSX 23, XLS 22, CSV 11, TXT 3.** Folders: Primary 18, Secondary 144.
- **No standalone image files** in the set; scanned content is embedded inside PDFs → "OCR for scanned images" = scanned-PDF OCR path, plus a generic image parser kept for robustness.
- **TXT is a real format** and must be a first-class parser (not in the original 5-format plan).
- **High header diversity** — the standardizer must map all of these to one canonical schema. Observed header families:

| Canonical field | Real-world header variants observed |
|---|---|
| `date` | `DATE`, `TXN DATE`, `TRAN DATE`, `TRAN_DATE`, `TRAN-DATE`, `Tran. Date`, `Tran_Date`, `TXN DT`, `Date*`, `Date` |
| `value_date` | `VALUE DATE`, `Value Date`, `POST DATE` |
| `narration` | `NARRATION`, `Narration`, `DESCRIPTION`, `PARTICULARS`, `TRAN PARTICULAR`, `TRAN_PARTICULAR`, `Transaction Details`, `Transaction Particulars`, `Tran Particular`, `Tran. Remarks` |
| `debit` | `DEBIT`, `DEBITS`, `DR`, `Dr_Amt`, `Debit Amt.`, `WITHDRAWAL`, `WITHDRAWALS`, `WITHDRAWAL AMT` |
| `credit` | `CREDIT`, `CREDITS`, `CR`, `Cr_Amt`, `Credit Amt.`, `DEPOSIT`, `DEPOSITS`, `DEPOSIT AMT` |
| `balance` | `BALANCE`, `BAL`, `Balance Amt.`, `BALANCE AMT`, `Balance(Rs.)`, `Balance Dr` |
| `ref_no` | `REFERENCE`, `Tran Ref Num`, `CHQNO`, `CHQ.NO.`, `CHQ-NUM`, `Cheque No.`, `Instrument Num.`, `Tran_ID`, `TRAN ID`, `Tran Ref Num` |
| `txn_type` | `TRAN TYPE`, `Tran. Type`, `TRAN SUB TYPE`, `Contra` flags |

- **Delimiters vary:** comma CSV (`TRAN_DATE,CHQNO,PARTICULARS,DR,CR,BAL,SOL`), **tab-delimited** CSV (`25078124219247-YASH DUBEY.csv`), pipe-delimited XLSX (`ACCOUNT | ACCT NAME | TRAN ID | ...`).
- **Single-amount-with-sign** vs **split debit/credit** columns both appear → standardizer must handle both.
- **Multi-line cells / `_x000D_` artifacts**, multi-page PDFs, repeated headers per page, opening-balance pseudo-rows (`OPENING BALANCE .00`, `BROUGHT FORWARD`) → must be filtered.

**Implication:** column mapping must be a **scored, synonym-driven, data-driven resolver** (not a per-bank lookup). A small declarative knowledge base (synonyms + bank fingerprints) is derived from this xlsx and shipped as config.

---

## 4. Gap Analysis vs. the 6 Core Requirements (the non-negotiable floor)

| Core Req | Requirement | Current state | Gap → Target |
|---|---|---|---|
| **1** | Multi-format upload + OCR + field detection + standardization | Parsers exist for pdf/csv/excel/docx/image; standardizer exists | **Add TXT parser**; make column mapping data-driven across all observed headers; add per-field confidence + quality metrics; verify scanned-PDF OCR path. Endpoints: `upload`, `jobs/{id}/status`, `statements/{id}/transactions`. |
| **2** | Cleaning: duplicates, failed (debit→credit reversal), balance consistency, missing data | duplicate/failed/balance detectors exist | Re-validate logic against real running-balance sequences; expose `validation-report` endpoint; persist `is_duplicate/is_failed/is_valid/confidence/notes` (columns already migrated). |
| **3** | Round-trip / circular detection across accounts | `round_trip_detector` exists in graph svc | Productionize cycle detection on the real account graph; expose `round-trips` + per-chain explanation; tune for layered chains. |
| **4** | Money-flow visualization (nodes=accounts, edges=txns) + accumulation account | money-flow + accumulation detectors exist | Expose `money-flow` graph payload in a stable, frontend-ready node/edge schema; identify accumulation/destination nodes; fan-in/fan-out. |
| **5** | **Money-trail FIFO**: from a credit, trace subsequent debits until pre-credit balance, FIFO across overlapping credits | `trail/fifo_tracker` exists | Implement **precisely** to spec, per-account, FIFO across multiple open credits; expose `money-trail/{transaction_id}`. (Explicitly graded.) |
| **6** | Reports: PDF **and** Excel, plus summary | explainer present; report generator **not clearly present** | Build a Report service producing JSON/PDF/Excel/DOCX + dashboard summary; expose `reports/{case_id}/pdf|excel|json` + `cases/{case_id}/summary`. (PDF + Excel explicitly graded.) |

---

## 5. Gap Analysis vs. the Production-API Mandate

| Mandate | Current | Target (Phase 0) |
|---|---|---|
| Versioned prefix `/api/v1` | Partial (2 routes) | All routes under `/api/v1`; never mutate a shipped contract |
| Uniform envelope `{success,data,error,meta}` | ❌ ad-hoc | Single `ApiResponse<T>` wrapper used by every handler |
| Uniform error schema (code+status+message) | ❌ panics → 500s | `AppError` enum → `IntoResponse`; no panics on request paths |
| Async job + status polling | Queue exists; **status never updated** | Job store updated to `queued→processing→completed/failed` with progress + error; persisted (DB-backed) so it survives restarts |
| OpenAPI/Swagger at `/docs` | ❌ | `utoipa` + `utoipa-swagger-ui`, generated from code |
| CORS | dep present, not wired | `tower-http` CorsLayer wired (configurable origins) |
| Pagination on list endpoints | ❌ | `?page&page_size` + `meta.pagination` on every list |
| Example payloads per endpoint | ❌ | In OpenAPI + this doc's endpoint catalog |
| Consistent service registry | conflicting ports | Single env-driven registry; worker uses it |

---

## 6. Target Architecture (kept + hardened)

```
Frontend (separate teammate)
        │  HTTP, /api/v1, JSON envelope
        ▼
Rust axum Gateway  ── api/{envelope,error,pagination}, CORS, OpenAPI /docs
        │           ── DB-backed job store (queued→processing→completed/failed)
        │           ── env-driven service registry
        ▼ (async worker, orchestration with per-stage status + graceful errors)
Python ML services (FastAPI), each returning the same envelope:
  ocr → standardize → validate → entity → graph(neo4j) → anomaly → temporal → trail → risk-fusion → report
        │                                   │
        ▼                                   ▼
   PostgreSQL (statements, transactions, entities, risk)     Neo4j (accounts, txns, entities, flows)
```

**Ingestion sub-pipeline (data-driven, Phase 1):**
```
Parser Registry → (OCR if scanned) → Document Normalizer → Statement Intelligence
→ Layout Intelligence → Metadata Intelligence → Table Intelligence → Column Intelligence
→ Universal Standardizer → Validation Engine  (each emits confidence + quality metrics)
```

---

## 7. API Contract Conventions (frozen in Phase 0)

**Success envelope**
```json
{ "success": true, "data": { }, "error": null,
  "meta": { "request_id": "uuid", "timestamp": "ISO-8601", "pagination": null } }
```
**Error envelope**
```json
{ "success": false, "data": null,
  "error": { "code": "VALIDATION_ERROR", "message": "Unsupported file type: image/gif", "details": {} },
  "meta": { "request_id": "uuid", "timestamp": "ISO-8601" } }
```
**Error codes (initial):** `VALIDATION_ERROR` (400), `UNSUPPORTED_MEDIA_TYPE` (415), `NOT_FOUND` (404), `JOB_NOT_FOUND` (404), `CONFLICT` (409), `UPSTREAM_SERVICE_ERROR` (502), `TIMEOUT` (504), `INTERNAL_ERROR` (500).
**Pagination:** query `page` (1-based, default 1), `page_size` (default 50, max 200); `meta.pagination = {page,page_size,total_items,total_pages}`.
**Versioning:** additive changes only on `/api/v1`; breaking changes go to `/api/v2`.
**Job lifecycle:** `queued → processing → completed | failed`; status payload `{job_id,status,progress(0-100),stage,error,statement_id}`.

---

## 8. Full Endpoint Catalog (the contract surface)

| Method | Path | Core Req | Notes |
|---|---|---|---|
| POST | `/api/v1/statements/upload` | 1 | multipart: `file` (1+), optional `bank_name`; returns `job_id`,`statement_id` |
| GET | `/api/v1/jobs/{job_id}/status` | 1 | async status (also keep legacy `/statements/{job_id}/status` alias) |
| GET | `/api/v1/statements` | 1 | list, paginated |
| GET | `/api/v1/statements/{id}` | 1 | metadata + quality metrics |
| GET | `/api/v1/statements/{id}/transactions` | 1,2 | standardized+cleaned, paginated |
| GET | `/api/v1/statements/{id}/validation-report` | 2 | duplicates/failed/balance mismatches |
| GET | `/api/v1/entities` | 2 | list, paginated, filterable by type |
| GET | `/api/v1/entities/{id}` | 2 | canonical entity |
| GET | `/api/v1/entities/{id}/aliases` | 2 | resolved aliases |
| GET | `/api/v1/entities/{id}/risk-profile` | 4 | fused risk + evidence |
| GET | `/api/v1/entities/{id}/explanation` | 6 | why/how/confidence/evidence |
| GET | `/api/v1/investigations/{case_id}/round-trips` | 3 | circular chains |
| GET | `/api/v1/investigations/{case_id}/round-trips/{chain_id}/explanation` | 6 | per-chain evidence |
| GET | `/api/v1/investigations/{case_id}/money-flow` | 4 | node/edge graph payload |
| GET | `/api/v1/investigations/{case_id}/graph/clusters` | 3 | communities |
| GET | `/api/v1/investigations/{case_id}/money-trail/{transaction_id}` | 5 | FIFO debit trail |
| GET | `/api/v1/investigations/{case_id}/timeline` | 5 | temporal events |
| GET | `/api/v1/investigations/{case_id}/top-suspicious-accounts` | 5 | ranked |
| GET | `/api/v1/investigations/{case_id}/top-risks` | 4 | ranked risks |
| GET | `/api/v1/reports/{case_id}/pdf` | 6 | download |
| GET | `/api/v1/reports/{case_id}/excel` | 6 | download |
| GET | `/api/v1/reports/{case_id}/json` | 6 | machine-readable |
| GET | `/api/v1/cases/{case_id}/summary` | 6 | dashboard payload |
| GET | `/api/v1/services/health` | — | gateway + upstream health |

---

## 9. Phased Roadmap (execution order + acceptance criteria)

### Phase 0 — API Foundation & Contract (unblocks frontend)
- `api/` module: `ApiResponse<T>`, `AppError`→`IntoResponse`, pagination types, request-id middleware.
- Wire CORS; add `utoipa` OpenAPI + Swagger `/docs`.
- DB-backed job store; worker updates `processing/completed/failed` + progress/stage.
- Env-driven service registry; remove port conflicts.
- Replace all `.expect()/panic!()` on request paths with typed errors.
- Stub **every** catalog endpoint returning the envelope with realistic mock data.
- **Done when:** every endpoint responds with a valid envelope; `/docs` renders; bad uploads return `415/400` (not 500); status transitions are observable.

### Phase 1 — Ingestion Generalization (Core Req 1, 2)
- Add **TXT parser**; confirm registry routing for all 5 real formats + scanned-PDF OCR.
- **Column Intelligence**: scored synonym resolver driven by a config KB derived from §3; handles split vs single-signed amount, delimiter variants, repeated headers, opening-balance/brought-forward filtering, `_x000D_` cleanup.
- **Universal Standardizer** → canonical schema with per-field confidence + statement quality metrics.
- **Validation Engine** re-audited on real running balances.
- **Done when:** standardization validated against the header families in `Consolidated_Bank_Data.xlsx` (pure-Python test harness), wired through `transactions` + `validation-report` endpoints.

### Phase 2 — Entity Intelligence (Core Req support) → entity endpoints.
### Phase 3 — Graph Intelligence (Core Req 3, 4) → round-trips, money-flow, clusters.
### Phase 4 — Risk Fusion (graph+temporal+anomaly+entity+txn) → risk-profile, top-risks.
### Phase 5 — Investigation Engine incl. **precise FIFO money-trail** (Core Req 5) → money-trail, timeline, top-suspicious.
### Phase 6 — Explainability (why/how/confidence/evidence) → explanation endpoints.
### Phase 7 — Reporting (Core Req 6): JSON/PDF/Excel/DOCX + summary → report endpoints.

Each phase: maps back to ≥1 Core Requirement, exposes real endpoints, ships example payloads, and is validated against multiple banks/formats (never one sample).

---

## 10. Key Decisions & Risks
- **Keep Rust+Python split** — the investment is real and the split is reasonable; consolidation is not worth the cost.
- **Data-driven, not bank-specific** — all mapping lives in config/synonym KBs; no hardcoded layouts.
- **Risk:** real OCR quality on scanned PDFs is unknown until run on-device → keep OCR confidence + quality metrics first-class so low-confidence extractions are flagged, not silently trusted.
- **Risk:** in-memory job store loses state on restart → move to DB-backed in Phase 0.
- **Verification reality:** Rust compiles and full pipeline runs on the developer's device; this environment validates pure-Python logic against dataset text extracts.

---

## 11. Immediate Next Steps
1. Phase 0 Rust API foundation (envelope, errors, CORS, OpenAPI, DB-backed jobs, stubbed full endpoint surface).
2. Phase 1 data-driven Column Intelligence + Universal Standardizer, validated against `Consolidated_Bank_Data.xlsx`.
3. Proceed through Phases 2–7, each ending in live, documented endpoints.
