#!/usr/bin/env python3
"""CBTC Activity Tracker Dashboard — Zoro Wallet Overview"""

import json
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

BASE_URL = "https://cbtc-data-api.bitsafe.finance"

# ── Named Wallets (original 5) ──────────────────────────────────────────────
NAMED_WALLETS = {
    "Retail Pool": "8324e2529b::1220efd7374bb65d1ce76f9cf6cfa7f4e9fd896179980d624485978ed0cf46c76d37",
    "INST-ALPHA":  "0afed9241a::1220320c5994fd50d10e15a687d336acf65d0ba07f94744d16d68291ac8bb65e2825",
    "INST-BETA":   "394df865bf::122058ec34c21cd7707c60c31b0ca721944612b2deb5fa59aeda8a62a06d824257a1",
    "INST-GAMMA":  "702758b398::12205271e3242c223dcbf092f3012f54265930c2a2eb465dbd45315d64a34bcfba2f",
    "Mayank":      "237268376e::122034217581211f6d9fca5ef447aba2cb9302608dedb336a1f58339178a4cc36f43",
}

# ── Batch Wallets (loaded from wallets-batch.json) ───────────────────────────
BATCH_WALLET_PATH = "/Users/mayank/Clawed/predict-now/wallets-batch.json"

def _load_batch_wallets() -> dict:
    """Load batch wallets and return {label: partyId} dict."""
    if not os.path.exists(BATCH_WALLET_PATH):
        return {}
    with open(BATCH_WALLET_PATH) as f:
        batch = json.load(f)
    return {f"Batch-{w['index']:02d}": w["partyId"] for w in batch}

BATCH_WALLETS = _load_batch_wallets()

# ── Combined ─────────────────────────────────────────────────────────────────
WALLETS = {**NAMED_WALLETS, **BATCH_WALLETS}
ALL_PARTY_IDS = list(WALLETS.values())

# ── API Client ───────────────────────────────────────────────────────────────
TIMEOUT = 120  # some endpoints are slow

def _post(path: str, body: dict):
    r = requests.post(f"{BASE_URL}{path}", json=body, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"API error on {path}: {data.get('error', 'unknown')}")
    return data["data"]


def health() -> str:
    r = requests.get(f"{BASE_URL}/health", timeout=10).json()
    return r.get("data") or r.get("status", "unknown")


def transfer_offers(
    sender: Optional[list] = None,
    receiver: Optional[list] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consumed_by=None,
    limit: int = 100,
) -> list:
    body = {"instrument_id": "CBTC", "limit": limit}
    if sender:
        body["sender"] = sender
    if receiver:
        body["receiver"] = receiver
    if start_date:
        body["start_date"] = start_date
    if end_date:
        body["end_date"] = end_date
    if consumed_by is not None:
        body["consumed_by"] = consumed_by
    return _post("/api/v1/events/transfer-offers", body)


def transfer_offers_count(**kwargs) -> int:
    body = {"instrument_id": "CBTC"}
    for k in ("sender", "receiver", "start_date", "end_date", "consumed_by"):
        if k in kwargs and kwargs[k] is not None:
            body[k] = kwargs[k]
    return _post("/api/v1/events/transfer-offers/count", body)


def reward_coupons(
    sender: Optional[list] = None,
    receiver: Optional[list] = None,
    creation_start_date: Optional[str] = None,
    creation_end_date: Optional[str] = None,
    limit: int = 100,
) -> list:
    body = {"instrument_id": "CBTC", "limit": limit}
    if sender:
        body["sender"] = sender
    if receiver:
        body["receiver"] = receiver
    if creation_start_date:
        body["creation_start_date"] = creation_start_date
    if creation_end_date:
        body["creation_end_date"] = creation_end_date
    return _post("/api/v1/events/reward-coupons", body)


def transfer_reward_aggregation(parties: list, start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/transfer-reward-aggregation", {
        "parties": parties,
        "start_date": start_date,
        "end_date": end_date,
    })


def daily_rewards(parties: list, start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/daily-rewards", {
        "parties": parties,
        "start_date": start_date,
        "end_date": end_date,
    })


def daily_count(start_date: Optional[str] = None, end_date: Optional[str] = None, choice=None) -> dict:
    body = {}
    if start_date:
        body["start_date"] = start_date
    if end_date:
        body["end_date"] = end_date
    if choice is not None:
        body["choice"] = choice
    return _post("/api/v1/analytics/transfer-offers/daily-count", body)


