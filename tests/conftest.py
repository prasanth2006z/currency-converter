from collections import namedtuple
from pathlib import Path

import pytest

from converter import cli

CliResult = namedtuple("CliResult", "code out err")

DEFAULT_RATES = "rates:\n  US: 90\n  CA: 100\n"


@pytest.fixture
def make_rates_file(tmp_path):
    """Write any YAML text to a temporary rates file and return its path."""
    counter = []

    def make(yaml_text):
        counter.append(1)
        path = tmp_path / f"rates_{len(counter)}.yaml"
        path.write_text(yaml_text, encoding="utf-8")
        return path

    return make


@pytest.fixture
def rates_file(make_rates_file):
    return make_rates_file(DEFAULT_RATES)


@pytest.fixture
def log_path(tmp_path) -> Path:
    # The folder does not exist yet; the program must create it.
    return tmp_path / "logs" / "conversions.log"


@pytest.fixture
def run_cli(capsys, rates_file, log_path):
    """Run converter.cli.main and return exit code, stdout and stderr.

    Pass rates_path or log_path to override the default fixtures.
    """

    def run(*argv, rates_path=None, log=None):
        code = cli.main(
            list(argv),
            rates_path=rates_file if rates_path is None else rates_path,
            log_path=log_path if log is None else log,
        )
        captured = capsys.readouterr()
        return CliResult(code, captured.out, captured.err)

    return run
