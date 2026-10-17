from decimal import Decimal

from converter.calculator import convert


def test_half_rounds_up():
    # Exact result is 0.135, which must round up to 0.14.
    assert convert(Decimal("0.0015"), Decimal("90")) == Decimal("0.14")


def test_exact_for_long_amounts():
    # 0.0014999...9 (30 nines) * 90 is just below the 0.135 tie. A multiplication
    # rounded to the default 28 digits would land on the tie and wrongly give 0.14.
    just_below = Decimal("0.0014" + "9" * 30)
    assert convert(just_below, Decimal("90")) == Decimal("0.13")
