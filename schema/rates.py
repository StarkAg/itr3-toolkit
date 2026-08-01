"""
Statutory rates by assessment year and regime.

Covers AY 2021-22 (when s.115BAC / the new regime was introduced) through
AY 2026-27. Add a new AY by adding a dict entry — no other file should need
editing.

Sources: Finance Act 2020 (introduced 115BAC, AY 2021-22) through Finance Act
2025 (AY 2026-27) and Finance Act 2026 (ITR-3/4 due-date change). Capital
gains: Finance (No. 2) Act 2024, effective 23-07-2024 — mid-year within
AY 2025-26, not at an AY boundary; see CAPITAL_GAINS_PERIODS below.
"""

# ---------------------------------------------------------------------------
# Slabs — (upper_bound, rate); the last bound is None for "and above"
# ---------------------------------------------------------------------------

OLD_REGIME_SLABS = [
    (2_50_000, 0.00),
    (5_00_000, 0.05),
    (10_00_000, 0.20),
    (None, 0.30),
]

# Old-regime basic exemption is age-based.
OLD_REGIME_EXEMPTION = {
    "below60":     2_50_000,
    "senior":      3_00_000,
    "superSenior": 5_00_000,
}

# The pre-Budget-2023 new regime (AY 2021-22 through AY 2023-24) was optional,
# had no standard deduction, and used a finer 7-slab table starting at 2.5L —
# unchanged across all three years. Budget 2023 replaced it for AY 2024-25
# onward: made it the default, added a standard deduction, and moved to a
# 6-slab table starting at 3L. AY 2026-27 (Finance Act 2025) widened the
# slabs again and raised the exemption to 4L.
_NEW_REGIME_2021_23 = [
    (2_50_000, 0.00), (5_00_000, 0.05), (7_50_000, 0.10),
    (10_00_000, 0.15), (12_50_000, 0.20), (15_00_000, 0.25),
    (None, 0.30),
]

NEW_REGIME_SLABS = {
    "2021-22": _NEW_REGIME_2021_23,
    "2022-23": _NEW_REGIME_2021_23,
    "2023-24": _NEW_REGIME_2021_23,
    "2024-25": [
        (3_00_000, 0.00), (6_00_000, 0.05), (9_00_000, 0.10),
        (12_00_000, 0.15), (15_00_000, 0.20), (None, 0.30),
    ],
    "2025-26": [
        (3_00_000, 0.00), (7_00_000, 0.05), (10_00_000, 0.10),
        (12_00_000, 0.15), (15_00_000, 0.20), (None, 0.30),
    ],
    "2026-27": [
        (4_00_000, 0.00), (8_00_000, 0.05), (12_00_000, 0.10),
        (16_00_000, 0.15), (20_00_000, 0.20), (24_00_000, 0.25),
        (None, 0.30),
    ],
}

# Before AY 2024-25 the new regime was OPTIONAL — filers defaulted to the old
# regime unless they affirmatively chose 115BAC. From AY 2024-25 it flipped:
# new is the default, and opting for old regime needs Form 10-IEA where there
# is business/professional income.
NEW_REGIME_WAS_DEFAULT_FROM = "2024-25"

# ---------------------------------------------------------------------------
# Rebate u/s 87A
# ---------------------------------------------------------------------------
# The threshold is tested on TOTAL income (including special-rate income), but
# the rebate itself is allowed only against SLAB tax. Finance Act 2025 put the
# exclusion of special-rate income beyond argument.

# Before Budget 2023, the new regime's rebate was identical to the old
# regime's — 5,00,000 / 12,500. Budget 2023 raised it for the new regime only;
# the old regime's has not changed since.
REBATE_87A = {
    "old": dict(income_limit=5_00_000, max_rebate=12_500),
    "new": {
        "2021-22": dict(income_limit=5_00_000,  max_rebate=12_500),
        "2022-23": dict(income_limit=5_00_000,  max_rebate=12_500),
        "2023-24": dict(income_limit=5_00_000,  max_rebate=12_500),
        "2024-25": dict(income_limit=7_00_000,  max_rebate=25_000),
        "2025-26": dict(income_limit=7_00_000,  max_rebate=25_000),
        "2026-27": dict(income_limit=12_00_000, max_rebate=60_000),
    },
}

REBATE_87A_EXCLUDES_SPECIAL_RATE = True

