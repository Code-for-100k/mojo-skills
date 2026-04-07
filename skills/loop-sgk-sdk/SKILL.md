---
name: loop-sgk-sdk
description: "Loop Wallet (Five North) SDK and Splice Wallet Kernel (SGK) for Canton Network dApp and wallet development. Use when: writing code that uses Loop SDK or SGK, connecting dApps to Loop Wallet, building Canton wallet integrations, submitting DAML transactions via Loop, querying holdings or active contracts, signing messages, estimating gas, building with @fivenorth/loop-sdk or @canton-network/wallet-sdk or @canton-network/dapp-sdk, implementing CIP-103 wallet connections, or any development involving fivenorth.io or splice-wallet-kernel. Trigger on: loop sdk, loop wallet, five north, fivenorth, splice wallet kernel, SGK, canton wallet sdk, dapp sdk, canton-network/wallet-sdk, canton-network/dapp-sdk, CIP-103, wallet connection, DAML transaction, getHolding, getActiveContracts, submitTransaction, signMessage, estimateGas, loop connect, loop provider."
---

# Loop SDK & Splice Wallet Kernel (SGK) — Development Guide

## Quick Reference

| What | Where |
|------|-------|
| Loop SDK Docs | https://docs.fivenorth.io/loop-sdk/overview/ |
| Loop API Reference | https://docs.fivenorth.io/loop-sdk/api-reference/ |
| Loop GitHub | https://github.com/fivenorth-io/loop-sdk |
| Loop npm | `@fivenorth/loop-sdk` (install via `bun add` or `npm install`) |
| SGK GitHub | https://github.com/hyperledger-labs/splice-wallet-kernel |
| SGK Wallet SDK | `@canton-network/wallet-sdk` |
| SGK dApp SDK | `@canton-network/dapp-sdk` |
| DA Integration Docs | https://docs.digitalasset.com/integrate/devnet/index.html |
| Splice Docs | https://hyperledger-labs.github.io/splice/index.html |

---

## Part 1: Loop SDK (Five North)

Lightweight JavaScript client for dApps to connect to Loop Wallet on Canton Network.

### Installation

```bash
# Browser dApp
bun add @fivenorth/loop-sdk
# or
npm install @fivenorth/loop-sdk

# Server-side (also needs node-forge)
npm install @fivenorth/loop-sdk node-forge
```

### Networks

| Network | Use |
|---------|-----|
| `local` | Local development |
| `devnet` | Testing |
| `mainnet` | Production |

### CRITICAL Limitation
Loop SDK **only supports DAML transactions from Splice built-in DAR files and Utility app DAR files**. Third-party DAR file uploads are NOT supported and are NOT planned.

### Supported DAR Packages (13 total)
Collateral apps, commercials, bridge applications, credential systems, hosting, registry operations, settlement functions, and other Splice utility packages.

---

### Browser Client Usage

#### 1. Initialize

```typescript
import loop from '@fivenorth/loop-sdk';

loop.init({
  appName: 'My dApp',
  network: 'mainnet', // 'local' | 'devnet' | 'mainnet'
  // Optional overrides:
  // walletUrl: 'https://custom-wallet.example.com',
  // apiUrl: 'https://custom-api.example.com',
  options: {
    openMode: 'popup',        // how wallet UI opens
    requestSigningMode: 'auto' // signing behavior
    // redirectUrl: 'https://...' // for redirect flows
  },
  onAccept: (provider) => {
    // User approved connection — provider is now available
    console.log('Connected:', provider.party_id);
  },
  onReject: () => {
    console.log('User rejected connection');
  },
  onTransactionUpdate: (update) => {
    // Receives: { command_id, submission_id, update_id, update_data }
    console.log('Tx update:', update);
  }
});
```

#### 2. Connect / Auto-Connect

```typescript
// Full connection flow (QR code, websocket, etc.)
loop.connect();

// Silent reconnect if session is still valid
loop.autoConnect();

// Check session without connecting
const session = loop.verifySession(); // returns session or null

// Logout
loop.logout();
```

#### 3. Provider API (after connection)

