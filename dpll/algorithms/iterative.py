"""Iterative DPLL algorithms with VSIDS and restarts."""

import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from ..helpers import parse_literal
    from ..heuristics import VSIDSScorer
    from ..watched_literals import WatchedFormula
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from helpers import parse_literal
    from heuristics import VSIDSScorer
    from watched_literals import WatchedFormula


def _pick_branching_variable(vars: List[str], model: Dict[str, bool]) -> Optional[str]:
    """Select next unassigned variable for branching.
    
    Args:
        vars: List of variable names (str)
        model: Current variable assignment mapping variable names to bool
    
    Returns:
        Variable name (str) to branch on, or None if all assigned
    """
    for var in vars:
        if var not in model:
            return var
    return None


def _bcp(formula: WatchedFormula, model: Dict[str, bool], trail: List[str]) -> bool:
    """Boolean constraint propagation for unit clauses.
    
    Args:
        formula: WatchedFormula object managing clauses
        model: Variable assignment dict to update
        trail: List of assigned variables (str) in order
    
    Returns:
        True if propagation succeeded, False if conflict detected
    """
    while True:
        unit_lit = None
        for clause in formula.clauses:
            unit = clause.get_unit_literal(model)
            if unit:
                unit_lit = unit
                break

        if unit_lit is None:
            return True

        var, pos = parse_literal(unit_lit)

        if var in model:
            if model[var] != pos:
                return False
            continue

        model[var] = pos
        trail.append(var)

        _, conflict = formula.propagate(unit_lit, model)
        if conflict:
            return False


def solve_iterative(vars: List[str], clauses: List[List[str]], model: Dict[str, bool], scorer: Optional[VSIDSScorer] = None, conflict_limit: int = 0) -> Optional[Dict[str, bool]]:
    """Solve SAT problem using iterative DPLL with optional VSIDS scoring.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        model: Initial variable assignment mapping variable names to bool
        scorer: Optional VSIDSScorer for variable selection
        conflict_limit: Max conflicts before restart (0 = no limit), int
    
    Returns:
        Dict mapping variables to bool if satisfiable, None if unsatisfiable, "restart" if limit reached
    """
    formula = WatchedFormula(clauses)
    conflicts = 0

    trail = []
    decision_stack = []

    if not _bcp(formula, model, trail):
        return None

    while True:
        if formula.is_satisfied(model):
            return model

        if scorer:
            var = scorer.pick_variable(model)
        else:
            var = _pick_branching_variable(vars, model)

        if var is None:
            if all(c.is_satisfied(model) for c in formula.clauses):
                return model
            conflict = True
        else:
            saved_state = formula.save_state()
            model[var] = True
            trail.append(var)
            decision_stack.append([var, False, saved_state])
            conflict = False

        if not conflict:
            if not _bcp(formula, model, trail):
                conflict = True

        while conflict:
            conflicts += 1
            if conflict_limit > 0 and conflicts >= conflict_limit:
                return "restart"

            if not decision_stack:
                return None

            last_var, tried_flipped, saved_state = decision_stack[-1]

            if scorer:
                scorer.bump(last_var)
                scorer.decay()

            while trail:
                u_var = trail.pop()
                if u_var in model:
                    del model[u_var]
                if u_var == last_var:
                    break
            
            formula.restore_state(saved_state)

            if not tried_flipped:
                saved_state = formula.save_state()
                model[last_var] = False
                trail.append(last_var)
                decision_stack[-1] = [last_var, True, saved_state]

                if _bcp(formula, model, trail):
                    conflict = False
                else:
                    conflict = True
            else:
                decision_stack.pop()
                conflict = True


def solve_with_restarts(vars: List[str], clauses: List[List[str]], model: Dict[str, bool], scorer: Optional[VSIDSScorer] = None) -> Optional[Dict[str, bool]]:
    """Solve SAT problem with periodic restarts and increasing conflict limits.
    
    Args:
        vars: List of variable names (str)
        clauses: List of clauses, each clause is a list of literals (str)
        model: Initial variable assignment mapping variable names to bool
        scorer: Optional VSIDSScorer for variable selection
    
    Returns:
        Dict mapping variables to bool if satisfiable, None otherwise
    """
    conflict_limit = 100
    max_restarts = 1000
    
    for _ in range(max_restarts):
        result = solve_iterative(vars, clauses, {}, scorer, conflict_limit)
        if result != "restart":
            return result
        conflict_limit = int(conflict_limit * 1.5)
    
    return solve_iterative(vars, clauses, {}, scorer, 0)
