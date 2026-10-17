from decimal import ROUND_HALF_UP, Decimal, localcontext

CENT = Decimal("0.01")


def convert(amount, rate):
    """Return amount * rate in INR, rounded half up to 2 decimals."""
    digits = len(amount.as_tuple().digits) + len(rate.as_tuple().digits)
    with localcontext() as context:
        # Enough precision that the product is exact; only the final rounding rounds.
        context.prec = digits + 5
        return (amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)
