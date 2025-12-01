from typing import List, Dict, Optional
from .helpers import parse_literal, simplify_clauses
from .heuristics import unit_propagate, eliminate_pure_literals
from .watched_literals import WatchedFormula


def solve_naive(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    if not clauses:
        return model
    if [] in clauses:
        return None
    
    remaining = [v for v in vars if v not in model]
    if not remaining:
        return None
    
    var = remaining[0]
    rest_vars = remaining[1:]
    
    pos_literal = var
    new_clauses = simplify_clauses(clauses, pos_literal)
    new_model = model.copy()
    new_model[var] = True
    
    result = solve_naive(rest_vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_naive(rest_vars, new_clauses, new_model)


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
    rest_vars = remaining[1:]
    
    pos_literal = var
    new_clauses = simplify_clauses(clauses, pos_literal)
    new_model = model.copy()
    new_model[var] = True
    
    result = solve_unit(rest_vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_unit(rest_vars, new_clauses, new_model)


def solve_pure(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model = eliminate_pure_literals(clauses, model)
    
    if not clauses:
        return model
    if [] in clauses:
        return None
    
    remaining = [v for v in vars if v not in model]
    if not remaining:
        return None
    
    var = remaining[0]
    rest_vars = remaining[1:]
    
    pos_literal = var
    new_clauses = simplify_clauses(clauses, pos_literal)
    new_model = model.copy()
    new_model[var] = True
    
    result = solve_pure(rest_vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_pure(rest_vars, new_clauses, new_model)


def solve_unit_pure(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    clauses, model, conflict = unit_propagate(clauses, model)
    if conflict:
        return None
    
    clauses, model = eliminate_pure_literals(clauses, model)
    
    if not clauses:
        return model
    if [] in clauses:
        return None
    
    remaining = [v for v in vars if v not in model]
    if not remaining:
        return None
    
    var = remaining[0]
    rest_vars = remaining[1:]
    
    pos_literal = var
    new_clauses = simplify_clauses(clauses, pos_literal)
    new_model = model.copy()
    new_model[var] = True
    
    result = solve_unit_pure(rest_vars, new_clauses, new_model)
    if result is not None:
        return result
    
    neg_literal = '-' + var
    new_clauses = simplify_clauses(clauses, neg_literal)
    new_model = model.copy()
    new_model[var] = False
    
    return solve_unit_pure(rest_vars, new_clauses, new_model)


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
    
    model[var] = True
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    del model[var]
    
    model[var] = False
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    del model[var]
    
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


def solve_iterative(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    formula = WatchedFormula(clauses)

    trail = []
    decision_stack = []

    if not _bcp(formula, model, trail):
        return None

    while True:
        if formula.is_satisfied(model):
            return model

        var = _pick_branching_variable(vars, model)

        if var is None:
            if all(c.is_satisfied(model) for c in formula.clauses):
                return model
            conflict = True
        else:
            model[var] = True
            trail.append(var)
            decision_stack.append([var, False])
            conflict = False

        if not conflict:
            if not _bcp(formula, model, trail):
                conflict = True

        while conflict:
            if not decision_stack:
                return None

            last_var, tried_flipped = decision_stack[-1]

            while trail:
                u_var = trail.pop()
                if u_var in model:
                    del model[u_var]
                if u_var == last_var:
                    break

            if not tried_flipped:
                model[last_var] = False
                trail.append(last_var)
                decision_stack[-1][1] = True

                if _bcp(formula, model, trail):
                    conflict = False
                else:
                    conflict = True
            else:
                decision_stack.pop()
                conflict = True
