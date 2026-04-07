---
name: cbtc-dashboard
description: "CBTC Activity Tracker API integration for building reward dashboards, balance views, and transfer analytics. Use this skill whenever building or modifying admin dashboard UI that shows CBTC rewards, wallet balances, transfer activity, daily metrics, or any analytics from the Activity Tracker API. Also use when the user asks about CBTC data, Zoro wallets, CC rewards, transfer offers, party balances, or reward coupons — whether building UI components, querying data, or debugging API responses. Trigger on: rewards dashboard, CBTC metrics, wallet balances, transfer analytics, daily rewards, mining rounds, tier eligibility, balance distribution, reward aggregation."
---

# CBTC Activity Tracker — API Integration Guide

This skill provides everything needed to integrate the CBTC Activity Tracker API into an admin dashboard or any frontend/backend that needs reward data, wallet balances, and transfer analytics.

## When to Use This

You're building (or modifying) a dashboard and need to:
- Show reward earnings (total CC rewards, per-tx rewards, daily breakdowns, client share)
- Display wallet balances (current, historical, trailing averages, tier eligibility)
- Show transfer activity (counts, volumes, acceptance rates, daily trends)
- Build network-wide analytics views (unique senders, unique holders, balance distribution)

## API Basics

**Base URL:** `https://cbtc-data-api.bitsafe.finance`

**Auth:** None — no API keys or tokens needed.

**All POST endpoints** accept `Content-Type: application/json`. Dates use `YYYY-MM-DD` format.

**Response envelope:**
```json
// Success
{"success": true, "data": <payload>}
// Error
{"success": false, "error": "Error message"}
```

**Performance:** Balance-related endpoints can take 30-120 seconds. Plan for loading states in the UI. Use generous timeouts (120s+) in fetch calls.

**OpenAPI spec:** `https://cbtc-data-api.bitsafe.finance/api-docs/openapi.json`

## Wallets

There are **50 Zoro wallets** to track — 5 named roles + 45 batch wallets.

### Named Wallets

| Label | Role | Party ID |
|-------|------|----------|
| **Retail Pool** | Retail pool + operator (the only wallet with funds) | `8324e2529b::1220efd7374bb65d1ce76f9cf6cfa7f4e9fd896179980d624485978ed0cf46c76d37` |
| **INST-ALPHA** | Institutional 1 (0 CBTC, pre-approved) | `0afed9241a::1220320c5994fd50d10e15a687d336acf65d0ba07f94744d16d68291ac8bb65e2825` |
| **INST-BETA** | Institutional 2 (0 CBTC, pre-approved) | `394df865bf::122058ec34c21cd7707c60c31b0ca721944612b2deb5fa59aeda8a62a06d824257a1` |
| **INST-GAMMA** | Institutional 3 (0 CBTC, pre-approved) | `702758b398::12205271e3242c223dcbf092f3012f54265930c2a2eb465dbd45315d64a34bcfba2f` |
| **Mayank** | Personal wallet (used for funding) | `237268376e::122034217581211f6d9fca5ef447aba2cb9302608dedb336a1f58339178a4cc36f43` |

Note: "Retail Pool" and "SENDER" are the same wallet.

### Batch Wallets (45)

Stored in `/Users/mayank/Clawed/predict-now/wallets-batch.json`. Each entry:
```json
{"index": 1, "partyId": "...", "publicKey": "...", "privateKey": "...", "createdAt": "..."}
```

Load them dynamically — the file may grow as more wallets are created.

## Reference Implementation

A working Python client is bundled at `scripts/cbtc_dashboard.py`. It has:
- All API functions already wired up with correct response parsing
- Wallet loading logic (named + batch from JSON)
- A `run_dashboard()` function that prints a full summary

You can run it directly (`python3 scripts/cbtc_dashboard.py`) or import individual functions. Use it as the reference for how to call each endpoint and handle the responses — especially the quirks documented below.

## Endpoints — What to Use for Each Dashboard Section

### Rewards Section

**Reward summary (aggregated):**
`POST /api/v1/analytics/transfer-reward-aggregation`
```json
// Request
{"parties": ["<party_id>", ...], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
// Response data
{"total_transfer_offers": 19, "accepted_transfer_offers": 16, "total_cc_reward": "55.18", "reward_per_tx": "3.449"}
```

**Daily reward breakdown:**
`POST /api/v1/analytics/daily-rewards`
```json
// Request
{"parties": ["<party_id>", ...], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
// Response data
{
  "daily_rewards": [
    {"date": "2026-03-21", "transfer_creation_count": 15, "accepted_transfer_count": 13, "total_reward": "47.03", "client_reward": "18.81"}
  ],
  "total_accepted_transfer_count": 16,
  "total_estimated_reward": "55.18",   // NOTE: field is "total_estimated_reward", not "total_reward"
  "client_reward": "22.07"             // NOTE: field is "client_reward", not "total_client_reward"
}
```

**Client reward formula:**
```
node_ops_profit_share = 3 * 0.0333 * (total_reward * 0.8)
client_share = (total_reward * 0.8 - node_ops_profit_share) * 0.5
```

