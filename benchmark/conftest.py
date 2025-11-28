import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--cnf-files",
        action="store",
        default=None,
        help="Comma-separated list of CNF files to benchmark"
    )
    parser.addoption(
        "--intensity",
        action="store",
        default="quick",
        choices=["quick", "full"],
        help="Benchmark mode: 'quick' (50 files, 20 rounds) or 'full' (all files, 1 round)"
    )
