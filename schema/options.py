"""
ITR-3 — enumerated options.

Every field in the return that is a choice rather than a number. Keeping them
here means a case file names a constant instead of retyping a string, and a
typo becomes an ImportError rather than a wrong return.
"""

# ---------------------------------------------------------------------------
# Who is filing
# ---------------------------------------------------------------------------

RESIDENTIAL_STATUS = {
    "RES":   "Resident and Ordinarily Resident",
    "RNOR":  "Resident but Not Ordinarily Resident",
    "NRI":   "Non-Resident",
}

AGE_CATEGORY = {
    "below60":     "Below 60 years",
    "senior":      "Senior citizen (60 to 79)",
    "superSenior": "Super senior citizen (80 and above)",
}

# ---------------------------------------------------------------------------
# Which return, under which provision
# ---------------------------------------------------------------------------

FILING_SECTION = {
    "139(1)":    "On or before the due date",
    "139(4)":    "Belated — after the due date, by 31 Dec of the AY",
    "139(5)":    "Revised — corrects an already-filed return",
    "139(8A)":   "Updated (ITR-U) — see UPDATED_RETURN_ADDITIONAL_TAX",
    "142(1)":    "In response to a notice u/s 142(1)",
    "148":       "In response to a notice u/s 148 (income escaping assessment)",
    "153A/153C": "Search or requisition cases",
}

# ITR-U additional tax, on (tax + interest), by when it is filed after the
# end of the relevant assessment year. Finance Act 2025 extended the window
# from 24 to 48 months.
UPDATED_RETURN_ADDITIONAL_TAX = {
    "within_12m": 0.25,
    "12_to_24m":  0.50,
    "24_to_36m":  0.60,
    "36_to_48m":  0.70,
}

# ITR-U is barred where it would produce a refund, reduce liability, or return
# a loss. It requires additional tax to be payable.
UPDATED_RETURN_BLOCKED_WHEN = (
    "results in refund",
    "reduces total tax liability",
    "is a loss return",
    "search/survey proceedings pending for the year",
)

REGIME = {
    "new": "New regime u/s 115BAC — default from AY 2024-25",
    "old": "Old regime — must be opted for; Form 10-IEA where business income",
}

# Business income means the regime choice is not free each year: opting out of
# the new regime needs Form 10-IEA, and the option can be exercised once and
# withdrawn once in a lifetime.
FORM_10IEA_REQUIRED_IF = "opting for OLD regime while having business/professional income"

# ---------------------------------------------------------------------------
# Heads of income
# ---------------------------------------------------------------------------

HEADS = {
    "salary":   "Income from Salary / Pension",
    "hp":       "Income from House Property",
    "bp":       "Profits and Gains from Business or Profession",
    "cg":       "Capital Gains",
    "os":       "Income from Other Sources",
}

HOUSE_PROPERTY_TYPE = {
    "SOP": "Self-occupied — annual value nil; interest capped",
    "LOP": "Let out — actual rent",
    "DLOP": "Deemed let out",
}

# ---------------------------------------------------------------------------
# Presumptive taxation
# ---------------------------------------------------------------------------

PRESUMPTIVE = {
    "44AD": dict(
        applies_to="Eligible business (not profession, agency, commission/brokerage)",
        rate_digital=0.06,
        rate_cash=0.08,
        turnover_limit=2_00_00_000,
        turnover_limit_if_cash_receipts_under_5pct=3_00_00_000,
        note="Declaring below the floor requires books u/s 44AA and audit u/s 44AB. "
             "Opting out after opting in locks you out for 5 assessment years (44AD(4)).",
    ),
    "44ADA": dict(
        applies_to="Specified professions u/s 44AA(1) — legal, medical, engineering, "
                   "architecture, accountancy, technical consultancy, interior "
                   "decoration, and notified professions",
        rate=0.50,
        turnover_limit=50_00_000,
        turnover_limit_if_cash_receipts_under_5pct=75_00_000,
        note="Minimum 50% of gross receipts. Below that, books + audit.",
    ),
    "44AE": dict(
        applies_to="Goods carriages, up to 10 vehicles",
        rate="Per vehicle per month — by gross vehicle weight",
        note="1,000 per tonne per month for heavy goods vehicles; 7,500 otherwise.",
    ),
}

# ---------------------------------------------------------------------------
# Business income that is not presumptive
# ---------------------------------------------------------------------------

BUSINESS_KIND = {
    "speculative":     "Intraday equity — speculative u/s 43(5); loss u/s 73",
    "non_speculative": "F&O / derivatives — non-speculative; loss u/s 72",
    "specified":       "Specified business u/s 35AD; loss u/s 73A",
    "regular":         "Ordinary business or profession with books",
}

# ---------------------------------------------------------------------------
# Capital gains
# ---------------------------------------------------------------------------

CAPITAL_GAIN_TYPE = {
    "stcg_111A":  "STCG on STT-paid equity / equity MF — special rate",
    "stcg_other": "STCG on everything else — taxed at slab",
    "ltcg_112A":  "LTCG on STT-paid equity / equity MF — special rate, annual exemption",
    "ltcg_112":   "LTCG on other assets — special rate",
    "ltcg_115AD": "LTCG for FIIs / specified funds",
}