def daily_unique_senders(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    body = {}
    if start_date:
        body["start_date"] = start_date
    if end_date:
        body["end_date"] = end_date
    return _post("/api/v1/analytics/transfer-offers/daily-unique-senders", body)


def daily_volume(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    body = {}
    if start_date:
        body["start_date"] = start_date
    if end_date:
        body["end_date"] = end_date
    return _post("/api/v1/analytics/transfer-offers/daily-volume", body)


def unique_holders(start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/cbtc-unique-holders", {
        "start_date": start_date,
        "end_date": end_date,
    })


def party_balances(parties: list, start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/cbtc-party-balances", {
        "parties": parties,
        "start_date": start_date,
        "end_date": end_date,
    })


def trailing_avg_balance(parties: list, start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/cbtc-trailing-avg-balance", {
        "parties": parties,
        "start_date": start_date,
        "end_date": end_date,
    })


def tier_eligibility(threshold: str, start_date: Optional[str] = None, end_date: Optional[str] = None, date: Optional[str] = None) -> dict:
    body = {"threshold": threshold}
    if date:
        body["date"] = date
    if start_date:
        body["start_date"] = start_date
    if end_date:
        body["end_date"] = end_date
    return _post("/api/v1/analytics/cbtc-tier-eligibility", body)


def balance_distribution(start_date: str, end_date: str) -> dict:
    return _post("/api/v1/analytics/cbtc-balance-distribution", {
        "start_date": start_date,
        "end_date": end_date,
    })


# ── Dashboard ────────────────────────────────────────────────────────────────
def _label(party_id: str) -> str:
    for name, pid in WALLETS.items():
        if pid == party_id:
            return name
    return party_id[:20] + "..."


