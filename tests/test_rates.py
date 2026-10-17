from decimal import Decimal

import pytest

from converter.rates import RatesError, load_rates


def test_load_rates_returns_file_values(rates_file, make_rates_file):
    assert load_rates(rates_file) == {"US": Decimal("90"), "CA": Decimal("100")}
    other = make_rates_file("rates:\n  US: 80\n  CA: 75.5\n")
    assert load_rates(other) == {"US": Decimal("80"), "CA": Decimal("75.5")}


@pytest.mark.parametrize(
    "yaml_text",
    [
        pytest.param(None, id="missing_file"),
        pytest.param("rates: [unclosed\n  US: 90", id="invalid_yaml"),
        pytest.param("other: 1\n", id="no_rates_map"),
        pytest.param("rates: 5\n", id="rates_not_a_map"),
        pytest.param("", id="empty_file"),
        pytest.param("rates:\n  CA: 100\n", id="missing_us"),
        pytest.param("rates:\n  US: 90\n", id="missing_ca"),
        pytest.param("rates:\n  US: 90\n  CA: 100\n  UK: 50\n", id="extra_country"),
        pytest.param("rates:\n  US: 0\n  CA: 100\n", id="zero_rate"),
        pytest.param("rates:\n  US: 90\n  CA: -1\n", id="negative_rate"),
        pytest.param("rates:\n  US: abc\n  CA: 100\n", id="text_rate"),
        pytest.param("rates:\n  US: true\n  CA: 100\n", id="boolean_rate"),
        pytest.param("rates:\n  US:\n  CA: 100\n", id="empty_rate"),
        pytest.param("rates:\n  US: .inf\n  CA: 100\n", id="infinite_rate"),
        pytest.param("rates:\n  US: .nan\n  CA: 100\n", id="nan_rate"),
    ],
)
def test_rates_error_cases(yaml_text, make_rates_file, tmp_path):
    path = tmp_path / "missing.yaml" if yaml_text is None else make_rates_file(yaml_text)
    with pytest.raises(RatesError):
        load_rates(path)


def test_unreadable_rates_path_raises(tmp_path):
    # A folder cannot be read as a file.
    with pytest.raises(RatesError):
        load_rates(tmp_path)
