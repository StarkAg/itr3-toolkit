"""
Tests for the statutory tables.

Run:  python3 -m pytest -q     (or: python3 tests/test_rates.py)

These pin the rules that are easy to get subtly wrong — slab boundaries, the
87A interaction with special-rate income, presumptive floors, and the fact that
a tax-exempt gift can still breach a cash-receipt limit.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "schema"))

import options  # noqa: E402
import rates    # noqa: E402


# --------------------------------------------------------------------------
# Slabs
# --------------------------------------------------------------------------

def test_new_regime_2026_27_slab_boundaries():
    slabs = rates.NEW_REGIME_SLABS["2026-27"]
    assert rates.slab_tax(400_000, slabs) == 0            # exemption edge
    assert rates.slab_tax(800_000, slabs) == 20_000       # 4L @ 5%
    assert rates.slab_tax(1_200_000, slabs) == 60_000     # + 4L @ 10%


def test_top_slab_is_open_ended():
    slabs = rates.NEW_REGIME_SLABS["2026-27"]
    # 30% applies above 24L; 25L should cost 1L more than 24L at 30% on the last lakh
    assert (rates.slab_tax(2_500_000, slabs)
            - rates.slab_tax(2_400_000, slabs)) == 30_000


def test_old_regime_unchanged_across_years():
    assert rates.slab_tax(1_000_000, rates.OLD_REGIME_SLABS) == 112_500


def test_exemption_rises_with_age():
    e = rates.OLD_REGIME_EXEMPTION
    assert e["below60"] < e["senior"] < e["superSenior"]


def test_pre_2023_new_regime_slabs_are_identical_across_its_three_years():
    """115BAC launched in AY 2021-22 with one table that held through AY 2023-24;
    Budget 2023 replaced it starting AY 2024-25. All three early years must
    share the exact same slabs, or one of them has been mistyped."""
    a, b, c = (rates.NEW_REGIME_SLABS[ay] for ay in ("2021-22", "2022-23", "2023-24"))
    assert a == b == c


def test_pre_2023_new_regime_exemption_was_lower_than_todays():
    old = rates.NEW_REGIME_SLABS["2021-22"]
    new = rates.NEW_REGIME_SLABS["2026-27"]
    assert old[0][0] == 2_50_000          # pre-2023: 2.5L exemption
    assert new[0][0] == 4_00_000          # AY 2026-27: 4L exemption
    assert old[0][0] < new[0][0]


def test_pre_2023_new_regime_had_seven_slabs_not_six():
    # The old table stepped 5/10/15/20/25/30; Budget 2023 collapsed it to
    # 5/10/15/20/30 (dropping the 25% step) and moved the boundaries.
    assert len(rates.NEW_REGIME_SLABS["2023-24"]) == 7
    assert len(rates.NEW_REGIME_SLABS["2024-25"]) == 6


# --------------------------------------------------------------------------
# 87A — the interaction that catches people out
# --------------------------------------------------------------------------

def test_87a_threshold_rose_for_2026_27():
    assert rates.REBATE_87A["new"]["2025-26"]["income_limit"] == 700_000
    assert rates.REBATE_87A["new"]["2026-27"]["income_limit"] == 1_200_000
    assert rates.REBATE_87A["new"]["2026-27"]["max_rebate"] == 60_000


def test_pre_2023_new_regime_rebate_matched_the_old_regime():
    """Before Budget 2023 the new regime had no rebate advantage over the old
    one — both were 5,00,000 / 12,500. Easy to assume it was always better."""
    for ay in ("2021-22", "2022-23", "2023-24"):
        assert rates.REBATE_87A["new"][ay] == rates.REBATE_87A["old"]


def test_87a_advantage_for_new_regime_started_ay_2024_25():
    assert (rates.REBATE_87A["new"]["2023-24"]
            != rates.REBATE_87A["new"]["2024-25"])
    assert (rates.REBATE_87A["new"]["2024-25"]["income_limit"]
            > rates.REBATE_87A["old"]["income_limit"])


def test_87a_does_not_cover_special_rate_income():
    """Rebate applies to slab tax only, but the ceiling is tested on TOTAL
    income — so special-rate income can destroy the rebate on slab income."""
    assert rates.REBATE_87A_EXCLUDES_SPECIAL_RATE is True
    assert "special rates" in options.SPECIAL_RATE_RULES["87A_rebate"]


def test_special_rate_income_can_push_past_the_ceiling():
    limit = rates.REBATE_87A["new"]["2026-27"]["income_limit"]
    slab_income, vda = 1_150_000, 100_000
    assert slab_income < limit                       # rebate would apply alone
    assert slab_income + vda > limit                 # together it is lost


# --------------------------------------------------------------------------
# Presumptive floors
# --------------------------------------------------------------------------

def test_presumptive_floors():
    assert options.PRESUMPTIVE["44ADA"]["rate"] == 0.50
    assert options.PRESUMPTIVE["44AD"]["rate_digital"] == 0.06
    assert options.PRESUMPTIVE["44AD"]["rate_cash"] == 0.08


def test_44ada_receipt_ceiling():
    p = options.PRESUMPTIVE["44ADA"]
    assert p["turnover_limit"] == 50_00_000
    assert p["turnover_limit_if_cash_receipts_under_5pct"] == 75_00_000


# --------------------------------------------------------------------------
# Capital gains — the rate change that lands mid-year, not at an AY boundary
# --------------------------------------------------------------------------

def test_capital_gains_rate_rose_on_23_july_2024():
    pre = rates.CAPITAL_GAINS_PERIODS["pre_2024_07_23"]
    post = rates.CAPITAL_GAINS_PERIODS["post_2024_07_23"]
    assert pre["stcg_111A"] == 0.15
    assert post["stcg_111A"] == 0.20
    assert pre["ltcg_112A"] == 0.10
    assert post["ltcg_112A"] == 0.125


def test_ltcg_112a_annual_exemption_rose_with_the_rate_change():
    assert (rates.CAPITAL_GAINS_PERIODS["pre_2024_07_23"]["ltcg_112A_annual_exemption"]
            < rates.CAPITAL_GAINS_PERIODS["post_2024_07_23"]["ltcg_112A_annual_exemption"])


def test_capital_gains_current_alias_matches_post_change_rates():
    assert rates.CAPITAL_GAINS == rates.CAPITAL_GAINS_PERIODS["post_2024_07_23"]


# --------------------------------------------------------------------------
# Special rates and their restrictions
# --------------------------------------------------------------------------

def test_vda_flat_thirty_percent():
    assert options.SPECIAL_RATE_SECTIONS["115BBH"]["rate"] == 0.30


def test_vda_permits_no_set_off():
    rule = options.SPECIAL_RATE_RULES["115BBH"]
    assert "cannot be set off" in rule
    assert "cannot be carried forward" in rule


def test_unexplained_money_is_the_worst_rate():
    rates_by_section = {k: v["rate"] for k, v in options.SPECIAL_RATE_SECTIONS.items()}
    assert rates_by_section["115BBE"] == max(rates_by_section.values())


# --------------------------------------------------------------------------
# Losses
# --------------------------------------------------------------------------

def test_speculative_loss_has_the_shortest_life():
    assert options.LOSS_CARRY_FORWARD["73"]["years"] == 4
    assert options.LOSS_CARRY_FORWARD["72"]["years"] == 8
    assert options.LOSS_CARRY_FORWARD["74"]["years"] == 8


def test_carry_forward_needs_a_timely_return():
    assert options.LOSS_CF_REQUIRES_TIMELY_RETURN is True


# --------------------------------------------------------------------------
# Cash limits — penalties that dwarf the tax
# --------------------------------------------------------------------------

def test_269st_threshold_and_penalty():
    st = options.CASH_LIMITS["269ST"]
    assert st["threshold"] == 2_00_000
    assert st["penalty_section"] == "271DA"
    assert "RECIPIENT" in st["penalty"]


def test_exempt_gift_can_still_breach_269st():
    """s.56(2)(x) exemption and s.269ST are independent questions."""
    assert "No exemption for relatives" in options.CASH_LIMITS["269ST"]["note"]
    assert "lineal ascendant" in " ".join(options.GIFT_EXEMPT_RELATIVES).lower()


def test_non_relative_gift_is_taxable_in_full_above_the_threshold():
    assert options.GIFT_RULES["non_relative_threshold"] == 50_000
    assert "WHOLE amount" in options.GIFT_RULES["note"]


# --------------------------------------------------------------------------
# Chapter VI-A availability under the new regime
# --------------------------------------------------------------------------

def test_new_regime_allows_only_three_via_deductions():
    # 80CCD(2) employer NPS, 80JJAA new employment, 80CCH Agniveer Corpus Fund.
    # A prior version of this test asserted only the first two, which was
    # simply wrong -- 80CCH is allowed under the new regime too. A repo that
    # asserts a false rule is worse than one that omits it.
    assert set(rates.NEW_REGIME_ALLOWS_ONLY) == {"80CCD(2)", "80JJAA", "80CCH"}
    for section in rates.NEW_REGIME_ALLOWS_ONLY:
        assert section in rates.CHAPTER_VIA


def test_80tta_and_80ttb_caps():
    assert rates.CHAPTER_VIA["80TTA"]["cap"] == 10_000
    assert rates.CHAPTER_VIA["80TTB"]["cap"] == 50_000


# --------------------------------------------------------------------------
# Due dates
# --------------------------------------------------------------------------

def test_itr3_non_audit_due_date_differs_from_itr1():
    d = rates.DUE_DATES["2026-27"]
    assert d["itr1_itr2_non_audit"] == "31-07-2026"
    assert d["itr3_itr4_non_audit"] == "31-08-2026"


def test_itr3_itr4_split_did_not_exist_before_2026_27():
    """The forms shared one non-audit date through AY 2025-26; the split is
    new. A case file for an earlier year must not look up the split keys."""
    for ay in ("2023-24", "2024-25", "2025-26"):
        assert "all_non_audit" in rates.DUE_DATES[ay]
        assert "itr1_itr2_non_audit" not in rates.DUE_DATES[ay]


def test_covid_years_are_deliberately_not_hardcoded():
    """AY 2021-22 / 2022-23 due dates were revised multiple times by
    successive CBDT notifications. Asserting one 'statutory' date for those
    years would be more misleading than omitting them."""
    assert "2021-22" not in rates.DUE_DATES
    assert "2022-23" not in rates.DUE_DATES


# --------------------------------------------------------------------------
# Surcharge
# --------------------------------------------------------------------------

def test_surcharge_is_capped_under_the_new_regime():
    income = 6_00_00_000
    assert rates.surcharge_rate(income, "old") == 0.37
    assert rates.surcharge_rate(income, "new") == 0.25


def test_no_surcharge_below_fifty_lakh():
    assert rates.surcharge_rate(49_99_999, "new") == 0


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception:
            failed += 1
            print(f"  FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
