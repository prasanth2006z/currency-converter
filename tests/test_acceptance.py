"""Spec examples run through converter.cli.main."""
from datetime import datetime, timedelta


def assert_result(result, expected):
    assert result.code == 0
    assert result.out == f"{expected} INR\n"


# --- User Story 1: convert ---------------------------------------------------


def test_100_us_gives_9000_00(run_cli):
    assert_result(run_cli("100", "US"), "9000.00")


def test_100_ca_gives_10000_00(run_cli):
    assert_result(run_cli("100", "CA"), "10000.00")


def test_2_50_us_gives_225_00(run_cli):
    assert_result(run_cli("2.50", "US"), "225.00")


def test_lowercase_country_accepted(run_cli):
    assert_result(run_cli("100", "us"), "9000.00")


def test_mixed_case_country_accepted(run_cli):
    assert_result(run_cli("100", "Ca"), "10000.00")


def test_max_amount_us_no_thousands_separator(run_cli):
    assert_result(run_cli("1000000", "US"), "90000000.00")


def test_max_amount_ca_no_thousands_separator(run_cli):
    assert_result(run_cli("1000000", "CA"), "100000000.00")


def test_extra_decimals_converted_exactly(run_cli):
    assert_result(run_cli("2.505", "US"), "225.45")


def test_smallest_convertible_amount_gives_0_01(run_cli):
    assert_result(run_cli("0.00006", "US"), "0.01")


def test_rates_come_from_rates_file(run_cli, make_rates_file):
    changed = make_rates_file("rates:\n  US: 80\n  CA: 100\n")
    assert_result(run_cli("100", "US", rates_path=changed), "8000.00")


# --- User Story 2: clear errors ----------------------------------------------

NOT_A_NUMBER = "Amount must be a number"
MORE_THAN_ZERO = "Amount must be more than 0"
RATES_UNAVAILABLE = "Rates are unavailable"

INVALID_EXAMPLES = [
    ("100", "UK"),
    ("0", "US"),
    ("-5", "CA"),
    ("abc", "US"),
    ("1000001", "US"),
    ("1,000", "US"),
    ("1e5", "US"),
    (".5", "US"),
    ("5.", "US"),
    ("+5", "US"),
    ("-1e5", "US"),
    ("-abc", "US"),
    ("-1,000", "US"),
    ("0.00001", "US"),
    ("", "US"),
    ("100", ""),
    ("abc", "UK"),
]


def assert_error(result, message):
    assert result.code == 1
    assert result.out == ""
    assert result.err == f"{message}\n"


def test_unsupported_country_error(run_cli):
    assert_error(run_cli("100", "UK"), "Only US and CA are supported")


def test_zero_amount_error(run_cli):
    assert_error(run_cli("0", "US"), MORE_THAN_ZERO)


def test_negative_amount_error(run_cli):
    assert_error(run_cli("-5", "CA"), MORE_THAN_ZERO)


def test_non_numeric_amount_error(run_cli):
    assert_error(run_cli("abc", "US"), NOT_A_NUMBER)


def test_amount_over_maximum_error(run_cli):
    assert_error(run_cli("1000001", "US"), "Amount must be 1000000 or less")


def test_comma_amount_error(run_cli):
    assert_error(run_cli("1,000", "US"), NOT_A_NUMBER)


def test_scientific_notation_error(run_cli):
    assert_error(run_cli("1e5", "US"), NOT_A_NUMBER)


def test_leading_dot_amount_error(run_cli):
    assert_error(run_cli(".5", "US"), NOT_A_NUMBER)


def test_trailing_dot_amount_error(run_cli):
    assert_error(run_cli("5.", "US"), NOT_A_NUMBER)


def test_plus_sign_amount_error(run_cli):
    assert_error(run_cli("+5", "US"), NOT_A_NUMBER)


def test_empty_amount_error(run_cli):
    assert_error(run_cli("", "US"), NOT_A_NUMBER)


def test_empty_country_error(run_cli):
    assert_error(run_cli("100", ""), "Only US and CA are supported")


def test_amount_error_wins_over_country_error(run_cli):
    assert_error(run_cli("abc", "UK"), NOT_A_NUMBER)


def test_dash_scientific_notation_is_amount_error(run_cli):
    assert_error(run_cli("-1e5", "US"), NOT_A_NUMBER)


def test_dash_text_is_amount_error(run_cli):
    assert_error(run_cli("-abc", "US"), NOT_A_NUMBER)


