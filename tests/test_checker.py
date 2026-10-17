from decimal import Decimal

import pytest

from converter.checker import InputError, check_input

NOT_A_NUMBER = "Amount must be a number"


@pytest.mark.parametrize(
    "amount, country, message",
    [
        ("abc", "US", NOT_A_NUMBER),
        ("1,000", "US", NOT_A_NUMBER),
        ("1e5", "US", NOT_A_NUMBER),
        (".5", "US", NOT_A_NUMBER),
        ("5.", "US", NOT_A_NUMBER),
        ("+5", "US", NOT_A_NUMBER),
        ("", "US", NOT_A_NUMBER),
        ("nan", "US", NOT_A_NUMBER),
        ("inf", "US", NOT_A_NUMBER),
        ("-1e5", "US", NOT_A_NUMBER),
        ("-abc", "US", NOT_A_NUMBER),
        ("-1,000", "US", NOT_A_NUMBER),
        (" 5", "US", NOT_A_NUMBER),
        ("0", "US", "Amount must be more than 0"),
        ("-5", "CA", "Amount must be more than 0"),
        ("1000001", "US", "Amount must be 1000000 or less"),
        ("100", "UK", "Only US and CA are supported"),
        ("100", "", "Only US and CA are supported"),
    ],
)
def test_checker_rejections(amount, country, message):
    with pytest.raises(InputError) as error:
        check_input(amount, country)
    assert str(error.value) == message


def test_checker_accepts_max_amount():
    assert check_input("1000000", "us") == (Decimal("1000000"), "US")


def test_checker_amount_checked_before_country():
    with pytest.raises(InputError) as error:
        check_input("abc", "UK")
    assert str(error.value) == NOT_A_NUMBER
