"""
ITR-3 case file — TEMPLATE.

Copy to `private/inputs.py` and fill in. `private/` is git-ignored, so real
figures never enter version control.

    cp template/inputs.example.py private/inputs.py

Conventions
  - Every figure carries a provenance comment. A number with no provenance does
    not belong in a return.
  - Mark each with CONFIRMED (stated by the assessee or read off a document),
    DERIVED (computed by a script here, reproducible) or DISPUTED (two credible
    values — resolve before filing).
  - `None` means "not yet established" and is reported as [PENDING] on the
    computation sheet rather than silently treated as zero. Set an explicit 0
    only when confirmed nil.

Vocabulary lives in `schema/options.py`; rates in `schema/rates.py`; the list of
schedules in `schema/schedules.py`.
"""

# ---------------------------------------------------------------------------
# Assessee
# ---------------------------------------------------------------------------
PROFILE = dict(
    name="",
    father="",
    addr1="",
    addr2="",
    dob="",                      # dd-mm-yyyy
    pan="",
    aadhaar="",
    mobile="",
    email="",
    status="Individual - Resident",   # options.RESIDENTIAL_STATUS
    age_category="below60",           # options.AGE_CATEGORY
    assessment_year="2026-27",
    financial_year="2025-26",
    py_end="31-03-2026",
    regime="new",                     # options.REGIME
    filing_section="139(1)",          # options.FILING_SECTION
    itr_form="ITR-3",
    due_date="31-08-2026",            # rates.DUE_DATES
)

# ---------------------------------------------------------------------------
# Salary — Schedule S
# ---------------------------------------------------------------------------
SALARY = dict(
    gross_salary=None,
    exempt_allowances=None,      # HRA, LTA etc. — old regime
    # Standard deduction is applied by the engine from rates.STANDARD_DEDUCTION
    professional_tax=None,       # old regime only
)

# ---------------------------------------------------------------------------
# House property — Schedule HP
# ---------------------------------------------------------------------------
# One dict per property. type: options.HOUSE_PROPERTY_TYPE
HOUSE_PROPERTIES = [
    # dict(type="LOP", gross_rent=0, municipal_tax=0, interest_on_loan=0,
    #      co_owner_share=1.0, tenant_pan=""),
]

# ---------------------------------------------------------------------------
# Profession / business — presumptive. Schedule BP
# ---------------------------------------------------------------------------
# section: "44AD" | "44ADA" | "44AE" | None
# Watch the floor: 44ADA needs >= 50% of gross receipts, 44AD >= 6% digital /
# 8% cash. Declaring below it means books u/s 44AA plus audit u/s 44AB.
PROFESSION = dict(
    section=None,
    gross_receipts=None,
    declared_income=None,
    rate=None,
    business_code="",            # ITR nature-of-business code
    business_name="",
    status="",
)

# Regular business with books — leave None when presumptive
REGULAR_BUSINESS = dict(
    turnover=None,
    net_profit=None,
    books_maintained=False,
)

# ---------------------------------------------------------------------------
# Trading — Schedule BP
# ---------------------------------------------------------------------------
# Broker P&L exports routinely span more than one financial year. FILTER BY
# SELL DATE to the year being filed before using any total.
FNO_RESULT = None                # non-speculative; loss carries u/s 72 (8y)
SPECULATIVE_RESULT = None        # intraday; loss carries u/s 73 (4y), speculative only

# ---------------------------------------------------------------------------
# Capital gains — Schedule CG
# ---------------------------------------------------------------------------
STCG_111A = None                 # equity STT-paid — special rate
STCG_OTHER = None                # everything else — slab
LTCG_112A = None                 # equity STT-paid — annual exemption applies
LTCG_OTHER = None                # other assets

# Scrip-wise detail for Schedule 112A, when LTCG u/s 112A is claimed
SCHEDULE_112A_ROWS = []          # dict(isin=, name=, qty=, sale=, cost=, fmv=)

# ---------------------------------------------------------------------------
# Virtual Digital Assets — Schedule VDA, s.115BBH
# ---------------------------------------------------------------------------
# GAINS ONLY. Loss on one VDA cannot offset gain on another, cannot offset any
# other head, and cannot be carried forward. Cost of acquisition is the only
# permitted deduction — transfer expenses are not.
VDA_GAIN = None
VDA_SALE_CONSIDERATION = None
VDA_COST = None
VDA_STATUS = ""
# Date-wise rows: generate with scripts/schedule_vda.py, or list them here.
VDA_ROWS = []

