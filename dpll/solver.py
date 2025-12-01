import time
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    from .helpers import get_vars
    from .algorithms import solve_naive, solve_unit, solve_pure, solve_unit_pure, solve_2wl, solve_iterative, solve_with_restarts
    from .heuristics import VSIDSScorer
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from helpers import get_vars
    from algorithms import solve_naive, solve_unit, solve_pure, solve_unit_pure, solve_2wl, solve_iterative, solve_with_restarts
    from heuristics import VSIDSScorer


def solve(vars: list, clauses: list, heuristics: list, model=None) -> Optional[Dict[str, bool]]:
    """Solve SAT problem using specified heuristics.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        heuristics: List of heuristic names (str) to apply
        model: Optional initial variable assignment (Dict[str, bool])
    
    Returns:
        Dict mapping variables to bool if satisfiable, False otherwise
    """
    if model is None:
        model = {}
    
    if heuristics == ['2wli']:
        result = solve_iterative(vars, clauses, model)
    elif not heuristics:
        result = solve_naive(vars, clauses, model)
    elif heuristics == ['unit']:
        result = solve_unit(vars, clauses, model)
    elif heuristics == ['pure']:
        result = solve_pure(vars, clauses, model)
    elif heuristics == ['2wl']:
        result = solve_2wl(vars, clauses, model)
    elif heuristics == ['vsids']:
        scorer = VSIDSScorer(clauses)
        result = solve_iterative(vars, clauses, model, scorer)
    elif heuristics == ['restarts']:
        scorer = VSIDSScorer(clauses)
        result = solve_with_restarts(vars, clauses, model, scorer)
    elif set(heuristics) == {'unit', 'pure'}:
        result = solve_unit_pure(vars, clauses, model)
    else:
        raise ValueError(f"Unknown heuristics: {heuristics}")
    
    # Handle both None and "restart" as unsatisfiable/failure cases
    if result is None or result == "restart":
        return False
    return result


if __name__ == "__main__":
    red, grn, yel, cyn, bld, rst = "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

    clauses = []
    
    t = input(f"{cyn}enter the number of clauses: {rst}")
    print(f"{cyn}enter each clause in a new line with spaces between variables (use '-' for negation):{rst}")
    for _ in range(int(t)):
        clause = input().split()
        clauses.append(clause)

    vars_list = get_vars(clauses)

    print(f"\n{bld}{yel}dpll solver benchmark{rst}")

    start_time = time.time()
    result_no_heuristics = solve(vars_list, clauses, [])
    elapsed_no_heuristics = time.time() - start_time
    
    res_col = grn if result_no_heuristics else red
    
    print(f"\n{bld}[naive dpll]{rst}")
    print(f"result: {res_col}{str(result_no_heuristics).lower()}{rst}")
    print(f"time: {elapsed_no_heuristics:.6f}s")

    start_time = time.time()
    result_unit = solve(vars_list, clauses, ['unit'])
    elapsed_unit = time.time() - start_time
    
    res_col = grn if result_unit else red
    
    print(f"\n{bld}[unit propagation]{rst}")
    print(f"result: {res_col}{str(result_unit).lower()}{rst}")
    print(f"time: {elapsed_unit:.6f}s")
    if elapsed_no_heuristics > 0:
        print(f"speedup: {cyn}{elapsed_no_heuristics/elapsed_unit:.2f}x{rst}")

    start_time = time.time()
    result_unit_pure = solve(vars_list, clauses, ['unit', 'pure'])
    elapsed_unit_pure = time.time() - start_time
    
    res_col = grn if result_unit_pure else red
    
    print(f"\n{bld}[unit propagation + pure literal]{rst}")
    print(f"result: {res_col}{str(result_unit_pure).lower()}{rst}")
    print(f"time: {elapsed_unit_pure:.6f}s")
    if elapsed_no_heuristics > 0:
        print(f"speedup: {cyn}{elapsed_no_heuristics/elapsed_unit_pure:.2f}x{rst}")

    start_time = time.time()
    result_2wl = solve(vars_list, clauses, ['2wl'])
    elapsed_2wl = time.time() - start_time
    
    res_col = grn if result_2wl else red
    
    print(f"\n{bld}[two-watched literals]{rst}")
    print(f"result: {res_col}{str(result_2wl).lower()}{rst}")
    print(f"time: {elapsed_2wl:.6f}s")
    if elapsed_no_heuristics > 0:
        print(f"speedup: {cyn}{elapsed_no_heuristics/elapsed_2wl:.2f}x{rst}")

    start_time = time.time()
    result_2wli = solve(vars_list, clauses, ['2wli'])
    elapsed_2wli = time.time() - start_time
    
    res_col = grn if result_2wli else red
    
    print(f"\n{bld}[two-watched literals iterative]{rst}")
    print(f"result: {res_col}{str(result_2wli).lower()}{rst}")
    print(f"time: {elapsed_2wli:.6f}s")
    if elapsed_no_heuristics > 0:
        print(f"speedup: {cyn}{elapsed_no_heuristics/elapsed_2wli:.2f}x{rst}")