#!/usr/bin/env python3
"""
Computation of Income — renders a case file as an accountant-style sheet.

Usage:
    python3 scripts/computation.py [--case PATH] [--out PATH]

--case defaults to examples/sample_case.py, so a fresh clone runs immediately.
Point it at your own case file (keep that outside version control).

Fields left as None are not yet established: they print as [PENDING] and are
excluded from the totals, so an unfinished sheet is visibly unfinished rather
than quietly wrong. Use an explicit 0 only for a confirmed nil.
"""

import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

_ap = argparse.ArgumentParser(description=__doc__,
                              formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--case", type=pathlib.Path,
                 default=ROOT / "examples" / "sample_case.py",
                 help="case file to render (default: the bundled example)")
_ap.add_argument("--out", type=pathlib.Path, default=None,
                 help="output HTML path (default: <case dir>/computation.html)")
_args = _ap.parse_args()

if not _args.case.exists():
    sys.exit(f"case file not found: {_args.case}\n"
             f"Copy template/inputs.example.py and fill it in.")

_spec = importlib.util.spec_from_file_location("case", _args.case)
case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(case)


def _get(name, default=None):
    """Read a field from the case file, tolerating omissions."""
    return getattr(case, name, default)


PROFILE                = _get("PROFILE", {})
PROFESSION             = _get("PROFESSION", {}) or {}
FNO_RESULT             = _get("FNO_RESULT") or 0
SPECULATIVE_RESULT     = _get("SPECULATIVE_RESULT") or 0
STCG_111A              = _get("STCG_111A") or 0
LTCG_112A              = _get("LTCG_112A") or 0
VDA_GAIN               = _get("VDA_GAIN") or 0
VDA_SALE_CONSIDERATION = _get("VDA_SALE_CONSIDERATION")
VDA_COST               = _get("VDA_COST")
GAMING_WINNINGS        = _get("GAMING_WINNINGS")
SAVINGS_INTEREST       = _get("SAVINGS_INTEREST", []) or []
FD_INTEREST            = _get("FD_INTEREST", []) or []
DIVIDEND               = _get("DIVIDEND") or 0
EXEMPT_INCOME          = _get("EXEMPT_INCOME", []) or []
TDS_194S               = _get("TDS_194S") or 0
ADVANCE_TAX            = _get("ADVANCE_TAX") or 0
SELF_ASSESSMENT_TAX    = _get("SELF_ASSESSMENT_TAX") or 0

PRESUMPTIVE_TURNOVER = PROFESSION.get("gross_receipts")
PRESUMPTIVE_INCOME   = PROFESSION.get("declared_income")
PRESUMPTIVE_SECTION  = PROFESSION.get("section") or "44AD"
PRESUMPTIVE_RATE     = PROFESSION.get("rate")
REGIME               = PROFILE.get("regime", "new")

# ------------------------- STATUTORY PARAMETERS ------------------------------

NEW_SLABS = [(400000, 0.00), (800000, 0.05), (1200000, 0.10),
             (1600000, 0.15), (2000000, 0.20), (2400000, 0.25),
             (float("inf"), 0.30)]
REBATE_LIMIT, REBATE_MAX = 1200000, 60000
CESS = 0.04
VDA_RATE, GAMING_RATE = 0.30, 0.30


def slab_tax(income):
    tax, lower = 0.0, 0
    for upto, rate in NEW_SLABS:
        if income <= lower:
            break
        tax += (min(income, upto) - lower) * rate
        lower = upto
    return tax


# ------------------------------ COMPUTE --------------------------------------

pending = []

warnings = []

presumptive = 0
eff_rate = None
if PRESUMPTIVE_INCOME is not None:
    presumptive = PRESUMPTIVE_INCOME
    if PRESUMPTIVE_TURNOVER:
        eff_rate = presumptive / PRESUMPTIVE_TURNOVER
elif PRESUMPTIVE_TURNOVER is None:
    pending.append("Presumptive business/profession income (u/s %s)" % PRESUMPTIVE_SECTION)
else:
    eff_rate = PRESUMPTIVE_RATE
    presumptive = round(PRESUMPTIVE_TURNOVER * PRESUMPTIVE_RATE)

