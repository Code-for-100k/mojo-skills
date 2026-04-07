---
name: zoro-wallet-api
description: "Zoro Wallet Canton API for on-chain wallet operations — sending CC/CBTC, checking balances, onboarding parties, managing transfers, and building Canton-based applications. Use when: writing code that interacts with the Zoro API, building wallet features, sending tokens, onboarding new parties, checking balances, managing pending transfers, debugging Canton transaction flows, or any development involving dev-api.zorowallet.com. Trigger on: zoro, canton send, wallet API, party onboard, CC transfer, CBTC transfer, canton transaction, wallet balance, transfer pre-approval, Ed25519 signing, canton broadcast."
---

# Zoro Wallet API — Development Guide

**Base URL:** `https://dev-api.zorowallet.com` (Canton **mainnet** despite "dev" prefix — real CC/CBTC)
**Auth:** `Authorization: Bearer canton_-KPOgjYXFL_DoI-S3wMhFCIbxaElqbjVJxUc69T7wbI`
**All endpoints are POST** with `Content-Type: application/json`.

## Reference Files

| What | Where |
|------|-------|
| Working project + examples | `/Users/mayank/Clawed/Using Zoro/` |
| Primary codebase | `/Users/mayank/Clawed/canton-send/` |
| Full API docs (15 endpoints) | `/Users/mayank/Clawed/Using Zoro/docs/Zoro_API_Documentation.md` |
| Credentials + scripts + gotchas | `/Users/mayank/Clawed/Using Zoro/docs/ZORO_AI_INSTRUCTIONS.md` |
| Wallet index (all 8 wallets) | `/Users/mayank/Clawed/Using Zoro/WALLET_INDEX.md` |
| Gas cost analysis | `/Users/mayank/Clawed/Using Zoro/GAS_COST_EXPLAINER.md` |
| Fees API bug report | `/Users/mayank/Clawed/Using Zoro/FEES_API_DIAGNOSIS.md` |
| Zoro Wallet SDK (ClickUp) | https://doc.clickup.com/9002019994/d/h/8c8zv4u-35836/2d80c79130e59b6 |
| CCView API (requires key) | https://docs.ccview.io/reference/general_search |

---

## Wallets

| Wallet | Party ID | Type | Env Vars | Keys In |
|--------|----------|------|----------|---------|
| **Retail Pool** | `8324e2529b::1220efd7...c76d37` | Retail (default sender, fee operator) | `SENDER_PARTY_ID`, `POOL_PARTY_ID`, `OPERATOR_PARTY_ID` | canton-send + predict-now `.env` |
| **Mayank App** | `237268376e::122034...36f43` | Personal (no private key in code) | Hardcoded as `DEFAULT_RECEIVER` | N/A (Zoro app) |
| **Inst Pool 1** | `0afed9241a::1220320c...e2825` | Institutional | `INSTITUTIONAL_POOL_PARTY_ID`, `POOL_INST1_PARTY_ID` | predict-now `.env` |
| **Inst Pool 2** | `394df865bf::122058ec...257a1` | Institutional | `POOL_INST2_PARTY_ID` | predict-now `.env` |
| **Inst Pool 3** | `702758b398::12205271...ba2f` | Institutional | `POOL_INST3_PARTY_ID` | predict-now `.env` |
| **Agent 1** | `df0c3fdb58::12200a97...ea94` | AI trading bot | `PARTY_ID_1` | canton-send `.env` |
| **Agent 2** | `689e91029e::12202e73...d0bc` | AI trading bot | `PARTY_ID_2` | canton-send `.env` |
| **Agent 3** | `1ca79f9918::12206e3a...f16d` | AI trading bot | `PARTY_ID_3` | canton-send `.env` |

**Instruments:**
- CC: `{ id: "Amulet", admin: "DSO::1220b1431ef217342db44d516bb9befde802be7d8899637d290895fa58880f19accc" }`
- CBTC: `{ id: "CBTC", admin: "cbtc-network::12205af3b949a04776fc48cdcc05a060f6bda2e470632935f375d1049a8546a3b262" }`

---

## API Endpoints

### Read-Only

**Balance:** `POST /canton/wallet/balance` — `{ "partyId": "..." }`
Response uses `balances` dict (NOT `instruments` array): `{ "balances": { "Amulet": "803.4", "CBTC": "0.0006" }, "balance": "803.4" }`

**Pending:** `POST /canton/transaction/history/pending` — `{ "partyId": "..." }`
Returns `{ count, transactions[] }` with `contractId`, `amount`, `sender`, `receiver`, `instrumentId`, `status`. Includes expired transfers — filter client-side.

**Full History (undocumented):** `POST /canton/transaction/history` — `{ "partyId": "...", "offset": <number> }`
Returns ALL transactions (CC, CBTC, gas payments). Paginated via `{ count, hasMore, nextOffset }`. **Only way to see actual gas costs.** Also: `/canton/transaction/history/completed`.
Pagination bug: `nextOffset` can equal previous offset — break the loop if so.

**Pre-Approval Status:** `POST /canton/wallet/transfer-preapproval-status` — `{ "partyId": "...", "instrument": {...} }`
Returns just `{ "partyId": "..." }` when pre-approved (no `isPreApproved` field).

