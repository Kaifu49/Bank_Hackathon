# FinIntel Backend — API Contract (v1)

Base URL: `http://localhost:8080`  ·  Interactive docs: **`/docs`** (Swagger UI) · spec: **`/openapi.json`**

All endpoints are under `/api/v1`. CORS is enabled (any origin in dev).

## Response envelope (every endpoint)
**Success**
```json
{ "success": true,
  "data": { },
  "error": null,
  "meta": { "request_id": "uuid", "timestamp": "ISO-8601", "pagination": null } }
```
**Error**
```json
{ "success": false,
  "data": null,
  "error": { "code": "VALIDATION_ERROR", "message": "human readable", "details": {} },
  "meta": { "request_id": "uuid", "timestamp": "ISO-8601" } }
```
**Error codes / HTTP status:** `VALIDATION_ERROR` 400 · `UNSUPPORTED_MEDIA_TYPE` 415 · `NOT_FOUND` 404 · `UPSTREAM_SERVICE_ERROR` 502 · `TIMEOUT` 504 · `NOT_IMPLEMENTED` 501 · `INTERNAL_ERROR` 500.

**Pagination:** query `?page=1&page_size=50` (max 200). List responses set `meta.pagination = { page, page_size, total_items, total_pages }`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/statements/upload` | Upload statement (multipart `file`, optional `bank_name`) |
| GET | `/api/v1/jobs/{job_id}/status` | Poll processing status |
| GET | `/api/v1/statements` | List statements (paginated) |
| GET | `/api/v1/statements/{id}` | Statement metadata |
| GET | `/api/v1/statements/{id}/transactions` | Standardized + cleaned txns (paginated) |
| GET | `/api/v1/statements/{id}/validation-report` | Duplicates / failed / mismatches |
| GET | `/api/v1/entities?type=UPI_ID` | List entities (paginated) |
| GET | `/api/v1/entities/{id}` | Entity detail |
| GET | `/api/v1/entities/{id}/aliases` | Entity aliases |
| GET | `/api/v1/entities/{id}/risk-profile` | Fused risk for the entity |
| GET | `/api/v1/entities/{id}/explanation` | Risk factors + evidence |
| GET | `/api/v1/investigations/{case_id}/round-trips` | Circular chains |
| GET | `/api/v1/investigations/{case_id}/money-flow` | Graph `{nodes, edges, summary}` |
| GET | `/api/v1/investigations/{case_id}/graph/clusters` | Communities |
| GET | `/api/v1/investigations/{case_id}/money-trail/{transaction_id}` | FIFO trail for a credit |
| GET | `/api/v1/investigations/{case_id}/timeline?account=` | Chronological events |
| GET | `/api/v1/investigations/{case_id}/top-suspicious-accounts?limit=` | Ranked accounts |
| GET | `/api/v1/investigations/{case_id}/top-risks?limit=` | Top fused risks |
| GET | `/api/v1/investigations/{case_id}/counterparties?account=` | Counterparty breakdown |
| GET | `/api/v1/cases/{case_id}/summary` | Dashboard summary |
| GET | `/api/v1/reports/{case_id}/json` | Report (JSON) |
| GET | `/api/v1/reports/{case_id}/pdf` | Report (PDF) — *Phase 7, returns 501 for now* |
| GET | `/api/v1/reports/{case_id}/excel` | Report (Excel) — *Phase 7, returns 501 for now* |

> `case_id`: use `all` for the whole transaction network; a statement UUID scopes round-trips / money-flow / clusters to that statement.

## Examples

**Upload**
```
POST /api/v1/statements/upload    (multipart/form-data: file=<statement.pdf>)
→ { "success": true,
    "data": { "job_id": "b4a3...", "statement_id": "f7c2...", "status": "queued" },
    "meta": { ... } }
```

**Poll status**
```
GET /api/v1/jobs/b4a3.../status
→ { "success": true,
    "data": { "job_id":"b4a3...", "statement_id":"f7c2...",
              "status":"processing", "progress":65, "stage":"entities", "error":null } }
```
`status`: `queued → processing → completed | failed`.

**Transactions (paginated)**
```
GET /api/v1/statements/f7c2.../transactions?page=1&page_size=50
→ { "success": true,
    "data": [ { "id":"...", "date":"2025-05-06", "amount":2300.0,
                "debit_credit":"CREDIT", "balance":5389.38, "narration":"UPI/.../...",
                "is_duplicate":false, "is_failed":false, "is_valid":true,
                "confidence_score":0.99 } ],
    "meta": { "pagination": { "page":1,"page_size":50,"total_items":237,"total_pages":5 } } }
```

**Money-flow graph (for visualization)**
```
GET /api/v1/investigations/all/money-flow
→ { "success": true, "data": {
    "summary": { "destination_account":"ACC082", "accumulation_accounts":[...], "fan_in":[...] },
    "nodes": [ { "id":"ACC082","type":"ACCOUNT","total_in":17888570.0,"is_accumulation":true } ],
    "edges": [ { "source":"ACC050","target":"ACC082","total_amount":544947.0,"txn_count":3 } ] } }
```

**FIFO money-trail**
```
GET /api/v1/investigations/all/money-trail/<credit_txn_uuid>
→ { "success": true, "data": { "kind":"credit_trail", "trail": {
    "credit_amount":50000, "spent":30000, "remaining":20000, "fully_traced":false,
    "consumed_by":[ {"debit_txn_id":"...","amount":10000,"destination":"rahul@ybl"} ] } } }
```

**Error example**
```
POST /api/v1/statements/upload   (file=foo.gif)
→ 415 { "success": false,
        "error": { "code":"UNSUPPORTED_MEDIA_TYPE",
                   "message":"unsupported file type: 'gif'. Allowed: [pdf, csv, ...]" } }
```
