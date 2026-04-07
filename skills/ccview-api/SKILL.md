---
name: ccview-api
description: "CC View (PixelPlex) Canton Network block explorer API for querying on-chain data — transfers, rewards, prices, supply, parties, ANS, validators, featured apps, and governance. Use this skill whenever fetching Canton mainnet data via the CC View API, building analytics or charts from on-chain metrics, looking up party details, checking transfer history, computing reward-per-transaction, or any task involving ccview.io endpoints. Trigger on: CC View, ccview, PixelPlex, Canton explorer, on-chain data, transfer stats, reward stats, supply stats, CC price, mining round, featured app reward, ANS lookup, party lookup, validator stats, block explorer API, reward per transaction, network analytics."
---

# CC View API — Canton Network Block Explorer

CC View (built by PixelPlex) is the primary block explorer for Canton Network mainnet. This skill covers all working API endpoints, authentication, response shapes, and common query patterns.

## Authentication

**Base URL:** `https://ccview.io`

**API Key:** `$CCVIEW_API_KEY`
- Pass as header: `x-api-key: $CCVIEW_API_KEY`
- Required on ALL requests

**Rate Limits:** Be conservative. Space requests when doing bulk queries. No official rate limit docs — avoid bursts of >10 req/s.

**API Docs:** https://docs.ccview.io/reference/general_search

## Working Endpoints (Tested & Verified)

### Rewards & Mining

**Daily Reward Statistics** — Core endpoint for reward analytics
```
GET /api/v1/rewards/daily_statistic?start=YYYY-MM-DD&end=YYYY-MM-DD&granularity={1h|1d}
```
Response:
```json
{
  "data": [{
    "day": "2026-03-26",
    "grp": 617,                                          // mining round number
    "validator_change_amount_per_day": "14650632.33",     // validator rewards
    "sv_change_amount_per_day": "13288022.63",            // super validator rewards
    "app_change_amount_per_day": "64454171.66",           // featured app rewards (use this for reward/tx calc)
    "burn_fee_per_day": "0",
    "validator_change_amount_accumulated": "3040614133.98",
    "sv_change_amount_accumulated": "24694548264.01",
    "app_change_amount_accumulated": "11200028431.88",
    "burn_fee_accumulated": "0",
    "record_time": "2026-03-26T05:11:57.162976Z"
  }],
  "total_volume": "29525927.91"
}
```
- `granularity`: `1h` for hourly buckets, `1d` for daily
- `grp` = mining round number
- `app_change_amount_per_day` = total featured app reward pool for that period

### Transfer Statistics

**Transfer Count (Ranged)** — For transaction volume analytics
```
GET /api/v2/token-transfers/stat-ranged?start_datetime=ISO8601&end_datetime=ISO8601&granularity={1h|1d}
```
Response:
```json
{
  "series": [
    {"record_time": "2026-03-21T00:00:00Z", "transfers_count": 984690}
  ]
}
```
- Use this + reward data to compute **reward per transaction**: `app_reward / transfers_count`

**Transfer Stat Per Day** — Quick daily snapshot (no date params, returns today)
```
GET /api/v1/explore/transfer-stat-per-day
GET /api/v1/explore/transfer-stat-per-day?day=YYYY-MM-DD
```
Response:
```json
{
  "date": "2026-03-26",
  "total_volume": "41547448.96",
  "transfer": 195708,
  "transfer_allocation": 41495,
  "transfer_instruction": 261,
  "transfer_command": 1,
  "transfer_merge_split": 71028,
  "accumulated_transfer": 130339462,
  "accumulated_transfer_allocation": 11071704,
  "accumulated_transfer_instruction": 412412,
  "accumulated_transfer_command": 1765967,
  "accumulated_transfer_merge_split": 48160681
}
```

**Token Transfer List**
```
GET /api/v2/token-transfers?limit=N
```
Response has `data[]` with each transfer containing:
- `event_id`, `update_id`, `record_time`
- `transfer_data.sender`, `transfer_data.provider`
- `transfer_data.receivers` (map of party_id -> [{output_number, amount, receiver_fee_ratio}])

**Transfers by Party**
```
GET /api/v1/token-transfer/by-party-id/v2?party_id=PARTY_ID&limit=N
GET /api/v1/token-transfer/by-party-id/v3?party_id=PARTY_ID&limit=N
```