### Transaction Pattern (prepare → sign → broadcast)

All writes follow: prepare → Ed25519-sign `preparedTransactionHash` → broadcast.

```
1. POST /canton/transaction/prepare/<action>  →  { commandId, command: { preparedTransaction, preparedTransactionHash, hashingSchemeVersion } }
2. signHash(preparedTransactionHash, privateKey)  →  signature (base64)
3. POST /canton/transaction/broadcast  →  { signature, publicKey, preparedTransaction: { commandId, command }, partyId }
```

**Signing** uses `@noble/ed25519` v2 — see `canton-send/src/lib/sign.ts`. Must set `ed.etc.sha512Sync = sha512`.

### Write Endpoints

| Endpoint | Body | Notes |
|----------|------|-------|
| `prepare/send` | `{ senderPartyId, receiverPartyId, amount, expiryDate, instrument, registryChoiceContext? }` | Set expiry 24h out |
| `prepare/accept` | `{ partyId, transferContractId, instrument }` | Fails on zero-UTXO wallets |
| `prepare/reject` | `{ partyId, transferContractId, instrument? }` | |
| `prepare/withdraw` | `{ partyId, transferContractId, instrument? }` | Sender cancels pending transfer |
| `prepare/transfer-preapproval` | `{ partyId, instrument }` | Per-instrument, no revoke API |
| `prepare/merge-delegation-proposal` | `{ partyId }` | Required before pre-approval |
| `prepare/bulk-send` | `{ partyId, receivers[{recipient, amount, memo?, expiryDate?}], instrument }` | 1-50 recipients |
| `prepare/submission` | `{ partyId, instrument?, command, disclosedContracts }` | Generic |
| `choice-context` | `{ senderPartyId, receiverPartyId, amount, expiryDate, instrument }` | Optional cache for sends |

**Onboarding** is different: signs `multiHash` (not `preparedTransactionHash`), uses `broadcast/external-party` (not `broadcast`), body is `{ signature, preparedParty: {...} }`.

---

## Gas & Fees

| Operation | CC Cost | Notes |
|-----------|---------|-------|
| CC send | 0 CC | Free |
| CBTC send | ~2.47 CC avg (1.85-3.02 range) | Measured across 50 ops |
| Pre-approval / Onboarding | 0 CC | |

**UPDATE (2026-04):** The `feesApplied` field is now returned in `/canton/transaction/prepare/send` responses:
```json
{
  "commandId": "bulk-696b4715-...",
  "command": { "preparedTransaction": "...", "preparedTransactionHash": "...", ... },
  "feesApplied": "3.01259264"
}
```
**Use `feesApplied` as the authoritative gas cost per transaction.** It's calculated retroactively from the last two mining rounds. The old `fees` field in transaction history still returns 0 — ignore it.

**Fallback method** (if `feesApplied` is missing/0): gas appears as CC TransferOut records in `/canton/transaction/history` paired by timestamp with CBTC events. Sender always pays. Fee is non-refundable.

**Typical fee:** ~3 CC per CBTC send.

---

## Critical Gotchas

1. **This is mainnet** — "dev" = Zoro API in beta, NOT a test network. Real money.
2. **Rate limit:** 0.5 TPS — wait >=2s between transactions.
3. **Zero-UTXO wallets can't accept transfers** — `prepare/accept` fails with `"No input utxos found for instrument Amulet"`. Fix: set up pre-approval first, then send. Existing pending transfers must be withdrawn by sender and re-sent.
4. **Pre-approval is per-instrument** — CC pre-approval does NOT cover CBTC. Run separately.
5. **CBTC gas comes from CC balance** — low CC = CBTC send fails.
6. **Never re-use commandId** — always sign/broadcast the most recent prepare response.
7. **Expiry date** — set 24h from now. Expired prepared transactions fail on broadcast.
8. **Balance API** returns `balances` dict, not `instruments[]` array. Types.ts is stale.
9. **Party IDs are 71-245 chars** — validate before API calls.
10. **Ed25519 keys** — base64-encoded 32-byte values. API key must start with `canton_`.

## New Party Setup

```bash
cd /Users/mayank/Clawed/canton-send
npx tsx src/onboard.ts              # 1. Generate keys, register party
npx tsx src/setup-party.ts          # 2. Merge delegation + CC pre-approval
npx tsx src/preapprove-cbtc.ts      # 3. CBTC pre-approval (optional)
# 4. Fund with CC, then: npx tsx src/balance.ts
```

## Existing Code

| File | Purpose |
|------|---------|
| `src/lib/api.ts` | All API calls (typed, logged) |
| `src/lib/sign.ts` | Ed25519 signing |
| `src/lib/config.ts` | `.env` loader (supports `SENDER_*` and `POOL_*`) |
| `src/lib/types.ts` | TypeScript interfaces (balance response is stale) |
| `agents/src/canton-client.ts` | `CantonClient` class — self-contained agent wrapper |
| `src/send.ts` / `send-cbtc.ts` | Send CC / CBTC |
| `src/balance.ts` / `src/pending.ts` | Check balance / pending transfers |
| `src/onboard.ts` / `src/setup-party.ts` | Party creation and setup |
