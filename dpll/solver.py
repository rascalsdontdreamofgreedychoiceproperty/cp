import time
from typing import Dict, Optional
from .helpers import get_vars
from .algorithms import solve_naive, solve_unit, solve_pure, solve_unit_pure, solve_2wl, solve_iterative


def solve(vars: list, clauses: list, heuristics: list, model=None) -> Optional[Dict[str, bool]]:
    if model is None:
        model = {}
    
    if heuristics == ['cdcl']:
        return solve_iterative(vars, clauses, model)

    if not heuristics:
        result = solve_naive(vars, clauses, model)
    elif heuristics == ['unit']:
        result = solve_unit(vars, clauses, model)
    elif heuristics == ['pure']:
        result = solve_pure(vars, clauses, model)
    elif heuristics == ['2wl']:
        result = solve_2wl(vars, clauses, model)
    elif set(heuristics) == {'unit', 'pure'}:
        result = solve_unit_pure(vars, clauses, model)
    else:
        raise ValueError(f"Unknown heuristics: {heuristics}")
    
    return result if result is not None else False


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
    result_cdcl = solve(vars_list, clauses, ['cdcl'])
    elapsed_cdcl = time.time() - start_time
    
    res_col = grn if result_cdcl else red
    
    print(f"\n{bld}[iterative dpll (pre-cdcl)]{rst}")
    print(f"result: {res_col}{str(result_cdcl).lower()}{rst}")
    print(f"time: {elapsed_cdcl:.6f}s")
    if elapsed_no_heuristics > 0:
        print(f"speedup: {cyn}{elapsed_no_heuristics/elapsed_cdcl:.2f}x{rst}")