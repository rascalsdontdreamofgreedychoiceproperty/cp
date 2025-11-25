import sys
import os
import copy
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.sudoku.solver import solve_sudoku, example_board
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

@pytest.mark.benchmark(group="sudoku")
@pytest.mark.parametrize("heuristics", SUDOKU_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_sudoku(benchmark, heuristics):
    """Benchmark Sudoku with various heuristic combinations"""
    board = copy.deepcopy(example_board)
    benchmark(solve_sudoku, board, heuristics)





# ============================================================================
# DPLL BENCHMARKS
# ============================================================================

# Default CNF files for testing
DEFAULT_CNF_FILES = [
    "tests/uf20-91/uf20-01.cnf",
    "tests/purepp.cnf"
]


def pytest_generate_tests(metafunc):
    """Generate test parameters based on command line options or defaults"""
    if "cnf_problem" in metafunc.fixturenames:
        cnf_files_option = metafunc.config.getoption("--cnf-files")
        if cnf_files_option:
            cnf_files = [f.strip() for f in cnf_files_option.split(",")]
        else:
            cnf_files = DEFAULT_CNF_FILES
        
        # Create a group name from the filename for better organization
        def get_group_name(filepath):
            basename = os.path.basename(filepath)
            return f"dpll-{basename}"
        
        metafunc.parametrize(
            "cnf_problem", 
            cnf_files, 
            indirect=True, 
            ids=lambda f: os.path.basename(f)
        )


def load_cnf(filepath):
    """Load and prepare CNF problem"""
    num_vars, num_clauses, clauses = parse_dimacs_cnf(filepath)
    # Convert integer literals to strings
    clauses_str = [[str(lit) for lit in clause] for clause in clauses]
    vars_list = get_vars(clauses_str)
    return vars_list, clauses_str


@pytest.fixture
def cnf_problem(request):
    """Fixture that provides different CNF problems"""
    filepath = request.param
    return load_cnf(filepath), os.path.basename(filepath)


@pytest.mark.benchmark
def test_dpll_none(benchmark, cnf_problem):
    """Benchmark DPLL with no heuristics"""
    (vars_list, clauses_original), filename = cnf_problem
    benchmark.group = f"dpll-{filename}"
    
    def setup():
        return (vars_list, copy.deepcopy(clauses_original), []), {}
    
    benchmark.pedantic(solve, setup=setup, rounds=1000, iterations=1)


@pytest.mark.benchmark
def test_dpll_unit(benchmark, cnf_problem):
    """Benchmark DPLL with unit propagation only"""
    (vars_list, clauses_original), filename = cnf_problem
    benchmark.group = f"dpll-{filename}"
    
    def setup():
        return (vars_list, copy.deepcopy(clauses_original), ["unit"]), {}
    
    benchmark.pedantic(solve, setup=setup, rounds=1000, iterations=1)


@pytest.mark.benchmark
def test_dpll_pure(benchmark, cnf_problem):
    """Benchmark DPLL with pure literal only"""
    (vars_list, clauses_original), filename = cnf_problem
    benchmark.group = f"dpll-{filename}"
    
    def setup():
        return (vars_list, copy.deepcopy(clauses_original), ["pure"]), {}
    
    benchmark.pedantic(solve, setup=setup, rounds=1000, iterations=1)


@pytest.mark.benchmark
def test_dpll_unit_pure(benchmark, cnf_problem):
    """Benchmark DPLL with unit propagation + pure literal"""
    (vars_list, clauses_original), filename = cnf_problem
    benchmark.group = f"dpll-{filename}"
    
    def setup():
        return (vars_list, copy.deepcopy(clauses_original), ["unit", "pure"]), {}
    
    benchmark.pedantic(solve, setup=setup, rounds=1000, iterations=1)




