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


# --------------------------------------------------------------------------
# 87A — the interaction that catches people out
# --------------------------------------------------------------------------

def test_87a_threshold_rose_for_2026_27():
    assert rates.REBATE_87A["new"]["2025-26"]["income_limit"] == 700_000
    assert rates.REBATE_87A["new"]["2026-27"]["income_limit"] == 1_200_000
    assert rates.REBATE_87A["new"]["2026-27"]["max_rebate"] == 60_000


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

def test_new_regime_allows_only_two_via_deductions():
    assert set(rates.NEW_REGIME_ALLOWS_ONLY) == {"80CCD(2)", "80JJAA"}
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
