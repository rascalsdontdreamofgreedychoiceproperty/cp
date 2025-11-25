import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--cnf-files",
        action="store",
        default=None,
        help="Comma-separated list of CNF files to benchmark"
    )