**Transfers Between Two Parties**
```
GET /api/v1/token-transfer/by-party-pair?sender=PARTY_ID&receiver=PARTY_ID&limit=N
GET /api/v1/token-transfer/by-party-pair/v3?sender=PARTY_ID&receiver=PARTY_ID&limit=N
```

**Transfer Stats by Party**
```
GET /api/v1/transfer-stat/by-party?party_id=PARTY_ID&granularity={1h|1d}&start_datetime=ISO&end_datetime=ISO
```

### Prices & Supply

**Current Prices** — Quick price summary
```
GET /api/v1/explore/prices
```
Response:
```json
{
  "current": "0.1408000000",
  "start_of_day": "0.1422220000",
  "one_day_ago": "0.1396500000",
  "one_week_ago": "0.1453800000",
  "one_month_ago": "0.1744400000",
  "one_year_ago": "0.0500000000"
}
```

**Historical Prices**
```
GET /api/v1/explore/prices-list?start_datetime=ISO8601&end_datetime=ISO8601
```
Response:
```json
{
  "prices": [{
    "price": "0.1394100000",
    "timepoint": "2026-03-24T23:52:53Z",
    "external_price": "0.1405755723",
    "traffic_kb_cost_in_cc": "0.44064174"
  }]
}
```
- `price` = on-chain CC price, `external_price` = external market price
- Data points roughly every 10 minutes

**Supply Stats**
```
GET /api/v1/explore/supply-stats?start=YYYY-MM-DD&end=YYYY-MM-DD
```
Response:
```json
[{
  "day": "2026-03-25",
  "total_supply_per_day": "9325868189.08",
  "amulet_price_per_day": "0.1422220000",
  "market_cap_per_day": "1326343625.59"
}]
```

### Party & ANS

**General Search** — Search by partial party ID or update ID
```
GET /api/v1/general-search?arg=SEARCH_TERM&limit=N
```
Returns `{ans: {data: [...]}, parties: {data: [...]}}` with matching ANS names and parties.

**Party Details**
```
GET /api/v1/party/details/by-party-id?party_id=PARTY_ID
```

**Party Counterparties**
```
GET /api/v1/party/counterparties?party_id=PARTY_ID&limit=N
```

**Party Balance Changes**
```
GET /api/v1/party/balance-changes/v2?party_id=PARTY_ID&limit=N
```

**Party Transfer Stats**
```
GET /api/v1/party/transfers-count-stat?party_id=PARTY_ID
```

**Party Update Stats**
```
GET /api/v1/party/update-stat?party_id=PARTY_ID
```

**Party Fee Stats**
```
GET /api/v1/party/fee-stat?party_id=PARTY_ID&start=YYYY-MM-DD&end=YYYY-MM-DD
```

**Party Interactions (between two parties)**
```
GET /api/v1/party/interactions?party_id_1=PARTY_ID&party_id_2=PARTY_ID
```

**Resolve Party**
```
POST /api/v1/party/resolve
Body: {"party_ids": ["PARTY_ID", ...]}
```

**ANS Name Availability**
```
GET /api/v1/ans/available/{ans_name}
```

**ANS by Party**
```
GET /api/v1/ans/list/{party_id}
```

**ANS Context by Name**
```
GET /api/v1/ans/context/list-by-name/{ans_name}
```

### Offers & Instructions

**Offers by Sender**
```
GET /api/v1/offer/by-sender-party/v2?party_id=PARTY_ID&status=STATUS&limit=N
```

**Transfer Instructions by Sender**
```
GET /api/v1/token-transfer-instruction/by-sender-party/v2?party_id=PARTY_ID&limit=N
```

**Transfer Preapprovals**
```
GET /api/v1/transfer-preapproval/by-party/v2?party_id=PARTY_ID&limit=N
```

**Transfer Allocations**
```
GET /api/v1/token-transfer-allocation/by-sender-party/v2?party_id=PARTY_ID&limit=N
```

**Transfer Commands**
```
GET /api/v1/token-transfer-command/by-sender-party/v2?party_id=PARTY_ID&limit=N
```

### Validators