# Statutory floors: 44ADA = 50% of gross receipts; 44AD = 6% digital / 8% cash.
if eff_rate is not None:
    floor = 0.50 if PRESUMPTIVE_SECTION == "44ADA" else 0.06
    if eff_rate < floor - 1e-9:
        warnings.append(
            f"Declared income is {eff_rate:.2%} of gross receipts "
            f"({presumptive:,} on {PRESUMPTIVE_TURNOVER:,}), which is BELOW the "
            f"{floor:.0%} statutory minimum for {PRESUMPTIVE_SECTION}. Declaring below "
            f"the floor requires books u/s 44AA and a tax audit u/s 44AB — "
            f"the presumptive scheme cannot be used as-is."
        )

gaming = 0
if GAMING_WINNINGS is None:
    pending.append("Online gaming / betting winnings u/s 115BBJ")
else:
    gaming = GAMING_WINNINGS

if VDA_SALE_CONSIDERATION is None or VDA_COST is None:
    pending.append("VDA gross sale consideration & cost (needed for Schedule VDA)")

# Business head: F&O loss sets off against presumptive income in the same year.
business_income = presumptive + FNO_RESULT + max(SPECULATIVE_RESULT, 0)
business_cf = []
if FNO_RESULT < 0 and presumptive == 0:
    business_income = 0
    business_cf.append(("Non-Speculative Business Loss (F&O)", -FNO_RESULT, "u/s 72 (8 years)"))
if SPECULATIVE_RESULT < 0:
    business_cf.append(("Speculative Business Loss (Intraday)", -SPECULATIVE_RESULT, "u/s 73 (4 years)"))

# Capital losses cannot set off against other heads -> carried forward.
cg_cf = []
if STCG_111A < 0:
    cg_cf.append(("Short-Term Capital Loss (STCG)", -STCG_111A, "u/s 74 (8 years)"))
if LTCG_112A < 0:
    cg_cf.append(("Long-Term Capital Loss (LTCG)", -LTCG_112A, "u/s 74 (8 years)"))
stcg_taxable = max(STCG_111A, 0)
ltcg_taxable = max(LTCG_112A, 0)

sav_total = sum(a for _, a in SAVINGS_INTEREST)
fd_total = sum(a for _, a in FD_INTEREST)
other_sources = sav_total + fd_total + DIVIDEND

normal_income = max(business_income, 0) + other_sources
total_income = normal_income + VDA_GAIN + gaming + stcg_taxable + ltcg_taxable

tax_normal = slab_tax(normal_income)
tax_vda = VDA_GAIN * VDA_RATE
tax_gaming = gaming * GAMING_RATE
tax_special = tax_vda + tax_gaming

# 87A rebate: slab income only. Finance Act 2025 bars rebate on special-rate income.
rebate = min(tax_normal, REBATE_MAX) if total_income <= REBATE_LIMIT else 0
tax_after_rebate = (tax_normal - rebate) + tax_special
cess_amt = round(tax_after_rebate * CESS)
total_tax = round(tax_after_rebate) + cess_amt
prepaid = TDS_194S + ADVANCE_TAX + SELF_ASSESSMENT_TAX
payable = total_tax - prepaid

# ------------------------------- RENDER --------------------------------------

def r(n):
    return f"{round(n):,}".replace(",", ",")


rows = []
def add(label, val=None, tot=None, cls=""):
    rows.append((label, val, tot, cls))

n = 1
head = ("Gains from Profession" if PRESUMPTIVE_SECTION == "44ADA"
        else "Gains from Business")
add(f"{n}. {head} — Eligible (u/s {PRESUMPTIVE_SECTION})", None, None, "head")
if presumptive == 0 and PRESUMPTIVE_TURNOVER is None:
    add("Gross Receipts", "[PENDING]", None, "pending")
    add("Deemed Profit", "[PENDING]", "[PENDING]", "pending")
else:
    pct = f" @ {eff_rate:.2%}" if eff_rate is not None else ""
    add(f"Gross Receipts{pct}", r(PRESUMPTIVE_TURNOVER))
    add("Deemed Profit", r(presumptive), r(presumptive))
n += 1

add(f"{n}. Business - Non-Speculative (F&O)", None, None, "head")
add("Net Result from F&O Trading", f"({r(-FNO_RESULT)})" if FNO_RESULT < 0 else r(FNO_RESULT))
if presumptive:
    add("Set off against presumptive business income", None, r(business_income))
