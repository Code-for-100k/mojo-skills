---
name: temple-canton-sdk
description: "Temple Canton JS SDK v2-beta for institutional trading on Canton Network — market data, orderbook, trading, deposits/withdrawals, WebSocket streaming, and onboarding. Use when: writing code that uses the Temple SDK or API, querying CC/USDCx or CBTC/USDCx market data, placing or canceling orders on Temple, checking trading balances, depositing or withdrawing funds, streaming live orderbook/ticker/trade data via WebSocket, onboarding users to Temple, or any development involving templedigitalgroup.com or @temple-digital-group/temple-canton-js. Trigger on: temple, temple SDK, temple API, temple trading, temple orderbook, CC/USDCx, CBTC/USDCx, temple deposit, temple withdraw, temple WebSocket, temple onboard, temple canton, temple market data."
---

# Temple Canton JS SDK — Development Guide

**Package:** `@temple-digital-group/temple-canton-js` v2.0.0-beta.7
**Project:** `/Users/mayank/Desktop/temple-sdk/`
**API Docs:** https://apidocs.templedigitalgroup.com/v2.0/reference/authentication-1
**npm:** https://www.npmjs.com/package/@temple-digital-group/temple-canton-js/v/2.0.0-beta.7

## Reference Files

| What | Where |
|------|-------|
| Working project + demo CLI | `/Users/mayank/Desktop/temple-sdk/` |
| SDK README (full API reference) | `/Users/mayank/Desktop/temple-sdk/node_modules/@temple-digital-group/temple-canton-js/README.md` |
| Demo script (all commands) | `/Users/mayank/Desktop/temple-sdk/index.js` |
| Environment config | `/Users/mayank/Desktop/temple-sdk/.env` |
| SDK source (config) | `/Users/mayank/Desktop/temple-sdk/node_modules/@temple-digital-group/temple-canton-js/src/config/index.js` |
| SDK source (REST API) | `/Users/mayank/Desktop/temple-sdk/node_modules/@temple-digital-group/temple-canton-js/dist/api/index.js` |
| SDK source (WebSocket) | `/Users/mayank/Desktop/temple-sdk/node_modules/@temple-digital-group/temple-canton-js/dist/websocket/index.js` |
| SDK source (Canton ops) | `/Users/mayank/Desktop/temple-sdk/node_modules/@temple-digital-group/temple-canton-js/src/canton/` |

---

## Setup

The SDK is already installed and working. ESM modules (`"type": "module"` in package.json).

```bash
cd /Users/mayank/Desktop/temple-sdk
npm start              # ticker
npm start -- orderbook # orderbook
npm start -- ws        # live WebSocket stream
```

### Environment (.env)

```
API_KEY=<temple-api-key>
NETWORK=testnet   # or mainnet
```

The account is registered under **mayank.eth@gmail.com** (verified, KYC complete). Current key is for **testnet**.

---

## Initialization

Always call `initialize()` before using any SDK function. API_KEY is required.

```javascript
import "dotenv/config";
import { initialize } from "@temple-digital-group/temple-canton-js";

initialize({
  API_KEY: process.env.API_KEY,
  NETWORK: process.env.NETWORK || "mainnet",
  // WALLET_ADAPTER: loop,  // Optional: pass Loop SDK instance for on-chain ops
});
```

For on-chain operations (deposits, withdrawals, onboarding, merging), a **wallet adapter** (Loop SDK) is required. Pass it as `WALLET_ADAPTER` in initialize or via `setWalletAdapter(loop)`.

---

## Supported Instruments & Pairs

| Asset | Type | Pairs |
|-------|------|-------|
| CC (Canton Coin) | Amulet | CC/USDCx |
| CBTC | Utility | CBTC/USDCx |
| USDCx | Utility | (quote currency) |

Use `CC` in all SDK methods — the SDK converts to `Amulet` internally where needed. The `Amulet` symbol is deprecated.

---

## REST API — Market Data

All market data functions require API_KEY auth. The SDK sends it as `X-API-Key` header.

```javascript
import {
  getTicker, getOrderBook, getRecentTrades,
  getOpenInterest, getSymbolConfig
} from "@temple-digital-group/temple-canton-js";

// Ticker (one or all pairs)
const ticker = await getTicker("CC/USDCx");
const allTickers = await getTicker();

// Orderbook (levels: number of price levels, precision: decimal places)
const book = await getOrderBook("CC/USDCx", { levels: 10 });

// Recent trades (limit: max 500)
const trades = await getRecentTrades("CC/USDCx", { limit: 20 });

// Open interest
const oi = await getOpenInterest("CC/USDCx");

// Symbol config (paused status, decimals, min quantity)
const cfg = await getSymbolConfig("CC/USDCx");
```