HOLDING_PERIOD_MONTHS = {
    "listed_securities": 12,
    "unlisted_shares":   24,
    "immovable_property": 24,
    "other_assets":      24,
}

# ---------------------------------------------------------------------------
# Income taxed at special rates (Schedule SI)
# ---------------------------------------------------------------------------

SPECIAL_RATE_SECTIONS = {
    "111A":   dict(rate=0.20, desc="STCG on equity (post 23-07-2024)"),
    "112A":   dict(rate=0.125, desc="LTCG on equity above the annual exemption"),
    "112":    dict(rate=0.125, desc="LTCG on other assets"),
    "115BB":  dict(rate=0.30, desc="Lottery, crossword, card games, gambling"),
    "115BBJ": dict(rate=0.30, desc="Net winnings from online games"),
    "115BBH": dict(rate=0.30, desc="Virtual Digital Assets"),
    "115BBE": dict(rate=0.60, desc="Unexplained cash credits/investments u/s 68-69D "
                                   "— plus 25% surcharge; no deduction, no set-off"),
}

# Rules that bite hardest, kept explicit because they are easy to get wrong.
SPECIAL_RATE_RULES = {
    "115BBH": (
        "Gains only. Loss on one VDA cannot be set off against gain on another, "
        "cannot be set off against any other head, and cannot be carried forward. "
        "No deduction other than cost of acquisition — not even transfer expenses."
    ),
    "115BBJ": (
        "Gross net winnings at 30%. No deduction for losses, entry fees or "
        "deposits. Winnings still count toward total income for the 87A ceiling."
    ),
    "87A_rebate": (
        "Finance Act 2025: rebate u/s 87A is NOT available against income "
        "chargeable at special rates. It applies to slab income only, while the "
        "eligibility threshold is tested on TOTAL income including special-rate "
        "income — so special-rate income can destroy the rebate on slab income."
    ),
}

# ---------------------------------------------------------------------------
# Losses — set-off and carry-forward
# ---------------------------------------------------------------------------

LOSS_CARRY_FORWARD = {
    "71B":  dict(head="House property",          years=8,
                 note="Set-off against other heads capped at 2,00,000 per year"),
    "72":   dict(head="Non-speculative business", years=8,
                 note="Not against salary"),
    "73":   dict(head="Speculative business",     years=4,
                 note="Only against speculative income"),
    "73A":  dict(head="Specified business u/s 35AD", years=None,
                 note="Indefinite; only against specified business income"),
    "74":   dict(head="Capital gains",            years=8,
                 note="STCL against STCG or LTCG; LTCL only against LTCG"),
    "74A":  dict(head="Owning and maintaining race horses", years=4),
}

# Carry-forward of loss is FORFEITED if the return is filed late. Unabsorbed
# depreciation is the exception — it carries forward regardless.
LOSS_CF_REQUIRES_TIMELY_RETURN = True

# ---------------------------------------------------------------------------
# Cash transaction limits — penalties that dwarf ordinary tax
# ---------------------------------------------------------------------------

CASH_LIMITS = {
    "269SS": dict(threshold=20_000, penalty_section="271D",
                  desc="Accepting loan/deposit/specified sum in cash",
                  penalty="Equal to the amount accepted"),
    "269ST": dict(threshold=2_00_000, penalty_section="271DA",
                  desc="RECEIVING cash — per person per day, per transaction, "
                       "or per event/occasion",
                  penalty="Equal to the amount received, on the RECIPIENT",
                  note="No exemption for relatives. A gift that is fully exempt "
                       "u/s 56(2)(x) still breaches 269ST if paid in cash. "
                       "Relief only via the 'good and sufficient reasons' proviso."),
    "269T":  dict(threshold=20_000, penalty_section="271E",
                  desc="Repaying loan/deposit in cash"),
}

# ---------------------------------------------------------------------------
# Gifts — s.56(2)(x)
# ---------------------------------------------------------------------------

GIFT_EXEMPT_RELATIVES = (
    "Spouse",
    "Brother or sister",
    "Brother or sister of the spouse",
    "Brother or sister of either parent",
    "Any lineal ascendant or descendant",
    "Any lineal ascendant or descendant of the spouse",
    "Spouse of any of the above",
)

GIFT_RULES = dict(
    non_relative_threshold=50_000,
    note="Above the threshold the WHOLE amount is taxable under Other Sources, "
         "not merely the excess. Gifts from relatives are exempt without limit, "
         "as are gifts on marriage, under a will, or in contemplation of death. "
         "Exempt gifts are still REPORTABLE in Schedule EI.",
)

# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

TAX_AUDIT_44AB = dict(
    business_turnover=1_00_00_000,
    business_turnover_if_cash_under_5pct=10_00_00_000,
    profession_receipts=75_00_000,
    also_required_when="Declaring below the presumptive floor while income "
                       "exceeds the basic exemption limit",
)
