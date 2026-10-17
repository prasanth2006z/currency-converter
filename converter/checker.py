import re
from decimal import Decimal

SUPPORTED_COUNTRIES = ("US", "CA")
MAX_AMOUNT = Decimal("1000000")
AMOUNT_PATTERN = re.compile(r"-?[0-9]+(\.[0-9]+)?")


class InputError(Exception):
    """Invalid user input; the message is shown to the user."""


def check_input(amount_text, country_text):
    """Return (amount, country) for valid input, or raise InputError.

    Checked in this order: amount is a number, more than 0, at most the maximum,
    then the country. The first failure is the one reported.
    """
    if not AMOUNT_PATTERN.fullmatch(amount_text):
        raise InputError("Amount must be a number")
    amount = Decimal(amount_text)
    if amount <= 0:
        raise InputError("Amount must be more than 0")
    if amount > MAX_AMOUNT:
        raise InputError("Amount must be 1000000 or less")
    country = country_text.upper()
    if country not in SUPPORTED_COUNTRIES:
        raise InputError("Only US and CA are supported")
    return amount, country