else:
    add("Loss not set off; carried forward u/s 72", None, "NIL")
n += 1

add(f"{n}. Income from Capital Gains", None, None, "head")
add("Short-Term Capital Gain on Equity (u/s 111A)",
    f"({r(-STCG_111A)})" if STCG_111A < 0 else r(STCG_111A))
add("Long-Term Capital Gain on Equity (u/s 112A)",
    f"({r(-LTCG_112A)})" if LTCG_112A < 0 else r(LTCG_112A))
add("Net Capital Gains (taxable)", None, r(stcg_taxable + ltcg_taxable))
n += 1

add(f"{n}. Income from Virtual Digital Assets (u/s 115BBH)", None, None, "head")
if VDA_SALE_CONSIDERATION is not None:
    add("Sale Consideration", r(VDA_SALE_CONSIDERATION))
    add("Less : Cost of Acquisition", r(VDA_COST))
else:
    add("Sale Consideration", "[PENDING]", None, "pending")
    add("Less : Cost of Acquisition", "[PENDING]", None, "pending")
add("Net Gain from VDA (no loss set-off permitted)", None, r(VDA_GAIN))
n += 1

if GAMING_WINNINGS is None:
    add(f"{n}. Winnings from Online Games (u/s 115BBJ)", None, None, "head")
    add("Net Winnings", "[PENDING]", "[PENDING]", "pending")
    n += 1
elif gaming:
    add(f"{n}. Winnings from Online Games (u/s 115BBJ)", None, None, "head")
    add("Net Winnings", r(gaming), r(gaming))
    n += 1

add(f"{n}. Income from Other Sources", None, None, "head")
for lbl, amt in SAVINGS_INTEREST:
    add(lbl, r(amt))
add("Interest from Savings Accounts", None, r(sav_total), "sub")
for lbl, amt in FD_INTEREST:
    add(lbl, r(amt))
add("Interest from Deposits (FD)", None, r(fd_total), "sub")
add("Dividend Income", r(DIVIDEND), r(DIVIDEND))
add("Income from Other Sources", None, r(other_sources), "sub")

add("Gross Total Income", None, r(total_income), "total")
add("Less : Deductions Chapter VI-A (New Regime - not available)", None, "0")
add("Net Total Income", None, r(total_income), "total")

add("Tax on Above", None, None, "head")
add(f"Tax on Normal Income (slab) — {r(normal_income)}", r(tax_normal))
add(f"Tax on VDA @ 30% (u/s 115BBH) — {r(VDA_GAIN)}", r(tax_vda))
if gaming:
    add(f"Tax on Winnings @ 30% (u/s 115BBJ) — {r(gaming)}", r(tax_gaming))
add("Less : Rebate u/s 87A (slab income only)", f"({r(rebate)})" if rebate else "0")
add("Tax after Rebate", None, r(tax_after_rebate), "sub")
add("Add : Health & Education Cess @ 4%", r(cess_amt))
add("Total Tax Liability", None, r(total_tax), "total")
add("Less : TDS u/s 194S (AIS - active entries)", f"({r(TDS_194S)})")
if ADVANCE_TAX:
    add("Less : Advance Tax", f"({r(ADVANCE_TAX)})")
add("Tax Payable" if payable >= 0 else "Refund Due", None,
    r(abs(payable)), "total")

cf = business_cf + cg_cf
if cf:
    add("Losses Carried Forward", None, None, "head")
    for lbl, amt, sec in cf:
        add(f"{lbl} — {sec}", r(amt))

if EXEMPT_INCOME:
    add("Exempt Income (Schedule EI — reported, not taxed)", None, None, "head")
    for lbl, amt in EXEMPT_INCOME:
        add(lbl, r(amt))
    add("Total Exempt Income", None, r(sum(a for _, a in EXEMPT_INCOME)), "sub")

body = ""
for label, val, tot, cls in rows:
    if cls == "head":
        body += f'<tr class="head"><td colspan="3">{label}</td></tr>'
    else:
        c = f' class="{cls}"' if cls else ""
        body += (f'<tr{c}><td class="l">{label}</td>'
                 f'<td class="n">{val or ""}</td><td class="n b">{tot or ""}</td></tr>')