# ---------------------------------------------------------------------------
# Winnings — s.115BB (lottery/gambling) and s.115BBJ (online games)
# ---------------------------------------------------------------------------
# Gross winnings at 30%. No deduction for losses, entry fees or deposits, and
# no set-off. Also counts toward total income for the 87A ceiling, so it can
# destroy the rebate on slab income as well as being taxed itself.
GAMING_WINNINGS = None           # 115BBJ
LOTTERY_WINNINGS = None          # 115BB

# ---------------------------------------------------------------------------
# Other sources — Schedule OS
# ---------------------------------------------------------------------------
SAVINGS_INTEREST = []            # [("S.A/c Interest - <bank>", amount), ...]
FD_INTEREST = []                 # [("FD Interest - <bank>", amount), ...]
DIVIDEND = None
OTHER_INCOME = []                # family pension, taxable gifts, commission
EXEMPT_DEDUCTIONS = []           # amounts netted out of the head (e.g. PPF interest)

# ---------------------------------------------------------------------------
# Exempt income — Schedule EI
# ---------------------------------------------------------------------------
# Exempt is not the same as unreported. Gifts from relatives, agricultural
# income, PPF interest and exempt LTCG all belong here.
#
# CASH RECEIPTS: a gift exempt u/s 56(2)(x) can still breach s.269ST if paid in
# cash — 2,00,000 or more, per person per day / per transaction / per occasion.
# Penalty u/s 271DA equals the amount received, levied on the recipient. There
# is no relative exemption. See schema/options.py CASH_LIMITS.
EXEMPT_INCOME = []               # [("description", amount), ...]

# ---------------------------------------------------------------------------
# Chapter VI-A — Schedule VIA. OLD regime only, bar 80CCD(2) and 80JJAA
# ---------------------------------------------------------------------------
CHAPTER_VIA = dict(
    c80C=None, c80CCD1B=None, c80CCD2=None, c80D=None, c80DD=None, c80DDB=None,
    c80E=None, c80EE=None, c80EEA=None, c80EEB=None, c80G=None, c80GG=None,
    c80GGC=None, c80TTA_TTB=None, c80U=None, c80JJAA=None, c80QQB=None,
    c80RRB=None,
    others=[],
)

# ---------------------------------------------------------------------------
# Brought-forward losses — Schedule BFLA / CFL
# ---------------------------------------------------------------------------
# [(ay, section, amount)] — sections per options.LOSS_CARRY_FORWARD
BROUGHT_FORWARD_LOSSES = []

# ---------------------------------------------------------------------------
# Taxes paid — Schedule TDS / TCS / IT
# ---------------------------------------------------------------------------
# Reconcile against AIS and Form 26AS. AIS rows can be marked Inactive, which
# usually means a duplicate — claim ACTIVE rows only, and re-download AIS
# immediately before filing since it is revised through the year.
TDS_SALARY = None
TDS_OTHER = None
TDS_194S = None                  # VDA
TCS = None
ADVANCE_TAX = None
SELF_ASSESSMENT_TAX = None

# ---------------------------------------------------------------------------
# Foreign — Schedule FA / FSI / TR
# ---------------------------------------------------------------------------
# Schedule FA covers assets held AT ANY TIME during the period, not just at year
# end. Non-disclosure carries a flat 10,00,000 penalty under the Black Money
# Act. Crypto on a foreign exchange is worth an explicit view.
FOREIGN_ASSETS = []
FOREIGN_INCOME = []
FOREIGN_TAX_CREDIT = None

# ---------------------------------------------------------------------------
# Disclosure — Schedule AL / GST
# ---------------------------------------------------------------------------
ASSETS_LIABILITIES = None        # required where total income exceeds 50,00,000
GST_TURNOVER = None              # where registered
GSTIN = ""

# ---------------------------------------------------------------------------
# Bank accounts — for refund, and all accounts held during the year
# ---------------------------------------------------------------------------
BANK_ACCOUNTS = []               # dict(bank=, account=, ifsc=, primary=False)

# ---------------------------------------------------------------------------
# Flags to carry into review — not part of the computation
# ---------------------------------------------------------------------------
# Anything AIS reports that needs an explanation: SFT cash deposits, large
# credits, high-value transactions.
REVIEW_FLAGS = []                # [("description", amount, "status"), ...]
