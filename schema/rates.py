"""
Statutory rates by assessment year and regime.

Add a new AY by adding a dict — no other file should need editing.
Sources: Finance Act 2024 (AY 2025-26), Finance Act 2025 (AY 2026-27).
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

NEW_REGIME_SLABS = {
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

# ---------------------------------------------------------------------------
# Rebate u/s 87A
# ---------------------------------------------------------------------------
# The threshold is tested on TOTAL income (including special-rate income), but
# the rebate itself is allowed only against SLAB tax. Finance Act 2025 put the
# exclusion of special-rate income beyond argument.

REBATE_87A = {
    "old": dict(income_limit=5_00_000, max_rebate=12_500),
    "new": {
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
    "old": 50_000,
    "new": {"2024-25": 50_000, "2025-26": 75_000, "2026-27": 75_000},
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
# Capital gains — rates current from 23 July 2024
# ---------------------------------------------------------------------------

CAPITAL_GAINS = dict(
    stcg_111A=0.20,
    ltcg_112A=0.125,
    ltcg_112A_annual_exemption=1_25_000,
    ltcg_112=0.125,
    indexation="Withdrawn from 23-07-2024. Resident individuals may elect the "
               "pre-amendment 20%-with-indexation for immovable property "
               "acquired before that date.",
)

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
}

NEW_REGIME_ALLOWS_ONLY = ("80CCD(2)", "80JJAA")

# ---------------------------------------------------------------------------
# Due dates
# ---------------------------------------------------------------------------
# Finance Act 2026 moved non-audit ITR-3/ITR-4 to 31 August permanently. It is
# not an extension, and it does not apply to ITR-1/ITR-2.

DUE_DATES = {
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
