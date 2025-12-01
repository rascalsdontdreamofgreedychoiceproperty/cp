"""DPLL algorithm with pure literal elimination."""

import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from ..helpers import simplify_clauses
    from ..heuristics import eliminate_pure_literals
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from helpers import simplify_clauses
    from heuristics import eliminate_pure_literals


def solve_pure(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    """Solve SAT problem using DPLL with pure literal elimination.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        model: Partial variable assignment mapping variable names to bool
    
    Returns:
        Dict mapping variables to bool if satisfiable, None otherwise
    """
    clauses, model = eliminate_pure_literals(clauses, model)
    return _solve_pure_helper(vars, clauses, model)


def _solve_pure_helper(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    """Helper for solve_pure, recursive DPLL step.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        model: Partial variable assignment mapping variable names to bool
    
    Returns:
        Dict mapping variables to bool if satisfiable, None otherwise
    """
    if not clauses:
        return model
    if [] in clauses:
        return None
    
    remaining = [v for v in vars if v not in model]
    if not remaining:
        return None
    
    var = remaining[0]
    
    pos_literal = var
    new_clauses = simplify_clauses(clauses, pos_literal)
    new_model = model.copy()
    new_model[var] = True
    
    result = _solve_pure_helper(vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return _solve_pure_helper(vars, new_clauses, new_model)
