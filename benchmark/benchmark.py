import sys
import os
import copy
import pytest
import pdb

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.sudoku.solver import solve_sudoku, example_board
from app.sudoku.backtracking import solve_sudoku as backtracking_solve_sudoku
from app.vertexcover.solver import solve_vertex_cover
from app.vertexcover.backtracking import find_minimum_vertex_cover as backtracking_solve_vertex_cover
from app.battleship.solver import solve_battleship
from app.battleship.backtracking import solve_battleship as backtracking_solve_battleship
from app.battleship.backtracking import UNKNOWN, WATER, SHIP
from parser.cnf_parser import parse_dimacs_cnf
from parser.sudoku_parser import parse_sudoku_csv
from parser.clq_parser import parse_dimacs_clq
from parser.battleship_parser import parse_battleship_csv

# ============================================================================
# HEURISTIC CONFIGURATIONS
# ============================================================================

# Sudoku heuristic combinations to benchmark
SUDOKU_HEURISTICS = [
    ["unit"],
    ["unit", "pure"],
    ["vsids"],
    ["2wl"],
    ["2wli"],
    ["restarts"],
]

# Battleship heuristic combinations to benchmark
BATTLESHIP_HEURISTICS = [
    ["unit"],
    ["unit", "pure"],
    ["vsids"],
    ["2wl"],
    ["2wli"],
    ["restarts"],
]

# Vertex Cover heuristic combinations to benchmark
VERTEXCOVER_HEURISTICS = [
    [],
    ["unit"],
    ["2wl"],
    ["2wli"],
    ["restarts"],
    ["vsids"],
    ["pure"],
    ["unit", "pure"],
]

# DPLL heuristic combinations to benchmark
DPLL_HEURISTICS = [
    [],
    ["unit"],
    ["2wl"],
    ["2wli"],
    ["restarts"],
    ["vsids"],
    ["pure"],
    ["unit", "pure"],
]


# ============================================================================
# SUDOKU BENCHMARKS
# ============================================================================

@pytest.fixture
def sudoku_puzzles(request):
    """Fixture to load Sudoku puzzles from CSV"""
    intensity = request.config.getoption("--intensity")
    
    # 1. Check if user provided a file via command line
    filepath = request.config.getoption("--sudoku-file")
    
    # 2. If NOT provided, automatically find it in the tests/sudoku folder
    if filepath is None:
        # root_dir is already defined at the top of your file
        filepath = os.path.join(root_dir, "tests", "sudoku", "small_sudoku.csv")
    
    # 3. Check if file exists
    if not os.path.exists(filepath):
        print(f"\nWarning: Dataset not found at {filepath}")
        print("Falling back to single example board.")
        return [example_board]
    
    # 4. Parse the file
    limit = 10 if intensity == "quick" else None
    return parse_sudoku_csv(filepath, limit=limit)

