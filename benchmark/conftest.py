# benchmark/conftest.py
import pytest

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "sat: Pure SAT/DPLL benchmarks")
    config.addinivalue_line("markers", "sudoku: Sudoku benchmarks")
    config.addinivalue_line("markers", "vertexcover: Vertex Cover benchmarks")

def pytest_addoption(parser):
    parser.addoption(
        "--cnf-files",
        action="store",
        default=None,
        help="Comma-separated list of CNF files to benchmark"
    )
    # --- ADDED THIS OPTION ---
    parser.addoption(
        "--sudoku-file",
        action="store",
        default=None, 
        help="Path to the Sudoku CSV dataset"
    )
    # -------------------------
    parser.addoption(
        "--intensity",
        action="store",
        default="quick",
        choices=["quick", "full"],
        help="Benchmark mode: 'quick' (limit iterations) or 'full'"
    )