**Reward coupons (detailed per-transfer):**
`POST /api/v1/events/reward-coupons`
```json
// Request
{"instrument_id": "CBTC", "sender": ["<party_id>"], "creation_start_date": "...", "creation_end_date": "...", "limit": 100}
// Response includes per record:
// - transfer details (amount, sender, receiver, contract_id)
// - reward_coupon_payload: {amount, round_number}
// - round_info: {mining_round_contract_id, issuance_featured_app_reward_coupon, round, opens_at, closes_at}
// - per_transfer_reward: {faam_batch_count, per_transfer_arc_amount, per_transfer_cc_reward}
```
Default `consumed_by` is `"TransferInstruction_Accept"` (only accepted transfers).

### Balances Section

**Current/historical balances:**
`POST /api/v1/analytics/cbtc-party-balances`
```json
// Request (max 100 parties, max 365 days)
{"parties": ["..."], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
// Response data — NOTE: wrapped in {"balances": [...]}
{"balances": [{"date": "2026-03-25", "party": "...", "balance": "0.0008004721"}]}
```

**30-day trailing average:**
`POST /api/v1/analytics/cbtc-trailing-avg-balance`
```json
// Request (max 100 parties, max 365 days)
{"parties": ["..."], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
// Response data — NOTE: wrapped in {"entries": [...]}
{"entries": [{"date": "...", "party": "...", "daily_balance": "0.0008", "trailing_avg_balance": "0.00014"}]}
```
Includes 29 days before start_date in calculation for accuracy.

**Tier eligibility:**
`POST /api/v1/analytics/cbtc-tier-eligibility`
```json
// Request — use EITHER "date" (single day) OR "start_date"/"end_date" (range)
{"threshold": "0.01", "date": "2026-03-25"}
// Response data
{"threshold": "0.01", "eligible_parties": [{"date": "...", "party": "...", "balance": "..."}], "total_unique_eligible_count": 5}
```
Common thresholds: `"0.001"`, `"0.01"`, `"0.1"`, `"1"`

**Balance distribution (histogram):**
`POST /api/v1/analytics/cbtc-balance-distribution`
```json
// Request (max 90 days)
{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
// Buckets: 0, 0-0.001, 0.001-0.01, 0.01-0.1, 0.1-1, 1-10, 10+
// Response: distribution[].date, distribution[].bucket, distribution[].count
```

### Transfer Activity Section

**Query transfer offers:**
`POST /api/v1/events/transfer-offers`
```json
// Request
{"instrument_id": "CBTC", "sender": ["..."], "receiver": ["..."], "start_date": "...", "end_date": "...", "consumed_by": "TransferInstruction_Accept", "limit": 100}
// consumed_by: "TransferInstruction_Accept" | "TransferInstruction_Reject" | "" (unconsumed) | omit (all)
// Pagination: cursor-based using created_at_offset → offer_created_after_ledger_offset
```

**Count transfer offers:**
`POST /api/v1/events/transfer-offers/count`
Same filters as above (minus `limit`). Returns integer count.

### Network Analytics Section

**Daily accepted transfer count:**
`POST /api/v1/analytics/transfer-offers/daily-count`
```json
{"start_date": "...", "end_date": "...", "choice": "TransferInstruction_Accept"}
// Response: {"daily_counts": [{"day": "2026-03-25", "transfer_count": 42}]}
```

**Daily unique senders:**
`POST /api/v1/analytics/transfer-offers/daily-unique-senders`
```json
{"start_date": "...", "end_date": "..."}
// Response: {"daily_unique_senders": [{"day": "...", "unique_senders": 15}]}
```

**Daily transfer volume:**
`POST /api/v1/analytics/transfer-offers/daily-volume`
```json
{"start_date": "...", "end_date": "..."}
// Response: {"daily_volumes": [{"day": "...", "transfer_volume": "50000.12345678"}]}
```

**Unique CBTC holders:**
`POST /api/v1/analytics/cbtc-unique-holders`
```json
{"start_date": "...", "end_date": "..."}  // max 365 days
// Response: {"daily_counts": [{"date": "...", "unique_holders": 100}]}
```

### Health Check
`GET /health` — returns `{"status": "ok"}` (not the standard envelope).

## Response Format Quirks

These are real discrepancies between the docs and the live API — discovered through testing:

| Endpoint | Docs Say | Actually Returns |
|----------|----------|-----------------|
| `GET /health` | `{"success": true, "data": "OK"}` | `{"status": "ok"}` |
| Party balances | flat list | `{"balances": [...]}` |
| Trailing avg | flat list | `{"entries": [...]}` |
| Daily rewards totals | `total_reward`, `total_client_reward` | `total_estimated_reward`, `client_reward` |

Always check the actual response shape. The bundled `scripts/cbtc_dashboard.py` handles all of these correctly — use it as ground truth.

## Deprecated Endpoints (Do Not Use)

- `POST /api/v1/analytics/cbtc-daily-metrics` — replaced by daily-count/unique-senders/daily-volume
- `POST /api/v1/analytics/cbtc-daily-metrics/total-supply`
- `POST /api/v1/analytics/cbtc-daily-metrics/transfer-volume`
- `POST /api/v1/analytics/cbtc-daily-metrics/transfer-count`
- `POST /api/v1/analytics/cbtc-daily-metrics/unique-users`