# ---------------------------------------------------------------------------
# Standard deduction on salary
# ---------------------------------------------------------------------------

STANDARD_DEDUCTION = {
    "old": 50_000,  # unchanged since AY 2020-21
    "new": {
        "2021-22": 0, "2022-23": 0, "2023-24": 0,   # not available pre-2023 new regime
        "2024-25": 50_000, "2025-26": 75_000, "2026-27": 75_000,
    },
}

# ---------------------------------------------------------------------------
# Surcharge — on tax, above these total-income thresholds
# ---------------------------------------------------------------------------

SURCHARGE_BANDS = [
    (50_00_000, 0.10),
    (1_00_00_000, 0.15),
    (2_00_00_000, 0.25),
    (5_00_00_000, 0.37),
]

# The new regime caps surcharge at 25%. Surcharge on 111A/112A/112 capital gains
# and on dividend is capped at 15% under both regimes.
SURCHARGE_CAP_NEW_REGIME = 0.25
SURCHARGE_CAP_ON_CG_AND_DIVIDEND = 0.15

# Marginal relief applies wherever crossing a surcharge threshold — or the 87A
# ceiling — would increase tax by more than the increase in income.
MARGINAL_RELIEF_APPLIES = True

CESS = 0.04  # Health and Education Cess, on tax plus surcharge

# ---------------------------------------------------------------------------
# Capital gains
# ---------------------------------------------------------------------------
# Finance (No. 2) Act 2024 changed these rates from 23 July 2024 — a date
# mid-way through AY 2025-26 (FY 2024-25), not an assessment-year boundary.
# A single AY 2025-26 return can carry BOTH rates depending on each asset's
# transfer date. Pick by transfer date, not by which AY you are filing:
#
#   transfer date <= 22-07-2024  -> CAPITAL_GAINS_PERIODS["pre_2024_07_23"]
#   transfer date >= 23-07-2024  -> CAPITAL_GAINS_PERIODS["post_2024_07_23"]
#
# Every full AY from 2021-22 through 2024-25 (i.e. up to FY 2023-24) falls
# entirely in the "pre" bucket. AY 2026-27 onward falls entirely "post".
# AY 2025-26 is the one year that can straddle both.

CAPITAL_GAINS_PERIODS = {
    "pre_2024_07_23": dict(
        stcg_111A=0.15,
        ltcg_112A=0.10,
        ltcg_112A_annual_exemption=1_00_000,
        ltcg_112="0.20 with indexation (other long-term assets)",
    ),
    "post_2024_07_23": dict(
        stcg_111A=0.20,
        ltcg_112A=0.125,
        ltcg_112A_annual_exemption=1_25_000,
        ltcg_112=0.125,
        indexation="Withdrawn from 23-07-2024. Resident individuals may elect "
                   "the pre-amendment 20%-with-indexation for immovable "
                   "property acquired before that date.",
    ),
}

# Convenience alias: the rates in force today (AY 2026-27 and beyond).
CAPITAL_GAINS = CAPITAL_GAINS_PERIODS["post_2024_07_23"]

# ---------------------------------------------------------------------------
# Chapter VI-A caps — OLD regime only, except 80CCD(2) and 80JJAA
# ---------------------------------------------------------------------------

