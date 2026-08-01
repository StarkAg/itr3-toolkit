# itr3-toolkit

Working papers for an Indian **ITR-3** — the statutory tables as code, a
computation sheet you can hand to a CA, and a FIFO reconstructor for crypto.

```bash
git clone https://github.com/StarkAg/itr3-toolkit
cd itr3-toolkit
python3 scripts/computation.py        # renders the bundled example
```

No dependencies. Python 3.9+.

---

## Why

ITR-3 is where the awkward cases land: presumptive income, F&O treated as
business, capital losses that cannot set off, crypto at a flat 30%. The rules
interact in ways that are easy to get subtly wrong, and spreadsheets do not
carry the reasoning.

This encodes the rules with the reasoning attached, and produces a computation
sheet in the format an Indian accountant expects.

## What is here

| | |
|---|---|
| `schema/options.py` | filing sections, regimes, presumptive schemes, special rates, loss carry-forward, cash-transaction limits, gift rules |
| `schema/schedules.py` | all 44 ITR-3 schedules + Part A/B, each with a note on when it applies |
| `schema/rates.py` | slabs for AY 2021-22 – 2026-27 × both regimes, 87A, surcharge, cess, capital-gains rates (both sides of the 23-07-2024 change), 22 Chapter VI-A sections, due dates |
| `scripts/computation.py` | case file → printable computation sheet |
| `scripts/vda_reconstruct.py` | exchange ledger → FIFO gain/loss |
| `scripts/schedule_vda.py` | → date-wise Schedule VDA CSV |
| `template/` | blank case file, 41 fields, documented |

## Use it for a real return

```bash
cp template/inputs.example.py my_case.py     # git-ignored by default
$EDITOR my_case.py
python3 scripts/computation.py --case my_case.py
```

PDF, without installing anything:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=computation.pdf "file://$PWD/computation.html"
```

Fields left as `None` render as `[PENDING]` and are excluded from the totals —
an unfinished return looks unfinished instead of quietly wrong. Use an explicit
`0` only for a confirmed nil.

### Crypto

```bash
python3 scripts/vda_reconstruct.py    # ledger → disposals
python3 scripts/schedule_vda.py       # → Schedule VDA CSV
```

FIFO per coin over an exchange ledger export. Read the docstring before
trusting the output — it values both legs at daily spot, which cannot see P2P
spreads, and for P2P arbitrage that spread *is* the profit. Treat it as a
working paper, not evidence.

## Rules worth knowing

Each of these is encoded, with a test pinning it.

**The new regime changed shape twice, not once.** It launched in AY 2021-22
optional, with a 7-slab table starting at ₹2.5L and no standard deduction.
Budget 2023 made it the default from AY 2024-25, collapsed it to 6 slabs
starting at ₹3L, and added a standard deduction. Finance Act 2025 widened it
again for AY 2026-27. A case file for AY 2022-23 must not reuse today's slabs.

**The capital-gains rate change landed mid-year, not at an AY boundary.**
Finance (No. 2) Act 2024 raised STCG/LTCG rates from 23 July 2024 — partway
through AY 2025-26 (FY 2024-25). A single AY 2025-26 return can carry both the
old and new rates depending on each asset's transfer date;
`CAPITAL_GAINS_PERIODS` is keyed by date range, not by AY, for exactly this
reason.

**87A cuts both ways.** The ₹12,00,000 ceiling is tested on *total* income
including special-rate income, but the rebate applies only to *slab* tax. A
small amount of crypto income can therefore destroy a large rebate.

**115BBH allows nothing.** Gains only — no set-off between assets, none against
other heads, no carry-forward, and cost of acquisition is the sole deduction.
Not even transfer expenses.

**A tax-exempt gift can still be illegal.** §269ST bars *receiving* ₹2,00,000+
in cash per person/day, per transaction, or per occasion, and there is no
exemption for relatives. A gift fully exempt under §56(2)(x) still attracts a
§271DA penalty equal to the amount received — on the recipient.

**Presumptive schemes have floors.** 44ADA needs ≥50% of gross receipts, 44AD
≥6% digital / 8% cash. Below the floor you need books and an audit. The
computation script warns when a case breaches this.

**Belated returns forfeit loss carry-forward.** Unabsorbed depreciation is the
only survivor.

**Non-audit ITR-3/ITR-4 are due 31 August**, not 31 July — a permanent change
under the Finance Act 2026, and it does not apply to ITR-1/ITR-2.

**Schedule FA covers the whole year**, not just year-end holdings, and
non-disclosure is a flat ₹10,00,000 penalty under the Black Money Act.

## Reconstructing crypto from a ledger

If you write your own reconstruction, include **every** flow. Counting only
trades and skipping deposits and withdrawals leaves withdrawn coin sitting in
the lot pool, so old cheap lots survive to be matched against later sales and
manufacture gains that were never realised. In the case this was built from,
that produced a result roughly 90× too high.

The check is that the pool closes to ~0 at year end. `vda_reconstruct.py`
prints the residual for exactly this reason.

## Tests

```bash
python3 tests/test_rates.py     # or: python3 -m pytest -q
```

32 tests over the slab boundaries across all six years, the 87A interaction,
presumptive floors, special-rate restrictions, loss lifetimes and cash limits.

## Keeping your data out of git

`.gitignore` excludes `private/`, `cases/`, `*_case.py` and `inputs.py` by
default. Case files hold PAN, Aadhaar and bank details — check `git status`
before your first commit, and consider keeping real cases in a separate private
repository entirely.

## Scope

Computation and working papers. It does **not** connect to the e-filing portal
and does not file anything.

Not tax advice, and not a substitute for a chartered accountant — particularly
on presumptive-scheme eligibility, cash-transaction exposure, foreign assets,
or a year needing ITR-U. Verify rates against the current Finance Act before
relying on them; contributions correcting them are welcome.

## Contributing

Corrections to the statutory tables are the most valuable contribution — cite
the section or Finance Act, and add a test. Support for other ITR forms, and
ledger parsers for other exchanges, are both natural extensions.

MIT licensed.
