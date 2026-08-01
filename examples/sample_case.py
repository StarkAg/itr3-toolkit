"""
Sample case — entirely fictitious. Runs out of the box:

    python3 scripts/computation.py

A freelance consultant filing ITR-3 for AY 2026-27 under the new regime, with
presumptive professional income, a small F&O loss, capital losses to carry
forward, a little crypto, bank interest, and an exempt gift from a relative.

It exercises the awkward interactions on purpose — the 87A rebate wiping slab
tax while special-rate VDA income stays taxable, an F&O loss setting off against
presumptive income, and capital losses that cannot set off at all.

Copy `template/inputs.example.py` for a real case, and keep it out of git.
"""

PROFILE = dict(
    name="A. N. EXAMPLE",
    father="B. N. Example",
    addr1="12 Sample Street",
    addr2="Exampleville, Karnataka - 560001",
    dob="01-01-1995",
    pan="AAAPA0000A",
    aadhaar="0000 0000 0000",
    mobile="9000000000",
    email="example@example.invalid",
    status="Individual - Resident",
    age_category="below60",
    assessment_year="2026-27",
    financial_year="2025-26",
    py_end="31-03-2026",
    regime="new",
    filing_section="139(1)",
    itr_form="ITR-3",
    due_date="31-08-2026",
)

# Profession u/s 44ADA — declared at the 50% statutory floor.
PROFESSION = dict(
    section="44ADA",
    gross_receipts=1400000,
    declared_income=700000,
    rate=0.50,
    business_code="16019",
    business_name="Technical consultancy",
    status="CONFIRMED",
)

# F&O — non-speculative business loss; sets off against presumptive income.
FNO_RESULT = -5000
SPECULATIVE_RESULT = 0

# Equity — small net losses; nil taxable, carried forward u/s 74.
STCG_111A = -200
LTCG_112A = -50

# Crypto u/s 115BBH — gains only, no set-off, taxed at a flat 30%.
VDA_GAIN = 12000
VDA_SALE_CONSIDERATION = 450000
VDA_COST = 438000

# No online-gaming winnings.
GAMING_WINNINGS = 0

SAVINGS_INTEREST = [
    ("S.A/c Interest - Bank A", 3200),
    ("S.A/c Interest - Bank B", 800),
]
FD_INTEREST = [
    ("FD Interest - Bank A", 6500),
]
DIVIDEND = 1500

# Exempt, but still reportable in Schedule EI. Note that a cash gift of
# 2,00,000 or more would breach s.269ST even though it is tax-exempt — this
# one is assumed received by bank transfer.
EXEMPT_INCOME = [
    ("Gift received from father (relative u/s 56(2)(x)) — by bank transfer", 200000),
]

TDS_194S = 450
ADVANCE_TAX = 0
SELF_ASSESSMENT_TAX = 0