pending_html = ""
if pending:
    items = "".join(f"<li>{p}</li>" for p in pending)
    pending_html = (f'<div class="warn"><strong>Not yet established — '
                    f'excluded from the totals above:</strong><ul>{items}</ul></div>')

if warnings:
    items = "".join(f"<li>{w}</li>" for w in warnings)
    pending_html += (f'<div class="warn"><strong>Compliance warnings:</strong>'
                     f'<ul>{items}</ul></div>')

html = f"""<meta charset="utf-8"><title>Computation of Income — {PROFILE['name']} — AY 2026-27</title>
<style>
 body{{font-family:'Times New Roman',Georgia,serif;max-width:820px;margin:28px auto;color:#111;font-size:14px}}
 h1{{text-align:center;font-size:19px;margin:0 0 2px}}
 .ay{{text-align:right;font-weight:bold;margin-bottom:10px}}
 .meta{{width:100%;border-collapse:collapse;margin-bottom:14px;font-size:13px}}
 .meta td{{padding:2px 4px;vertical-align:top}}
 .meta .k{{width:150px}}
 h2{{text-align:center;font-size:15px;letter-spacing:1px;border-top:1.5px solid #111;
     border-bottom:1.5px solid #111;padding:5px 0;margin:14px 0}}
 table.c{{width:100%;border-collapse:collapse}}
 table.c td{{padding:2.5px 5px}}
 td.l{{width:58%}} td.n{{text-align:right;width:21%;font-variant-numeric:tabular-nums}}
 td.n.b{{font-weight:600}}
 tr.head td{{font-weight:bold;padding-top:9px}}
 tr.sub td{{border-top:1px solid #bbb}}
 tr.total td{{border-top:1.5px solid #111;border-bottom:1.5px solid #111;font-weight:bold}}
 tr.pending td{{color:#a11}}
 .warn{{border:1.5px solid #a11;background:#fff4f4;padding:9px 13px;margin-top:18px;font-size:13px}}
 .warn ul{{margin:6px 0 0 18px}}
 .foot{{margin-top:26px;font-size:12px;font-style:italic}}
 @media print{{body{{margin:0}}}}
</style>
<h1>{PROFILE['name']}</h1>
<div class="ay">ASSMT. YR. 2026-27</div>
<table class="meta">
 <tr><td class="k">Father's Name</td><td>: {PROFILE['father']}</td>
     <td class="k">Status</td><td>: {PROFILE['status']}</td></tr>
 <tr><td class="k">Address</td><td>: {PROFILE['addr1']}</td>
     <td class="k">Regime</td><td>: NEW (115BAC)</td></tr>
 <tr><td class="k"></td><td>&nbsp; {PROFILE['addr2']}</td>
     <td class="k">Previous Year End</td><td>: {PROFILE['py_end']}</td></tr>
 <tr><td class="k">Date of Birth</td><td>: {PROFILE['dob']}</td>
     <td class="k">Aadhaar No.</td><td>: {PROFILE['aadhaar']}</td></tr>
 <tr><td class="k">Permanent Account No.</td><td>: {PROFILE['pan']}</td>
     <td class="k">Mobile No.</td><td>: {PROFILE['mobile']}</td></tr>
</table>
<h2>COMPUTATION OF INCOME</h2>
<table class="c">{body}</table>
{pending_html}
<div class="foot">A Stark Industries Software</div>
"""

import pathlib
out = _args.out or (_args.case.parent / "computation.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html)

print(f"Normal (slab) income      {r(normal_income):>12}")
print(f"VDA gain @30%             {r(VDA_GAIN):>12}")
print(f"Total income              {r(total_income):>12}")
print(f"Tax on slab income        {r(tax_normal):>12}")
print(f"87A rebate                {r(rebate):>12}")
print(f"Tax on VDA                {r(tax_vda):>12}")
print(f"Cess @4%                  {r(cess_amt):>12}")
print(f"TOTAL TAX                 {r(total_tax):>12}")
print(f"Less prepaid (TDS)        {r(prepaid):>12}")
print(f"{'TAX PAYABLE' if payable>=0 else 'REFUND':<25} {r(abs(payable)):>12}")
if pending:
    print("\nPENDING (excluded):")
    for p in pending:
        print("  -", p)
print(f"\nwrote {out}")