CHAPTER_VIA = {
    "80C":       dict(cap=1_50_000, desc="LIC, PPF, ELSS, principal on housing loan, tuition fees"),
    "80CCC":     dict(cap=1_50_000, desc="Pension fund — shares the 80C ceiling"),
    "80CCD(1)":  dict(cap=1_50_000, desc="NPS employee — within the 80C ceiling"),
    "80CCD(1B)": dict(cap=50_000,   desc="NPS additional — over and above 80C"),
    "80CCD(2)":  dict(cap="10% of salary (14% for government employees)",
                      desc="Employer NPS contribution — ALLOWED IN THE NEW REGIME"),
    "80D":       dict(cap="25,000 self and family; 50,000 where senior citizens",
                      desc="Health insurance; 5,000 within it for preventive check-up"),
    "80DD":      dict(cap="75,000; 1,25,000 for severe disability",
                      desc="Maintenance of a dependant with disability"),
    "80DDB":     dict(cap="40,000; 1,00,000 for senior citizens",
                      desc="Treatment of specified diseases"),
    "80E":       dict(cap=None, desc="Interest on education loan — 8 years, no cap"),
    "80EE":      dict(cap=50_000, desc="First-time home buyer interest"),
    "80EEA":     dict(cap=1_50_000, desc="Affordable housing interest"),
    "80EEB":     dict(cap=1_50_000, desc="Electric vehicle loan interest"),
    "80G":       dict(cap="50% or 100%, some subject to 10% of adjusted GTI",
                      desc="Donations. Cash donations above 2,000 are disallowed"),
    "80GG":      dict(cap="Least of 5,000/month, 25% of total income, or rent "
                          "less 10% of total income",
                      desc="Rent paid where no HRA is received"),
    "80GGC":     dict(cap=None, desc="Political contributions — non-cash only"),
    "80TTA":     dict(cap=10_000, desc="Savings interest — below 60"),
    "80TTB":     dict(cap=50_000, desc="Savings and deposit interest — senior citizens"),
    "80U":       dict(cap="75,000; 1,25,000 for severe disability",
                      desc="Self, with disability"),
    "80JJAA":    dict(cap="30% of additional employee cost, 3 years",
                      desc="New employment — ALLOWED IN THE NEW REGIME"),
    "80QQB":     dict(cap=3_00_000, desc="Royalty on books"),
    "80RRB":     dict(cap=3_00_000, desc="Royalty on patents"),
    "80CCH":     dict(cap=None, desc="Agnipath Scheme — Agniveer Corpus Fund "
                      "contribution. ALLOWED IN THE NEW REGIME (from AY 2023-24)"),
}

NEW_REGIME_ALLOWS_ONLY = ("80CCD(2)", "80JJAA", "80CCH")

# ---------------------------------------------------------------------------
# Due dates
# ---------------------------------------------------------------------------
# STATUTORY dates only — i.e. what the Act specifies before any CBDT
# notification extends them. CBDT has extended the non-audit deadline in
# several recent years (AY 2024-25 and AY 2025-26 among them); those
# extensions are announced late and change the practical date, not the one
# below. Always check for a current-year circular before relying on this.
#
# Finance Act 2026 moved non-audit ITR-3/ITR-4 to 31 August PERMANENTLY,
# splitting them from ITR-1/ITR-2 for the first time. That split does not
# exist in earlier years — all non-audit forms shared one date.
#
# AY 2021-22 and AY 2022-23 are deliberately omitted: COVID-era due dates were
# revised multiple times by successive notifications and a single "statutory"
# date would be misleading for those two years specifically.

DUE_DATES = {
    "2023-24": {
        "all_non_audit":       "31-07-2023",
        "audit":               "31-10-2023",
        "transfer_pricing":    "30-11-2023",
        "belated_and_revised": "31-12-2023",
    },
    "2024-25": {
        "all_non_audit":       "31-07-2024",
        "audit":               "31-10-2024",
        "transfer_pricing":    "30-11-2024",
        "belated_and_revised": "31-12-2024",
    },
    "2025-26": {
        "all_non_audit":       "31-07-2025",
        "audit":               "31-10-2025",
        "transfer_pricing":    "30-11-2025",
        "belated_and_revised": "31-12-2025",
    },
    "2026-27": {
        "itr1_itr2_non_audit": "31-07-2026",
        "itr3_itr4_non_audit": "31-08-2026",
        "audit":               "31-10-2026",
        "transfer_pricing":    "30-11-2026",
        "belated_and_revised": "31-12-2026",
    },
}

ADVANCE_TAX_INSTALMENTS = [
    ("15 June",      0.15),
    ("15 September", 0.45),
    ("15 December",  0.75),
    ("15 March",     1.00),
]

ADVANCE_TAX_THRESHOLD = 10_000  # liability below this needs no advance tax


def slab_tax(income, slabs):
    """Tax on `income` under a (upper_bound, rate) table."""
    tax, lower = 0.0, 0
    for upper, rate in slabs:
        if income <= lower:
            break
        top = income if upper is None else min(income, upper)
        tax += (top - lower) * rate
        if upper is None:
            break
        lower = upper
    return tax


def surcharge_rate(total_income, regime):
    rate = 0.0
    for threshold, band in SURCHARGE_BANDS:
        if total_income > threshold:
            rate = band
    if regime == "new":
        rate = min(rate, SURCHARGE_CAP_NEW_REGIME)
    return rate