The `provider` object is received in `onAccept`. Properties:
- `provider.party_id` — Canton party ID (string)
- `provider.public_key` — User's public key (string)
- `provider.email` — User's email (string)

#### 4. Get Holdings

```typescript
const holdings = await provider.getHolding();
// Returns: Holding[]
// Each: { instrument_id: { admin, id }, decimals, symbol, org_name,
//         total_unlocked_coin, total_locked_coin, image }
```

#### 5. Get Active Contracts

```typescript
// By template ID
const contracts = await provider.getActiveContracts({
  templateId: 'ModuleName:TemplateName'
});

// By interface ID
const contracts = await provider.getActiveContracts({
  interfaceId: 'ModuleName:InterfaceName'
});
// Returns: ActiveContract[] — each has template_id, contract_id, and payload fields
```

#### 6. Submit Transactions

```typescript
// Async (returns immediately, update via onTransactionUpdate callback)
const result = await provider.submitTransaction(
  damlCommand, // ExerciseCommand or multi-command
  {
    estimateTraffic: true,       // optional: pre-estimate gas
    deduplicationPeriod: '30s'   // optional: dedup window
  }
);

// Blocking (waits for ledger confirmation)
const result = await provider.submitAndWaitForTransaction(
  damlCommand,
  { execution_mode: 'wait' }
);
```

#### 7. Transfer Tokens

```typescript
await provider.transfer(
  recipientPartyId,   // Canton party ID
  '10.5',             // amount as string
  'Amulet',           // instrument: 'Amulet' | 'CC' | 'CIP-56' | custom
  {
    memo: 'Payment for services',
    message: 'Thanks!',
    execution_mode: 'wait',          // optional
    deduplicationPeriod: '60s'       // optional
  }
);
```

#### 8. Sign Messages

```typescript
const signature = await provider.signMessage('Arbitrary message to sign');
```

#### 9. Estimate Gas

```typescript
const gasEstimate = await provider.estimateGas(transactionPayload);
// Returns: EstimatedGasResponse
```

#### 10. Get Account Info

```typescript
const accounts = await provider.getAccount();
// Returns: Account[] — includes pre-approval and merge contract status
```

#### 11. Get Auth Token

```typescript
const token = provider.getAuthToken();
// Use for authenticated backend API calls
```

---

### Server-Side Usage

For backend services that need to submit transactions without wallet UI popups. **Requires access to user's private key.**

```typescript
import loop from '@fivenorth/loop-sdk/server';

// Initialize with private key
loop.init({
  network: 'mainnet',
  privateKey: process.env.CANTON_PRIVATE_KEY
});

// Estimate gas
const gas = await loop.estimateGas(payload);

// Check pending gas
const pending = await loop.checkDueGas(trackingId);

// Pay gas
await loop.payGas(trackingId);
```

**Security Warning:** Browser dApps should NEVER handle private keys directly. Server-side only.

---

### Types Reference

```typescript
type Network = 'local' | 'devnet' | 'mainnet';

type Account = {
  party_id: string;
  auth_token: string;
  public_key: string;
};

type InstrumentId = {
  admin: string;
  id: string;
};

type Holding = {
  instrument_id: InstrumentId;
  decimals: number;
  symbol: string;
  org_name: string;
  total_unlocked_coin: string;
  total_locked_coin: string;
  image: string;
};

type ActiveContract = {
  template_id: string;
  contract_id: string;
  [key: string]: any;
};

type RunTransactionResponse = {
  command_id: string;
  submission_id: string;
  update_id: string;
  update_data: any;
};
```

---

## Part 2: Splice Wallet Kernel (SGK)

Full TypeScript framework implementing CIP-103 for Canton Network wallet integrations.

### Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   dApp      │────>│  Wallet Gateway  │────>│  Canton Participant  │
│ (dApp SDK)  │     │  (middleware)     │     │  Node               │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                           │
                    ┌──────┴───────┐
                    │  Wallet SDK  │
                    │  (direct)    │
                    └──────────────┘
