"""DPLL algorithm with two-watched literals."""

import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from ..helpers import parse_literal
    from ..watched_literals import WatchedFormula
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from helpers import parse_literal
    from watched_literals import WatchedFormula


def solve_2wl(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    """Solve SAT problem using DPLL with two-watched literals.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        model: Partial variable assignment mapping variable names to bool
    
    Returns:
        Dict mapping variables to bool if satisfiable, None otherwise
    """
    formula = WatchedFormula(clauses)
    return solve_2wl_recursive(vars, formula, model)


def solve_2wl_recursive(vars: List[str], formula: WatchedFormula, model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    """Recursive helper for two-watched literals DPLL.
    
    Args:
        vars: List of variable names (str)
        formula: WatchedFormula object managing watched literals
        model: Partial variable assignment mapping variable names to bool
    
    Returns:
        Dict mapping variables to bool if satisfiable, None otherwise
    """
    assigned_in_this_step = []

    while True:
        unit_lit = None
        for clause in formula.clauses:
            unit = clause.get_unit_literal(model)
            if unit:
                unit_lit = unit
                break
        
        if unit_lit is None:
            break
        
        var, pos = parse_literal(unit_lit)
        
        if var in model:
            if model[var] != pos:
                _backtrack(model, assigned_in_this_step)
                return None
            continue
        
        model[var] = pos
        assigned_in_this_step.append(var)
        
        new_unit, conflict = formula.propagate(unit_lit, model)
        if conflict:
            _backtrack(model, assigned_in_this_step)
            return None
        
        if new_unit:
            pass

    if formula.is_satisfied(model):
        return model
    
    remaining = [v for v in vars if v not in model]
    if not remaining:
        if all(c.is_satisfied(model) for c in formula.clauses):
            return model
        _backtrack(model, assigned_in_this_step)
        return None
    
    var = remaining[0]
    
    saved_state = formula.save_state()
    model[var] = True
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    del model[var]
    formula.restore_state(saved_state)
    
    saved_state = formula.save_state()
    model[var] = False
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    del model[var]
    formula.restore_state(saved_state)
    
    _backtrack(model, assigned_in_this_step)
    return None


def _backtrack(model: Dict[str, bool], vars_to_remove: List[str]):
    """Remove variables from model during backtracking.
    
    Args:
        model: Variable assignment dict to modify
        vars_to_remove: List of variable names (str) to remove
    
    Returns:
        None (modifies model in place)
    """
    for var in reversed(vars_to_remove):
        if var in model:
            del model[var]