def _hr(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def run_dashboard():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    # ── Health ──
    print(f"API Status: {health()}")

    named_ids = list(NAMED_WALLETS.values())
    batch_ids = list(BATCH_WALLETS.values())

    # ── Wallet Balances (today) ──
    _hr(f"WALLET BALANCES — {len(WALLETS)} wallets (today)")
    try:
        # API max 100 parties — we have 50, fine
        result = party_balances(ALL_PARTY_IDS, today, today)
        bals = result.get("balances", []) if isinstance(result, dict) else result
        date_shown = today
        if not bals:
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
            result = party_balances(ALL_PARTY_IDS, yesterday, yesterday)
            bals = result.get("balances", []) if isinstance(result, dict) else result
            date_shown = yesterday
            if bals:
                print(f"  (showing {yesterday})")
        if bals:
            bal_map = {e["party"]: float(e["balance"]) for e in bals}
            # Named wallets — show individually
            print("  ── Named Wallets ──")
            for name, pid in NAMED_WALLETS.items():
                b = bal_map.get(pid, 0.0)
                print(f"  {name:15s}  {b:>14.8f} CBTC")
            # Batch wallets — summary
            batch_bals = [bal_map.get(pid, 0.0) for pid in batch_ids]
            nonzero = [b for b in batch_bals if b > 0]
            print(f"  ── Batch Wallets ({len(batch_ids)} total) ──")
            print(f"  With balance:     {len(nonzero):>5} / {len(batch_ids)}")
            print(f"  Total held:       {sum(batch_bals):>14.8f} CBTC")
            if nonzero:
                print(f"  Max balance:      {max(nonzero):>14.8f} CBTC")
                print(f"  Min (non-zero):   {min(nonzero):>14.8f} CBTC")
        else:
            print("  No balance data available")
    except Exception as e:
        print(f"  Error: {e}")

    # ── Transfer Activity (last 7 days) ──
    _hr("TRANSFER ACTIVITY (last 7 days)")
    # Named wallets — individual
    for name, pid in NAMED_WALLETS.items():
        try:
            total = transfer_offers_count(sender=[pid], start_date=week_ago, end_date=today)
            accepted = transfer_offers_count(
                sender=[pid], start_date=week_ago, end_date=today,
                consumed_by="TransferInstruction_Accept",
            )
            print(f"  {name:15s}  sent: {total:>5}   accepted: {accepted:>5}")
        except Exception as e:
            print(f"  {name:15s}  Error: {e}")
    # Batch wallets — aggregate
    try:
        batch_total = transfer_offers_count(sender=batch_ids, start_date=week_ago, end_date=today)
        batch_accepted = transfer_offers_count(
            sender=batch_ids, start_date=week_ago, end_date=today,
            consumed_by="TransferInstruction_Accept",
        )
        print(f"  {'Batch (all 45)':15s}  sent: {batch_total:>5}   accepted: {batch_accepted:>5}")
    except Exception as e:
        print(f"  {'Batch (all 45)':15s}  Error: {e}")

    # ── Reward Aggregation (last 30 days) ──
    _hr("REWARD SUMMARY (last 30 days)")
    # Retail Pool
    try:
        agg = transfer_reward_aggregation([NAMED_WALLETS["Retail Pool"]], month_ago, today)
        print(f"  ── Retail Pool ──")
        print(f"  Total offers:     {agg.get('total_transfer_offers', 0)}")
        print(f"  Accepted:         {agg.get('accepted_transfer_offers', 0)}")
        print(f"  Total CC reward:  {agg.get('total_cc_reward', '0')}")
        print(f"  Reward/tx:        {agg.get('reward_per_tx', '0')}")
    except Exception as e:
        print(f"  Retail Pool error: {e}")
    # Batch wallets
    try:
        agg_b = transfer_reward_aggregation(batch_ids, month_ago, today)
        print(f"  ── Batch Wallets (45) ──")
        print(f"  Total offers:     {agg_b.get('total_transfer_offers', 0)}")
        print(f"  Accepted:         {agg_b.get('accepted_transfer_offers', 0)}")
        print(f"  Total CC reward:  {agg_b.get('total_cc_reward', '0')}")
        print(f"  Reward/tx:        {agg_b.get('reward_per_tx', '0')}")
    except Exception as e:
        print(f"  Batch error: {e}")

    # ── Daily Rewards (last 7 days — all wallets) ──
    _hr("DAILY REWARDS (last 7 days — all wallets)")
    try:
        dr = daily_rewards(ALL_PARTY_IDS, week_ago, today)
        if dr.get("daily_rewards"):
            print(f"  {'Date':<12} {'Accepted':>8} {'Total Reward':>14} {'Client Reward':>14}")
            print(f"  {'─' * 50}")
            for d in dr["daily_rewards"]:
                print(f"  {d['date']:<12} {d['accepted_transfer_count']:>8} {d['total_reward']:>14} {d['client_reward']:>14}")
            print(f"  {'─' * 50}")
            print(f"  Total accepted: {dr.get('total_accepted_transfer_count', 0)}")
            print(f"  Total reward:   {dr.get('total_estimated_reward', dr.get('total_reward', '0'))}")
            print(f"  Client reward:  {dr.get('client_reward', dr.get('total_client_reward', '0'))}")
        else:
            print("  No reward data for this period")
    except Exception as e:
        print(f"  Error: {e}")

    # ── Network-wide Daily Metrics (last 7 days) ──
    _hr("NETWORK DAILY METRICS (last 7 days)")
    try:
        counts = daily_count(start_date=week_ago, end_date=today, choice="TransferInstruction_Accept")
        volumes = daily_volume(start_date=week_ago, end_date=today)
        senders = daily_unique_senders(start_date=week_ago, end_date=today)

        count_map = {c["day"]: c["transfer_count"] for c in counts.get("daily_counts", [])}
        vol_map = {v["day"]: v["transfer_volume"] for v in volumes.get("daily_volumes", [])}
        sender_map = {s["day"]: s["unique_senders"] for s in senders.get("daily_unique_senders", [])}

        all_days = sorted(set(list(count_map) + list(vol_map) + list(sender_map)))
        if all_days:
            print(f"  {'Date':<12} {'Tx Count':>9} {'Volume':>16} {'Senders':>8}")
            print(f"  {'─' * 48}")
            for day in all_days:
                c = count_map.get(day, 0)
                v = vol_map.get(day, "0")
                s = sender_map.get(day, 0)
                print(f"  {day:<12} {c:>9} {v:>16} {s:>8}")
        else:
            print("  No data")
    except Exception as e:
        print(f"  Error: {e}")

    # ── Trailing Avg Balance (retail, last 7 days) ──
    _hr("30-DAY TRAILING AVG BALANCE (Retail Pool)")
    try:
        result = trailing_avg_balance([WALLETS["Retail Pool"]], week_ago, today)
        entries = result.get("entries", []) if isinstance(result, dict) else result
        if entries:
            latest = entries[-1]
            print(f"  Date:             {latest['date']}")
            print(f"  Daily balance:    {latest['daily_balance']} CBTC")
            print(f"  Trailing avg:     {latest['trailing_avg_balance']} CBTC")
        else:
            print("  No data")
    except Exception as e:
        print(f"  Error: {e}")

    print(f"\n{'═' * 60}")
    print(f"  Dashboard generated at {datetime.now(timezone.utc).isoformat()}Z")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    run_dashboard()
