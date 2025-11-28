import sys
import os
import copy
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.sudoku.solver import solve_sudoku, example_board
from app.sudoku.backtracking import solve_sudoku as backtracking_solve_sudoku
from parser.cnf_parser import parse_dimacs_cnf


# ============================================================================
# HEURISTIC CONFIGURATIONS
# ============================================================================

# Sudoku heuristic combinations to benchmark
SUDOKU_HEURISTICS = [
    ["unit"],
    ["unit", "pure"],
]

# DPLL heuristic combinations to benchmark
DPLL_HEURISTICS = [
    [],
    ["unit"],
    ["pure"],
    ["unit", "pure"],
]


# ============================================================================
# SUDOKU BENCHMARKS
# ============================================================================

@pytest.mark.benchmark(group="sudoku-dpll")
@pytest.mark.parametrize("heuristics", SUDOKU_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_sudoku_dpll(benchmark, heuristics):
    """Benchmark Sudoku with DPLL solver using various heuristic combinations"""
    board = copy.deepcopy(example_board)
    benchmark(solve_sudoku, board, heuristics)


@pytest.mark.benchmark(group="sudoku-backtracking")
def test_sudoku_backtracking(benchmark):
    """Benchmark Sudoku with backtracking solver"""
    board = copy.deepcopy(example_board)
    benchmark(backtracking_solve_sudoku, board)



# ============================================================================
# DPLL BENCHMARKS
# ============================================================================

def get_cnf_files(config):
    """Get list of CNF files based on command line options"""
    # Check for explicit file list
    cnf_files_option = config.getoption("--cnf-files")
    if cnf_files_option:
        return [f.strip() for f in cnf_files_option.split(",")]
    
    # Otherwise use benchmark mode
    mode = config.getoption("--intensity")
    uf20_dir = os.path.join(root_dir, "tests", "uf20-91")
    
    # Get all files in uf20-91 directory
    all_files = sorted([os.path.join(uf20_dir, f) for f in os.listdir(uf20_dir) if f.endswith(".cnf")])
    
    if mode == "quick":
        # Use every 20th file to get ~50 files
        return all_files[::20]
    else:  # full
        return all_files


def load_cnf(filepath):
    """Load and prepare CNF problem"""
    num_vars, num_clauses, clauses = parse_dimacs_cnf(filepath)
    # Convert integer literals to strings
    clauses_str = [[str(lit) for lit in clause] for clause in clauses]
    vars_list = get_vars(clauses_str)
    return vars_list, clauses_str


@pytest.fixture
def cnf_files(request):
    """Fixture that provides list of CNF files based on benchmark mode"""
    return get_cnf_files(request.config)


@pytest.mark.benchmark(group="dpll")
@pytest.mark.parametrize("heuristics", DPLL_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_dpll(benchmark, cnf_files, heuristics, request):
    """Benchmark DPLL with various heuristic combinations across multiple files"""
    mode = request.config.getoption("--intensity")
    rounds = 20 if mode == "quick" else 1
    
    # Load all problems once
    problems = [load_cnf(filepath) for filepath in cnf_files]
    
    def run_all_problems():
        """Run solver on all problems"""
        for vars_list, clauses_original in problems:
            clauses = copy.deepcopy(clauses_original)
            solve(vars_list, clauses, heuristics)
    
    benchmark.pedantic(run_all_problems, rounds=rounds, iterations=1)




