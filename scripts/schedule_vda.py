#!/usr/bin/env python3
"""
Emit Schedule VDA (ITR-3) as a CSV — one row per transfer, FY 2025-26.

Schedule VDA wants date of acquisition, date of transfer, cost, consideration
and income per transfer. Typing 144 rows by hand is where the time goes; this
generates them from the reconstructed disposals.

Reads : data/vda_disposals.json  (produced by scripts/vda_reconstruct.py)
Writes: schedules/schedule_vda.csv

CAVEAT — read before filing. Consideration and cost here are reconstructed at
DAILY SPOT prices, not the actual P2P INR amounts. For P2P arbitrage the profit
IS the spread over spot, which this method cannot see. Treat this CSV as a
working paper, not as evidence. Replace with real P2P order values if you can
export them.
"""

import csv
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
FY_START = datetime.date(2025, 4, 1)
FY_END = datetime.date(2026, 3, 31)

disposals = json.loads((ROOT / "private" / "vda_disposals.json").read_text())

rows = []
for d in disposals:
    sold_on = datetime.date.fromisoformat(d["date"])
    if not (FY_START <= sold_on <= FY_END):
        continue
    rows.append({
        "Sl": len(rows) + 1,
        "Asset": d["coin"],
        "Date of Acquisition": "",          # FIFO pools lots; see note below
        "Date of Transfer": d["date"],
        "Quantity": f'{d["qty"]:.8f}',
        "Head of Income": "Capital Gains",
        "Cost of Acquisition (INR)": round(d["cost"]),
        "Consideration Received (INR)": round(d["proceeds"]),
        "Income from Transfer (INR)": round(d["gain"]),
        "Source": d["op"],
    })

out = ROOT / "private" / "schedules" / "schedule_vda.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

proceeds = sum(r["Consideration Received (INR)"] for r in rows)
cost = sum(r["Cost of Acquisition (INR)"] for r in rows)
gains = sum(r["Income from Transfer (INR)"] for r in rows
            if r["Income from Transfer (INR)"] > 0)
losses = -sum(r["Income from Transfer (INR)"] for r in rows
              if r["Income from Transfer (INR)"] < 0)

print(f"rows            {len(rows):>12}")
print(f"consideration   {proceeds:>12,}")
print(f"cost            {cost:>12,}")
print(f"gains only      {gains:>12,}   <- 115BBH taxable base")
print(f"losses          {losses:>12,}   <- NOT deductible, no set-off")
print(f"\nwrote {out}")
print("\nNOTE: 'Date of Acquisition' is blank — FIFO matched each sale against a")
print("pool of lots, so a single transfer can span several acquisition dates.")
print("The portal wants one date per row; pick the earliest lot consumed, or")
print("file the consolidated figures with this CSV retained as the working paper.")