def test_dash_comma_is_amount_error(run_cli):
    assert_error(run_cli("-1,000", "US"), NOT_A_NUMBER)


def test_amount_too_small_error(run_cli):
    assert_error(run_cli("0.00001", "US"), "Amount is too small to convert")


def test_amount_error_wins_over_missing_rates(run_cli, tmp_path):
    result = run_cli("abc", "US", rates_path=tmp_path / "missing.yaml")
    assert_error(result, NOT_A_NUMBER)


def test_missing_rates_file_shows_error(run_cli, tmp_path):
    assert_error(run_cli("100", "US", rates_path=tmp_path / "missing.yaml"), RATES_UNAVAILABLE)


def test_unreadable_rates_file_shows_error(run_cli, tmp_path):
    # A folder cannot be read as a file.
    assert_error(run_cli("100", "US", rates_path=tmp_path), RATES_UNAVAILABLE)


def test_invalid_yaml_rates_file_shows_error(run_cli, make_rates_file):
    broken = make_rates_file("rates: [unclosed\n  US: 90")
    assert_error(run_cli("100", "US", rates_path=broken), RATES_UNAVAILABLE)


def test_rates_file_missing_country_shows_error(run_cli, make_rates_file):
    only_us = make_rates_file("rates:\n  US: 90\n")
    assert_error(run_cli("100", "US", rates_path=only_us), RATES_UNAVAILABLE)


def test_rates_file_extra_country_shows_error(run_cli, make_rates_file):
    extra = make_rates_file("rates:\n  US: 90\n  CA: 100\n  UK: 50\n")
    assert_error(run_cli("100", "US", rates_path=extra), RATES_UNAVAILABLE)


def test_zero_rate_shows_error(run_cli, make_rates_file):
    zero = make_rates_file("rates:\n  US: 0\n  CA: 100\n")
    assert_error(run_cli("100", "US", rates_path=zero), RATES_UNAVAILABLE)


def test_negative_rate_shows_error(run_cli, make_rates_file):
    negative = make_rates_file("rates:\n  US: -90\n  CA: 100\n")
    assert_error(run_cli("100", "US", rates_path=negative), RATES_UNAVAILABLE)


def test_non_numeric_rate_shows_error(run_cli, make_rates_file):
    for bad in ("abc", "true", "", ".inf", ".nan"):
        path = make_rates_file(f"rates:\n  US: {bad}\n  CA: 100\n")
        assert_error(run_cli("100", "US", rates_path=path), RATES_UNAVAILABLE)


def test_no_inr_amount_in_any_error_output(run_cli):
    for amount, country in INVALID_EXAMPLES:
        result = run_cli(amount, country)
        assert result.out == "", (amount, country)
        assert "INR" not in result.err, (amount, country)
        assert result.code == 1, (amount, country)


# --- User Story 3: conversions are recorded ----------------------------------


def test_successful_conversion_is_logged(run_cli, log_path):
    assert_result(run_cli("2.50", "us"), "225.00")
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    timestamp, amount, country, result = lines[0].split(" | ")
    assert datetime.fromisoformat(timestamp).utcoffset() == timedelta(0)
    assert (amount, country, result) == ("2.50", "US", "225.00")


def test_log_file_and_folder_created_on_first_use(run_cli, log_path):
    assert not log_path.parent.exists()
    run_cli("100", "US")
    assert log_path.is_file()


def test_each_conversion_adds_one_line(run_cli, log_path):
    run_cli("100", "US")
    run_cli("100", "CA")
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 2


def test_failed_conversion_is_not_logged(run_cli, log_path):
    run_cli("100", "UK")
    assert not log_path.exists()


def test_too_small_conversion_is_not_logged(run_cli, log_path):
    run_cli("0.00001", "US")
    assert not log_path.exists()


def test_log_write_failure_shows_error_and_no_result(run_cli, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a folder")
    # The log folder would have to be created inside a file, which is impossible.
    assert_error(
        run_cli("100", "US", log=blocker / "conversions.log"),
        "Could not write the conversion log",
    )


# --- Leading zeros (spec edge case) ------------------------------------------


def test_leading_zeros_amount_accepted(run_cli):
    assert_result(run_cli("00005", "US"), "450.00")
    assert_result(run_cli("007.5", "CA"), "750.00")
    assert_error(run_cli("000", "US"), MORE_THAN_ZERO)
