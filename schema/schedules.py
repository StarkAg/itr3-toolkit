"""
ITR-3 — the schedules, in filing order.

Each entry says what the schedule is for and when it applies, so a case file can
be checked against the list rather than against memory. `applies_when` is prose,
not a predicate — the judgement stays with the filer.
"""

PART_A = {
    "GEN":     "General information — PAN, Aadhaar, address, filing section, "
               "regime, residential status, nature of business, audit info",
    "BS":      "Balance sheet as at year end. Presumptive filers complete only "
               "the 'no account case' fields",
    "MANUFAC": "Manufacturing account — opening/closing stock, cost of goods",
    "TRADING": "Trading account — turnover, purchases, gross profit",
    "P&L":     "Profit and loss account. Presumptive filers use the 'no account "
               "case' block only",
    "OI":      "Other information — method of accounting, valuation, 43B items, "
               "amounts disallowable",
    "QD":      "Quantitative details of principal goods traded or manufactured",
}

SCHEDULES = {
    # ---- heads of income -------------------------------------------------
    "S":        dict(name="Salary",
                     applies_when="Any salary or pension income"),
    "HP":       dict(name="House Property",
                     applies_when="Any let-out, deemed let-out or self-occupied "
                                  "property; also where only loan interest is claimed"),
    "BP":       dict(name="Business or Profession",
                     applies_when="Always in ITR-3. Carries presumptive income "
                                  "(44AD/44ADA/44AE), F&O and speculative results"),
    "CG":       dict(name="Capital Gains",
                     applies_when="Any transfer of a capital asset"),
    "112A":     dict(name="LTCG on equity — scrip-wise",
                     applies_when="LTCG u/s 112A is claimed; ISIN-level detail"),
    "115AD":    dict(name="LTCG for FII / specified fund",
                     applies_when="Non-resident institutional investors"),
    "VDA":      dict(name="Virtual Digital Assets",
                     applies_when="Any transfer of crypto or other VDA. Date-wise: "
                                  "acquisition date, transfer date, cost, "
                                  "consideration, income per transfer"),
    "OS":       dict(name="Other Sources",
                     applies_when="Interest, dividend, family pension, gifts "
                                  "taxable u/s 56(2)(x), winnings"),

    # ---- depreciation ----------------------------------------------------
    "DPM":      dict(name="Depreciation on plant and machinery",
                     applies_when="Books maintained with depreciable assets"),
    "DOA":      dict(name="Depreciation on other assets",
                     applies_when="Buildings, furniture, intangibles"),
    "DEP":      dict(name="Summary of depreciation", applies_when="With DPM/DOA"),
    "DCG":      dict(name="Deemed capital gain on sale of depreciable assets",
                     applies_when="Block of assets sold"),
    "ESR":      dict(name="Deduction u/s 35 — scientific research",
                     applies_when="Research expenditure claimed"),

    # ---- loss handling ---------------------------------------------------
    "CYLA":     dict(name="Current year loss adjustment",
                     applies_when="Any loss set off within the current year"),
    "BFLA":     dict(name="Brought forward loss adjustment",
                     applies_when="Losses carried in from earlier years"),
    "CFL":      dict(name="Carry forward of losses",
                     applies_when="Any loss to carry to later years. FORFEITED "
                                  "if the return is belated"),
    "UD":       dict(name="Unabsorbed depreciation",
                     applies_when="Depreciation not absorbed; carries forward "
                                  "indefinitely and survives a belated return"),

    # ---- deductions ------------------------------------------------------
    "VIA":      dict(name="Chapter VI-A deductions",
                     applies_when="OLD regime only, apart from 80CCD(2) and 80JJAA"),
    "80G":      dict(name="Donations", applies_when="80G claimed; donee-wise"),
    "80GGA":    dict(name="Donations for research / rural development",
                     applies_when="80GGA claimed"),
    "80GGC":    dict(name="Contribution to political parties",
                     applies_when="80GGC claimed"),
    "80-IA":    dict(name="Infrastructure undertakings", applies_when="Claimed"),
    "80-IB":    dict(name="Certain industrial undertakings", applies_when="Claimed"),
    "80-IC/IE": dict(name="Special category states", applies_when="Claimed"),
    "10AA":     dict(name="SEZ units", applies_when="Claimed"),

    # ---- special computations -------------------------------------------
    "SI":       dict(name="Income chargeable at special rates",
                     applies_when="Any 111A / 112A / 112 / 115BB / 115BBH / "
                                  "115BBJ / 115BBE income"),
    "EI":       dict(name="Exempt income",
                     applies_when="Agricultural income, PPF interest, exempt "
                                  "gifts from relatives, exempt LTCG, dividends "
                                  "exempt in the donee's hands. Reported, not taxed"),
    "PTI":      dict(name="Pass-through income",
                     applies_when="Business trust or investment fund units"),
    "SPI":      dict(name="Income of specified persons",
                     applies_when="Spouse or minor child income clubbed u/s 64"),
    "AMT":      dict(name="Alternate Minimum Tax",
                     applies_when="Old regime with 10AA / 80-IA-series claims"),
    "AMTC":     dict(name="AMT credit", applies_when="AMT paid in an earlier year"),
    "ICDS":     dict(name="ICDS adjustments",
                     applies_when="Books maintained; effect of income computation "
                                  "and disclosure standards"),
    "TPSA":     dict(name="Secondary adjustment to transfer price",
                     applies_when="Transfer pricing adjustment u/s 92CE"),
    "5A":       dict(name="Apportionment between spouses",
                     applies_when="Portuguese Civil Code — Goa, Daman and Diu"),

    # ---- foreign ---------------------------------------------------------
    "FSI":      dict(name="Foreign source income",
                     applies_when="Any income earned outside India"),
    "TR":       dict(name="Tax relief u/s 90 / 90A / 91",
                     applies_when="Foreign tax credit claimed"),
    "FA":       dict(name="Foreign assets",
                     applies_when="Any foreign asset or account held AT ANY TIME "
                                  "during the period — not just at year end. "
                                  "Non-disclosure: flat 10,00,000 penalty under "
                                  "the Black Money Act. Consider whether crypto "
                                  "held on a foreign exchange qualifies"),

    # ---- disclosure ------------------------------------------------------
    "AL":       dict(name="Assets and liabilities",
                     applies_when="Total income exceeds 50,00,000"),
    "GST":      dict(name="GST turnover",
                     applies_when="Registered under GST — turnover as reported "
                                  "in GST returns"),

    # ---- taxes paid ------------------------------------------------------
    "TDS1":     dict(name="TDS on salary", applies_when="Form 16"),
    "TDS2":     dict(name="TDS other than salary",
                     applies_when="Form 16A — interest, professional fees, 194S "
                                  "on VDA. Claim ACTIVE AIS rows only"),
    "TDS3":     dict(name="TDS u/s 194IA / 194IB / 194M / 194S (Form 26QB etc.)",
                     applies_when="Deducted by a non-TAN deductor"),
    "TCS":      dict(name="Tax collected at source",
                     applies_when="Form 27D — LRS remittances, foreign travel"),
    "IT":       dict(name="Advance tax and self-assessment tax",
                     applies_when="Any challan paid; BSR code, date, serial"),
}

PART_B = {
    "TI":  "Total income — aggregation of the heads after set-off and Chapter VI-A",
    "TTI": "Computation of tax liability — slab tax, special-rate tax, surcharge, "
           "marginal relief, 87A rebate, cess, relief u/s 89/90/91, interest u/s "
           "234A/234B/234C, fee u/s 234F, taxes paid, and the balance",
}

VERIFICATION = (
    "A return is not filed until it is verified. Aadhaar OTP is the fastest "
    "route; net-banking EVC and a signed ITR-V by post also work. The window is "
    "30 days from transmission — miss it and the return is treated as never filed."
)

INTEREST_AND_FEE = {
    "234A": "1% per month on unpaid tax — for filing late",
    "234B": "1% per month — advance tax under 90% of assessed tax",
    "234C": "1% per month — advance tax instalments deferred",
    "234F": "5,000 late fee; 1,000 where total income is at or below 5,00,000",
}