```

### Components

| Package | npm | Purpose |
|---------|-----|---------|
| **dApp SDK** | `@canton-network/dapp-sdk` | JSON-RPC 2.0 (CIP-103), EIP-1193 provider, multi-transport |
| **Wallet SDK** | `@canton-network/wallet-sdk` | Direct Canton integration, party allocation, contract read/write |
| **Wallet Gateway** | (server binary) | Server + browser extension middleware |
| **Core modules** | 20+ internal packages | Stores, signing, RPC, auth |

### Signing Drivers

| Driver | Use Case |
|--------|----------|
| Internal Ed25519 | Development / testing |
| Canton participant-managed | Delegated signing |
| Fireblocks | Institutional custody |
| Blockdaemon | Institutional custody |

### Requirements

- Node.js 20+
- Yarn 4 with Corepack
- Running Canton participant node

### Setup

```bash
git clone https://github.com/hyperledger-labs/splice-wallet-kernel.git
cd splice-wallet-kernel
corepack enable
yarn install
yarn build
```

### dApp SDK Usage (CIP-103)

```typescript
import { createProvider } from '@canton-network/dapp-sdk';

// Create provider (EIP-1193 style)
const provider = createProvider({
  transport: 'http', // or 'postMessage' for browser extensions
  url: 'https://wallet-gateway.example.com'
});

// Request connection
const accounts = await provider.request({
  method: 'canton_requestAccounts'
});

// Get holdings
const holdings = await provider.request({
  method: 'canton_getHoldings',
  params: { partyId: accounts[0] }
});

// Submit transaction
const txResult = await provider.request({
  method: 'canton_submitTransaction',
  params: { command: damlCommand }
});
```

### Wallet SDK Usage (Direct)

```typescript
import { WalletClient } from '@canton-network/wallet-sdk';

const client = new WalletClient({
  participantUrl: 'https://participant.example.com',
  signingDriver: 'ed25519' // or 'fireblocks', 'blockdaemon'
});

// Allocate party
const party = await client.allocateParty({ displayName: 'My Party' });

// Read contracts
const contracts = await client.getActiveContracts({
  templateId: 'Splice.Amulet:Amulet'
});

// Sign and submit transaction
await client.submitTransaction(command);
```

---

## When to Use Which SDK

| Scenario | Use |
|----------|-----|
| Building a browser dApp that connects to Loop Wallet | **Loop SDK** (browser client) |
| Backend service submitting Canton transactions | **Loop SDK** (server) or **SGK Wallet SDK** |
| Building a new wallet or wallet gateway | **SGK** (full framework) |
| Implementing CIP-103 wallet standard | **SGK dApp SDK** |
| Institutional custody with Fireblocks/Blockdaemon | **SGK** (signing drivers) |
| Quick dApp with wallet connection popup | **Loop SDK** (simplest path) |
| Custom DAML contract interactions beyond Splice DARs | **SGK Wallet SDK** (Loop SDK doesn't support custom DARs) |

---

## Common Gotchas

1. **Loop SDK DAR limitation**: Only Splice built-in DARs work. If you need custom DAML contracts, use SGK.
2. **Loop npm 403**: The npm web page returns 403, but `npm install @fivenorth/loop-sdk` works fine.
3. **SGK requires Node 20+**: Won't work on older Node versions.
4. **SGK uses Yarn 4**: Must enable Corepack first (`corepack enable`).
5. **Private keys in browser**: NEVER. Use server-side Loop SDK or SGK for private key operations.
6. **Network naming**: Loop uses `'mainnet'`, SGK may use participant URLs directly.
7. **Gas estimation**: Always estimate before large transactions to avoid failures.

---

## Related Resources

| Resource | URL |
|----------|-----|
| Splice main repo | https://github.com/hyperledger-labs/splice |
| Splice docs | https://hyperledger-labs.github.io/splice/index.html |
| Global Synchronizer | https://docs.dev.sync.global/overview/overview.html |
| splice-wallet Daml models | https://docs.dev.global.canton.network.sync.global/app_dev/api/splice-wallet/index.html |
| SGK Releases | https://github.com/hyperledger-labs/splice-wallet-kernel/releases |
| DA Integration Docs | https://docs.digitalasset.com/integrate/devnet/index.html |
| Canton Whitepapers | https://www.canton.network/whitepapers |
