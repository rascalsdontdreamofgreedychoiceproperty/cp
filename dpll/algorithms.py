import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from .helpers import parse_literal, simplify_clauses
    from .heuristics import unit_propagate, eliminate_pure_literals, VSIDSScorer
    from .watched_literals import WatchedFormula
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from helpers import parse_literal, simplify_clauses
    from heuristics import unit_propagate, eliminate_pure_literals, VSIDSScorer
    from watched_literals import WatchedFormula


def solve_naive(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
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
    
    result = solve_naive(vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_naive(vars, new_clauses, new_model)


def solve_unit(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model, conflict = unit_propagate(clauses, model)
    if conflict:
        return None
    
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
    
    result = solve_unit(vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_unit(vars, new_clauses, new_model)


def solve_pure(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model = eliminate_pure_literals(clauses, model)
    return _solve_pure_helper(vars, clauses, model)


def _solve_pure_helper(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
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


def solve_unit_pure(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model, conflict = unit_propagate(clauses, model)
    if conflict:
        return None
    
    clauses, model = eliminate_pure_literals(clauses, model)
    
    return _solve_unit_pure_helper(vars, clauses, model)


def _solve_unit_pure_helper(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model, conflict = unit_propagate(clauses, model)
    if conflict:
        return None
    
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
    
    result = _solve_unit_pure_helper(vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return _solve_unit_pure_helper(vars, new_clauses, new_model)


def solve_2wl(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    formula = WatchedFormula(clauses)
    return solve_2wl_recursive(vars, formula, model)


def solve_2wl_recursive(vars: List[str], formula: WatchedFormula, model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
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
    for var in reversed(vars_to_remove):
        if var in model:
            del model[var]


def _pick_branching_variable(vars: List[str], model: Dict[str, bool]) -> Optional[str]:
    for var in vars:
        if var not in model:
            return var
    return None


def _bcp(formula: WatchedFormula, model: Dict[str, bool], trail: List[str]) -> bool:
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
    conflict_limit = 100
    max_restarts = 1000
    
    for _ in range(max_restarts):
        result = solve_iterative(vars, clauses, {}, scorer, conflict_limit)
        if result != "restart":
            return result
        conflict_limit = int(conflict_limit * 1.5)
    
    return solve_iterative(vars, clauses, {}, scorer, 0)