@pytest.mark.sudoku
@pytest.mark.benchmark(group="sudoku-dpll")
@pytest.mark.parametrize("heuristics", SUDOKU_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_sudoku_dpll(benchmark, sudoku_puzzles, heuristics):
    """Benchmark Sudoku DPLL on the dataset"""
    
    # We define a function that runs ALL loaded puzzles sequentially.
    # The benchmark will measure how long it takes to process the whole batch.
    def run_all_sudokus():
        for board in sudoku_puzzles:
            # IMPORTANT: Deepcopy board because solvers modify it in-place
            board_copy = copy.deepcopy(board)
            solve_sudoku(board_copy, heuristics)

    # Increase rounds for more accurate measurements
    benchmark.pedantic(run_all_sudokus, rounds=5, iterations=1)


@pytest.mark.sudoku
@pytest.mark.benchmark(group="sudoku-backtracking")
def test_sudoku_backtracking(benchmark, sudoku_puzzles):
    """Benchmark Sudoku Backtracking on the dataset"""
    
    def run_all_sudokus():
        for board in sudoku_puzzles:
            board_copy = copy.deepcopy(board)
            backtracking_solve_sudoku(board_copy)

    benchmark.pedantic(run_all_sudokus, rounds=1, iterations=1)


# ============================================================================
# BATTLESHIP BENCHMARKS
# ============================================================================

@pytest.fixture
def battleship_puzzles(request):
    """Fixture to load Battleship puzzles from CSV"""
    intensity = request.config.getoption("--intensity")
    
    # 1. Check if user provided a file via command line (assuming standard naming convention)
    # Note: If --battleship-file isn't in conftest.py, this might return None, 
    # so we fallback to the default path logic below.
    try:
        filepath = request.config.getoption("--battleship-file")
    except ValueError:
        filepath = None
    
    # 2. If NOT provided, automatically find it in the tests/battleship folder or root
    if filepath is None:
        # Check standard location
        filepath = os.path.join(root_dir, "tests", "battleship", "battleship.csv")
        # Fallback to root or uploaded location if needed
        if not os.path.exists(filepath):
             filepath = os.path.join(root_dir, "battleship.csv")
    
    # 3. Check if file exists
    if not os.path.exists(filepath):
        print(f"\nWarning: Battleship dataset not found at {filepath}")
        return []
    
    # 4. Parse the file
    limit = 10 if intensity == "quick" else None
    raw_puzzles = parse_battleship_csv(filepath, limit=limit)
    
    # 5. Convert raw characters to solver constants (UNKNOWN, WATER, SHIP)
    processed_puzzles = []
    for (grid_chars, fleet) in raw_puzzles:
        board = []
        for row in grid_chars:
            converted_row = []
            for char in row:
                if char == '.':
                    converted_row.append(WATER)
                elif char == 'X':
                    converted_row.append(SHIP)
                else:
                    converted_row.append(UNKNOWN)
            board.append(converted_row)
        processed_puzzles.append((board, fleet))
        
    return processed_puzzles

@pytest.mark.battleship
@pytest.mark.benchmark(group="battleship-dpll")
@pytest.mark.parametrize("heuristics", BATTLESHIP_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_battleship_dpll(benchmark, battleship_puzzles, heuristics):
    """Benchmark Battleship DPLL on the dataset"""
    
    def run_all_battleships():
        for board, fleet in battleship_puzzles:
            board_copy = copy.deepcopy(board)
            solve_battleship(board_copy, fleet, heuristics)

    benchmark.pedantic(run_all_battleships, rounds=5, iterations=1)

@pytest.mark.battleship
@pytest.mark.benchmark(group="battleship-backtracking")
def test_battleship_backtracking(benchmark, battleship_puzzles):
    """Benchmark Battleship Backtracking on the dataset"""
    
    def run_all_battleships():
        for board, fleet in battleship_puzzles:
            board_copy = copy.deepcopy(board)
            backtracking_solve_battleship(board_copy, fleet)

    benchmark.pedantic(run_all_battleships, rounds=1, iterations=1)


# ============================================================================
# VERTEX COVER BENCHMARKS
# ============================================================================

def get_clq_files(config):
    mode = config.getoption("--intensity")
    dimacs_mvc_dir = os.path.join(root_dir, "tests", "dimacs_mvc")

    all_files = sorted([os.path.join(dimacs_mvc_dir, f) for f in os.listdir(dimacs_mvc_dir) if f.endswith(".clq")])

    if mode == "quick":
        # we don't have enough datasets for this
        return all_files
    else:
        return all_files

@pytest.fixture
def clq_files(request):
    """Fixture that provides list of CLQ files based on benchmark mode"""
    return get_clq_files(request.config)

@pytest.mark.vertexcover
@pytest.mark.benchmark(group="vertexcover-dpll")
@pytest.mark.parametrize("heuristics", VERTEXCOVER_HEURISTICS, ids=lambda h: "_".join(h) if h else "none")
def test_vertexcover_dpll(benchmark, clq_files, heuristics):
    """Benchmark Vertex Cover with DPLL solver using various heuristic combinations"""
    graphs = [parse_dimacs_clq(filepath) for filepath in clq_files]
    def run_all_mvcs():
        for graph in graphs:
            g = copy.deepcopy(graph)
            solve_vertex_cover(g, None, heuristics)

    benchmark.pedantic(run_all_mvcs, rounds=1, iterations=1)

@pytest.mark.vertexcover
@pytest.mark.benchmark(group="vertexcover-backtracking")
def test_vertexcover_backtracking(benchmark, clq_files):
    """Benchmark Vertex Cover with backtracking solver"""
    graphs = [parse_dimacs_clq(filepath) for filepath in clq_files]
    def run_all_mvcs():
        for graph in graphs:
            g = copy.deepcopy(graph)
            backtracking_solve_vertex_cover(g)

    benchmark.pedantic(run_all_mvcs, rounds=1, iterations=1)



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


@pytest.mark.sat
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