**Validator Performance (Ranged)**
```
GET /api/v1/validator/performance-ranged?start_datetime=ISO&end_datetime=ISO&granularity={1h|1d}
```

**Traffic by Validator**
```
GET /api/v1/traffic-ranged/by-validator/v2?validator_id=ID&start_datetime=ISO&end_datetime=ISO&granularity={1h|1d}
```

### Verdicts (Private Transactions)

**Verdicts Stats**
```
GET /api/v1/verdicts-stat/ranged?start_datetime=ISO&end_datetime=ISO&granularity={1h|1d}
```

**Verdicts List**
```
GET /api/v1/verdicts/list/v2?limit=N
```

### Updates History

**Updates by Record Time**
```
GET /api/v1/update-history/by-record-time/v3?limit=N
```

**Updates by Party**
```
GET /api/v1/update-history/by-party-id/v3?party_id=PARTY_ID&limit=N
```

**Update Details**
```
GET /api/v1/update-by-event-id/v3?event_id=EVENT_ID
```

## Known Non-Working Endpoints (404 as of Mar 2026)

These return `{"error": "Proxy error", "details": "Request failed with status code 404"}`:
- `/api/v1/mining-round`
- `/api/v1/featured-apps/list/v2`
- `/api/v1/featured-apps/top-5/v2`
- `/api/v1/rewards/history`
- `/api/v1/validator/statistics`
- `/api/v1/governance/statistics`

Use alternatives: reward data from `/api/v1/rewards/daily_statistic`, validator data from `/api/v1/validator/performance-ranged`.

## Common Patterns

### Reward Per Transaction Calculation
```bash
# 1. Get reward data
curl "https://ccview.io/api/v1/rewards/daily_statistic?start=START&end=END&granularity=1d" \
  -H "x-api-key: $CCVIEW_API_KEY"

# 2. Get transfer counts for same period
curl "https://ccview.io/api/v2/token-transfers/stat-ranged?start_datetime=STARTT00:00:00Z&end_datetime=ENDT23:59:59Z&granularity=1d" \
  -H "x-api-key: $CCVIEW_API_KEY"

# 3. Divide: reward_per_tx = app_change_amount_per_day / transfers_count
```

### Convert CC to USD
```python
# Fetch current price
prices = requests.get("https://ccview.io/api/v1/explore/prices", headers={"x-api-key": API_KEY}).json()
cc_price_usd = float(prices["current"])
usd_value = cc_amount * cc_price_usd
```

### Pagination
Most `/v2` and `/v3` list endpoints support cursor-based pagination:
- `limit` — number of results per page
- Response includes a cursor/offset for the next page
- Check response for `next_cursor` or similar field

### Date Formats
- Date-only params: `YYYY-MM-DD` (e.g., `start=2026-03-11`)
- DateTime params: ISO 8601 with Z suffix (e.g., `start_datetime=2026-03-11T00:00:00Z`)
- Granularity: `1h` (hourly) or `1d` (daily)

## Example: Full Analytics Query (Python)
```python
import requests

API_KEY = "$CCVIEW_API_KEY"
HEADERS = {"x-api-key": API_KEY}
BASE = "https://ccview.io"

# Get 7-day reward + tx data
rewards = requests.get(f"{BASE}/api/v1/rewards/daily_statistic?start=2026-03-19&end=2026-03-26&granularity=1d", headers=HEADERS).json()
transfers = requests.get(f"{BASE}/api/v2/token-transfers/stat-ranged?start_datetime=2026-03-19T00:00:00Z&end_datetime=2026-03-26T00:00:00Z&granularity=1d", headers=HEADERS).json()
prices = requests.get(f"{BASE}/api/v1/explore/prices", headers=HEADERS).json()

# Build daily reward/tx
tx_by_day = {t["record_time"][:10]: t["transfers_count"] for t in transfers["series"]}
for r in rewards["data"]:
    day = r["day"]
    app_reward = float(r["app_change_amount_per_day"])
    txs = tx_by_day.get(day, 0)
    if txs > 0:
        rpt = app_reward / txs
        usd_rpt = rpt * float(prices["current"])
        print(f"{day}: {rpt:.1f} CC/tx (${usd_rpt:.2f}), {txs:,} txs, pool={app_reward/1e6:.1f}M CC")
```