---

## REST API — Trading

```javascript
import {
  getTradingBalance, getActiveOrders,
  createOrderRequest, cancelOrder, cancelAllOrders,
  getDelegation
} from "@temple-digital-group/temple-canton-js";

// Check balance
const balance = await getTradingBalance();
// Returns { balances: [{ asset, unlocked, locked, in_flight, ... }] }

// Active orders
const orders = await getActiveOrders({ symbol: "CC/USDCx", limit: 50 });

// Place a single limit order
const result = await createOrderRequest({
  symbol: "CC/USDCx",
  side: "buy",        // "buy" or "sell"
  quantity: 10.5,
  price: 1.25,
  order_type: "limit",
  // expires_at: optional ISO timestamp
});

// Place batch orders (max 20)
const batch = await createOrderRequest([
  { symbol: "CC/USDCx", side: "buy", quantity: 100, price: 1.25, order_type: "limit" },
  { symbol: "CC/USDCx", side: "sell", quantity: 50, price: 1.50, order_type: "limit" },
]);
// Returns { success, request_ids, count, message }

// Cancel single or batch (max 20)
await cancelOrder("ord_abc123");
await cancelOrder(["ord_abc123", "ord_def456"]);
// Returns { success, canceled, already_queued, not_found, message }

// Cancel all (optionally filter by symbol)
await cancelAllOrders({ symbol: "CC/USDCx" });
await cancelAllOrders(); // all symbols

// Delegation status
const delegation = await getDelegation();
```

---

## REST API — Withdrawals

```javascript
import {
  createWithdrawalRequest, getWithdrawalRequestStatus
} from "@temple-digital-group/temple-canton-js";

const req = await createWithdrawalRequest("USDCx", "250.50");
const status = await getWithdrawalRequestStatus(req.request_id);
```

---

## On-Chain Operations (require Wallet Adapter)

These need a Loop SDK instance passed via `WALLET_ADAPTER` or `setWalletAdapter()`.

### Onboarding

```javascript
import { isUserOnboarded, onboardUser } from "@temple-digital-group/temple-canton-js";

const delegation = await isUserOnboarded(partyId);
if (!delegation) {
  const result = await onboardUser({ partyId });
  // result.delegation — confirmed delegation contract
  // result.warning — set if not confirmed within 60s
}
```

### Deposits

```javascript
import { deposit } from "@temple-digital-group/temple-canton-js";

// Simple: handles UTXO selection, fee reservation (10 CC), validation
await deposit(100, "USDCx");
await deposit(10, "CC");

// Low-level: prepareDepositHoldings + depositFunds
import { prepareDepositHoldings, depositFunds } from "@temple-digital-group/temple-canton-js";
const opts = await prepareDepositHoldings(100, "USDCx");
await depositFunds(opts);
```

### Withdrawals (on-chain)

```javascript
import { withdrawFunds, emergencyWithdrawFunds } from "@temple-digital-group/temple-canton-js";

// Withdraw available (unlocked, non-in-flight) balance to wallet
await withdrawFunds({ asset_id: "USDCx", amount: "250.50" });

// Emergency: cancel all orders + withdraw everything
await emergencyWithdrawFunds(opts);
```

### Withdraw Delegation

```javascript
import { withdrawDelegation } from "@temple-digital-group/temple-canton-js";
await withdrawDelegation(); // auto-fetches delegation
await withdrawDelegation(delegationContractId, partyId); // explicit
```

### Balances & Holdings

```javascript
import { getUserBalances, getUtxoCount } from "@temple-digital-group/temple-canton-js";

const balances = await getUserBalances(partyId);
// Each entry: { asset, total_balance, available_balance, locked_balance, merge_warning, holdings, ... }

const utxos = await getUtxoCount(partyId, "USDCx", walletProvider);
```

### Merge Holdings

```javascript
import {
  mergeAmuletHoldingsForParty, mergeUtilityHoldingsForParty,
  getAmuletDisclosures
} from "@temple-digital-group/temple-canton-js";

await mergeAmuletHoldingsForParty(partyId);
await mergeUtilityHoldingsForParty(partyId, "USDCx");

// With wallet provider (merge up to 5 smallest UTXOs)
const cmd = await mergeUtilityHoldingsForParty(partyId, "USDCx", true, walletProvider, 5);
await walletProvider.submitTransaction(cmd);
```

