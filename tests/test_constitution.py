"""Guard tests for constitution principles I, III and V."""
import ast
import io
import tokenize
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = sorted((ROOT / "converter").glob("*.py"))
NETWORK_MODULES = {"socket", "urllib", "http", "requests", "ftplib", "smtplib", "ssl"}


def test_source_has_no_float():
    for path in SOURCE_FILES:
        source = path.read_text(encoding="utf-8")
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            assert not (
                token.type == tokenize.NAME and token.string == "float"
            ), f"float used in {path.name} line {token.start[0]}"


def test_source_has_no_network_imports():
    for path in SOURCE_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            for module in modules:
                assert (
                    module.split(".")[0] not in NETWORK_MODULES
                ), f"network import {module} in {path.name}"


def test_source_has_no_hard_coded_rates():
    rates = yaml.safe_load((ROOT / "config" / "rates.yaml").read_text(encoding="utf-8"))["rates"]
    rate_values = {Decimal(str(value)) for value in rates.values()}
    for path in SOURCE_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
                continue
            if isinstance(node.value, (int, float)):
                value = Decimal(str(node.value))
            elif isinstance(node.value, str):
                try:
                    value = Decimal(node.value.strip())
                except ArithmeticError:
                    continue
            else:
                continue
            assert value not in rate_values, f"rate value {value} hard-coded in {path.name}"
