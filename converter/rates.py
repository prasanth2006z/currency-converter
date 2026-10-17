import numbers
from decimal import Decimal
from pathlib import Path

import yaml

from converter.checker import SUPPORTED_COUNTRIES

DEFAULT_RATES_PATH = Path(__file__).resolve().parent.parent / "config" / "rates.yaml"


class RatesError(Exception):
    """The rates file is missing, unreadable or invalid."""


def _to_rate(value):
    # bool is a subclass of int, so it must be rejected first.
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise RatesError("rate is not a number")
    rate = Decimal(str(value))
    if not rate.is_finite() or rate <= 0:
        raise RatesError("rate must be a number greater than 0")
    return rate


def load_rates(path=None):
    """Return {country: rate}; raise RatesError if the file is not valid."""
    path = DEFAULT_RATES_PATH if path is None else path
    try:
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise RatesError(str(error)) from error
    rates = data.get("rates") if isinstance(data, dict) else None
    if not isinstance(rates, dict) or set(rates) != set(SUPPORTED_COUNTRIES):
        raise RatesError("rates must contain exactly US and CA")
    return {country: _to_rate(value) for country, value in rates.items()}