---

## WebSocket — Real-Time Data

Works in Node.js and browsers. Two types of data:
- **Market data** — public, requires explicit subscribe
- **User data** — auto-pushed after auth (API_KEY or cookie)

```javascript
import {
  subscribeOrderbook, subscribeTrades, subscribeTicker,
  subscribeCandles, subscribeOracle, subscribeOracleVolume,
  subscribeUserOrders, subscribeUserTrades, subscribeUserBalances,
  disconnectWebSocket
} from "@temple-digital-group/temple-canton-js";

// Market data channels (returns unsubscribe function)
const unsub = subscribeOrderbook("CC/USDCx", (data) => console.log(data));
subscribeTrades("CC/USDCx", (data) => console.log(data));
subscribeTicker("CC/USDCx", (data) => console.log(data));
subscribeCandles("CC/USDCx", 60, (data) => console.log(data));
// Candle granularity: 60 (1m), 300 (5m), 900 (15m), 3600 (1h), 14400 (4h), 86400 (1d)
subscribeOracle("cc", (data) => console.log(data));
subscribeOracleVolume("cc", (data) => console.log(data));

// User data (auto-pushed, no subscribe message)
subscribeUserOrders((data) => console.log(data));
subscribeUserTrades((data) => console.log(data));
subscribeUserBalances((data) => console.log(data));

// Cleanup
unsub();                 // single channel
disconnectWebSocket();   // everything
```

### Advanced WebSocket

```javascript
import { TempleWebSocket } from "@temple-digital-group/temple-canton-js";

const ws = new TempleWebSocket();
ws.onConnect = () => console.log("Connected");
ws.onDisconnect = (code, reason) => console.log("Disconnected:", code, reason);
ws.onAuth = (success, userId) => console.log("Auth:", success, userId);
ws.onError = (err) => console.error(err);
ws.autoReconnect = true; // default, exponential backoff
ws.connect();

const unsub = ws.subscribe("orderbook:Amulet/USDCx", (data) => { ... });
const unsubOrder = ws.onUserEvent("user_order", (data) => { ... });
```

---

## Network Configuration

The SDK auto-resolves URLs and contract IDs based on `NETWORK`:

| Network | REST API | WebSocket |
|---------|----------|-----------|
| mainnet | `https://api.templedigitalgroup.com` | `wss://ws.templedigitalgroup.com/v1/stream` |
| testnet | `https://api-testnet.templedigitalgroup.com` | `wss://ws-dev.templedigitalgroup.com/v1/stream` |

Hardcoded contract IDs (orchestrator, featured app, disclosures) are resolved per-network automatically.

---

## Authentication

Two methods:

1. **API Key** (recommended) — long-lived, set via `initialize({ API_KEY })`, sent as `X-API-Key` header
2. **JWT Bearer Token** — `POST /auth/login` with credentials, expires 30 min, refresh via `POST /auth/refresh`

API key takes precedence when both are present.

---

## Error Handling

All REST functions return `{ error: true, status, code, message }` on failure instead of throwing. Check for the `error` field:

```javascript
const result = await getTicker("CC/USDCx");
if (result.error) {
  console.error(`API error: ${result.message} (HTTP ${result.status})`);
} else {
  console.log(result.ticker);
}
```

---

## v2 Trading Flow (Full Lifecycle)

```
1. Check onboarding   →  isUserOnboarded(party)
   If NOT onboarded   →  onboardUser(party)
2. Deposit funds      →  deposit(amount, symbol)
3. Check balance      →  getTradingBalance()
4. Place orders       →  createOrderRequest({ symbol, side, quantity, price })
5. Cancel orders      →  cancelOrder(orderId) or cancelAllOrders({ symbol })
6. Withdraw funds     →  withdrawFunds({ asset_id, amount })
7. Withdraw delegation → withdrawDelegation()
```

---

## Gotchas & Tips

- **Symbol normalization**: Always use `CC`, never `Amulet`. The SDK converts internally.
- **Fee reserve**: Deposits require at least 10 CC reserved for transaction fees.
- **Batch limits**: Max 20 orders per `createOrderRequest` batch, max 20 IDs per `cancelOrder` batch.
- **Trade limit**: `getRecentTrades` max 500.
- **WebSocket user data**: No subscribe message needed — just register handlers. Auto-pushed after auth.
- **Testnet vs Mainnet**: Current setup is **testnet**. Switch `NETWORK=mainnet` in `.env` for production.
- **ESM only**: Package uses `"type": "module"`. Use `import` not `require`.
