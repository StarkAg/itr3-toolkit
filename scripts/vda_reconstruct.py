#!/usr/bin/env python3
"""
Reconstruct VDA gain/loss for a financial year from an exchange ledger.

Reads : private/ledger.txt          (pdftotext -layout of the exchange export)
        private/fx_usdinr.json      (USD/INR daily — api.frankfurter.dev)
        private/coin_usd_prices.json(daily closes — api.binance.com klines)
Writes: private/vda_disposals.json

Written against a Binance "Transaction History" PDF export, whose rows read
    <user id> <timestamp> <wallet> <operation> <coin> <change> [remark]
Point LEDGER at a different export and adjust ROW/INTERNAL/DISPOSAL_OPS to
match its vocabulary.

METHOD
  FIFO per coin. Every inflow (P2P buy, Deposit, Crypto Box, Send) opens a lot;
  every outflow consumes lots oldest-first. Withdrawals consume lots but are
  NOT disposals — moving coin to your own wallet is not a transfer for 115BBH.
  Wallet-internal transfers are ignored entirely.

THE MISTAKE THIS GUARDS AGAINST
  Counting only trades and skipping Deposit/Withdraw leaves withdrawn coin
  sitting in the lot pool. Old cheap lots then survive to be matched against
  later sales, manufacturing gains that were never realised — in the case this
  was built from, an inflated result roughly 90x the corrected one. Including
  every flow makes the pool close to ~0 at year end, which is the check that
  the reconstruction is honest. Watch the residual printed at the end.

WHAT THIS CANNOT DO
  Both legs are valued at DAILY SPOT. For P2P trading the profit IS the premium
  over spot, and that margin is invisible to a spot-priced model by
  construction — so the output is a floor, not a measurement, and understates
  real profit. Prefer actual order values with INR amounts whenever the exchange
  can export them, and treat this as a working paper.
"""

import datetime
import json
import os
import pathlib
import re
from collections import defaultdict, deque

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "private"
LEDGER = DATA / os.environ.get("VDA_LEDGER", "ledger.txt")

# Financial year being filed — override with FY_START_YEAR=2024 etc.
_fy = int(os.environ.get("FY_START_YEAR", 2025))
FY_START = datetime.date(_fy, 4, 1)
FY_END = datetime.date(_fy + 1, 3, 31)

# Wallet-internal moves — no acquisition, no disposal.
INTERNAL = {
    "Transfer Between Spot and Funding",
    "Transfer Funds to Spot",
    "Transfer Funds to Funding Wallet",
}
# Outflows that ARE transfers for 115BBH purposes.
DISPOSAL_OPS = {"P2P Trading", "Merchant Acquiring", "Small Assets Exchange BNB"}

# Leading account id varies per export; matched generically rather than pinned.
ROW = re.compile(
    r"^\d{6,}\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\S+)\s+(.+?)\s{2,}"
    r"([A-Z0-9]{2,15})\s+(-?\d+\.?\d*)\s*(.*)$"
)

fx = json.loads((DATA / "fx_usdinr.json").read_text())
coin_usd = json.loads((DATA / "coin_usd_prices.json").read_text())


def nearest(series, day):
    """Nearest quote on/before `day`, else on/after. Covers weekends/holidays."""
    for delta in range(0, 12):
        k = (datetime.date.fromisoformat(day) - datetime.timedelta(days=delta)).isoformat()
        if k in series:
            return series[k]
    for delta in range(1, 12):
        k = (datetime.date.fromisoformat(day) + datetime.timedelta(days=delta)).isoformat()
        if k in series:
            return series[k]
    return None


def inr_price(coin, day):
    rate = nearest(fx, day)
    if coin in ("USDT", "USDC"):
        return rate                      # dollar stablecoins: 1 USD
    usd = nearest(coin_usd.get(coin, {}), day)
    return usd * rate if (usd and rate) else None


rows = []
for line in LEDGER.read_text().splitlines():
    m = ROW.match(line.strip())
    if m:
        date, account, op, coin, change, remark = m.groups()
        rows.append((date, account, op.strip(), coin, float(change), remark.strip()))
rows.sort(key=lambda r: r[0])

lots = defaultdict(deque)     # coin -> deque([qty, inr_cost_per_unit])
disposals = []
unpriced = 0

for date, _account, op, coin, change, _remark in rows:
    if op in INTERNAL:
        continue
    day = date[:10]
    price = inr_price(coin, day)
    if price is None:
        unpriced += 1
        continue

    if change > 0:
        lots[coin].append([change, price])          # buy or deposit
        continue

    qty = -change
    remaining, cost = qty, 0.0
    while remaining > 1e-12 and lots[coin]:
        lot = lots[coin][0]
        take = min(lot[0], remaining)
        cost += take * lot[1]
        lot[0] -= take
        remaining -= take
        if lot[0] <= 1e-12:
            lots[coin].popleft()

    if op == "Withdraw":
        continue                                     # own wallet: not a transfer
    if op not in DISPOSAL_OPS:
        continue

    proceeds = qty * price
    disposals.append({
        "date": day,
        "coin": coin,
        "op": op,
        "qty": qty,
        "px_inr": price,
        "proceeds": proceeds,
        "cost": cost,
        "gain": proceeds - cost,
        "in_fy": FY_START <= datetime.date.fromisoformat(day) <= FY_END,
        "unmatched_qty": remaining,        # >0 means no acquisition record found
    })

(DATA / "vda_disposals.json").write_text(json.dumps(disposals, indent=1))

fy = [d for d in disposals if d["in_fy"]]
gains = sum(d["gain"] for d in fy if d["gain"] > 0)
losses = -sum(d["gain"] for d in fy if d["gain"] < 0)
residual = {c: sum(l[0] for l in q) for c, q in lots.items() if sum(l[0] for l in q) > 1e-6}

print(f"disposals in FY   {len(fy):>12}")
print(f"consideration     {sum(d['proceeds'] for d in fy):>12,.0f}")
print(f"cost              {sum(d['cost'] for d in fy):>12,.0f}")
print(f"gains only        {gains:>12,.0f}   <- 115BBH base")
print(f"losses            {losses:>12,.0f}   <- no set-off permitted")
print(f"tax @30%          {gains * 0.30:>12,.0f}")
if unpriced:
    print(f"\nrows skipped (no price): {unpriced}")
print("\nresidual balance left in pool (sanity check, should be ~0):")
for coin, qty in residual.items():
    print(f"  {coin:6} {qty:.8f}")
