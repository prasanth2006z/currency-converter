import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from converter.calculator import convert
from converter.checker import InputError, check_input
from converter.rates import DEFAULT_RATES_PATH, RatesError, load_rates

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "conversions.log"


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m converter")
    parser.add_argument("amount", help="dollar amount")
    parser.add_argument("country", help="US or CA")
    return parser


def parse_arguments(argv):
    # After "--" every argument is positional, so an amount such as -5 or -1e5
    # is always the amount and never a command-line option.
    if "-h" not in argv and "--help" not in argv:
        argv = ["--", *argv]
    return build_parser().parse_args(argv)


def convert_amount(args, rates_path):
    """Check input, read rates, calculate. Return (country, result).

    Raises InputError or RatesError.
    """
    amount, country = check_input(args.amount, args.country)
    rates = load_rates(rates_path)
    result = convert(amount, rates[country])
    if result == 0:
        raise InputError("Amount is too small to convert")
    return country, result


def write_log_line(log_path, amount_text, country, result):
    """Append one line: UTC ISO time | amount as entered | country | result."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    line = " | ".join([timestamp, amount_text, country, format(result, "f")])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main(argv=None, rates_path=None, log_path=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        args = parse_arguments(argv)
    except SystemExit as exit_:
        return exit_.code or 0
    try:
        country, result = convert_amount(
            args, DEFAULT_RATES_PATH if rates_path is None else rates_path
        )
    except InputError as error:
        print(error, file=sys.stderr)
        return 1
    except RatesError:
        print("Rates are unavailable", file=sys.stderr)
        return 1
    # Log before showing the result, so a shown result always has a log record.
    try:
        write_log_line(
            Path(DEFAULT_LOG_PATH if log_path is None else log_path), args.amount, country, result
        )
    except OSError:
        print("Could not write the conversion log", file=sys.stderr)
        return 1
    print(f"{format(result, 'f')} INR")
    return 0
