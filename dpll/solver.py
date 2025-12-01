import time
from typing import List, Dict, Optional, Tuple, Set


def parse_literal(lit: str) -> Tuple[str, bool]:
    if lit.startswith('-'):
        return lit[1:], False
    return lit, True


def negate_literal(lit: str) -> str:
    return lit[1:] if lit.startswith('-') else '-' + lit


def simplify_clauses(clauses: List[List[str]], literal: str) -> List[List[str]]:
    neg_literal = negate_literal(literal)
    new_clauses = []
    
    for clause in clauses:
        if literal in clause:
            continue
        if neg_literal in clause:
            new_clause = [lit for lit in clause if lit != neg_literal]
            new_clauses.append(new_clause)
        else:
            new_clauses.append(clause)
    
    return new_clauses


# 2wl type shit

class WatchedClause:
    __slots__ = ['literals', 'watch1', 'watch2']
    
    def __init__(self, literals: List[str]):
        self.literals = literals
        n = len(literals)
        self.watch1 = 0 if n > 0 else -1
        self.watch2 = 1 if n > 1 else -1
    
    def is_satisfied(self, model: Dict[str, bool]) -> bool:
        for lit in self.literals:
            var, pos = parse_literal(lit)
            if var in model and model[var] == pos:
                return True
        return False
    
    def update_watch(self, watched_idx: int, model: Dict[str, bool]) -> Optional[int]:
        for i, lit in enumerate(self.literals):
            if i == self.watch1 or i == self.watch2:
                continue
            
            var, pos = parse_literal(lit)
            if var not in model:
                return i
            if model[var] == pos:
                return i
        return None
    
    def get_unit_literal(self, model: Dict[str, bool]) -> Optional[str]:
        if self.watch1 == -1:
            return None
        
        lit1 = self.literals[self.watch1]
        var1, pos1 = parse_literal(lit1)
        
        if self.watch2 == -1:
            if var1 not in model:
                return lit1
            return None
        
        lit2 = self.literals[self.watch2]
        var2, pos2 = parse_literal(lit2)
        
        if var1 in model:
            if model[var1] != pos1 and var2 not in model:
                return lit2
        elif var2 in model:
            if model[var2] != pos2:
                return lit1
        
        return None
    
    def is_conflicting(self, model: Dict[str, bool]) -> bool:
        if self.watch1 == -1:
            return True
        
        lit1 = self.literals[self.watch1]
        var1, pos1 = parse_literal(lit1)
        
        if self.watch2 == -1:
            return var1 in model and model[var1] != pos1
        
        lit2 = self.literals[self.watch2]
        var2, pos2 = parse_literal(lit2)
        
        return (var1 in model and model[var1] != pos1 and 
                var2 in model and model[var2] != pos2)


class WatchedFormula:
    def __init__(self, clauses: List[List[str]]):
        self.clauses = [WatchedClause(c) for c in clauses]
        self.watch_lists = {}
        self._build_watch_lists()
    
    def _build_watch_lists(self):
        for idx, clause in enumerate(self.clauses):
            if clause.watch1 != -1:
                lit = clause.literals[clause.watch1]
                neg = negate_literal(lit)
                if neg not in self.watch_lists:
                    self.watch_lists[neg] = []
                self.watch_lists[neg].append((idx, 1))
            
            if clause.watch2 != -1:
                lit = clause.literals[clause.watch2]
                neg = negate_literal(lit)
                if neg not in self.watch_lists:
                    self.watch_lists[neg] = []
                self.watch_lists[neg].append((idx, 2))
    
    def propagate(self, literal: str, model: Dict[str, bool]) -> Tuple[Optional[str], bool]:
        if literal not in self.watch_lists:
            return None, False
        
        watch_list = self.watch_lists[literal]
        new_watch_list = []
        unit_literal = None
        
        for clause_idx, watch_num in watch_list:
            clause = self.clauses[clause_idx]
            
            if clause.is_satisfied(model):
                new_watch_list.append((clause_idx, watch_num))
                continue
            
            watched_idx = clause.watch1 if watch_num == 1 else clause.watch2
            new_watch_idx = clause.update_watch(watched_idx, model)
            
            if new_watch_idx is not None:
                if watch_num == 1:
                    clause.watch1 = new_watch_idx
                else:
                    clause.watch2 = new_watch_idx
                
                new_lit = clause.literals[new_watch_idx]
                neg = negate_literal(new_lit)
                if neg not in self.watch_lists:
                    self.watch_lists[neg] = []
                self.watch_lists[neg].append((clause_idx, watch_num))
            else:
                new_watch_list.append((clause_idx, watch_num))
                
                if clause.is_conflicting(model):
                    self.watch_lists[literal] = new_watch_list
                    return None, True
                
                unit = clause.get_unit_literal(model)
                if unit and unit_literal is None:
                    unit_literal = unit
        
        self.watch_lists[literal] = new_watch_list
        return unit_literal, False
    
    def is_satisfied(self, model: Dict[str, bool]) -> bool:
        return all(c.is_satisfied(model) for c in self.clauses)


# core

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

# llm generated code
def solve_2wl_recursive(vars: List[str], formula: WatchedFormula, model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    # 1. Track changes made ONLY in this specific recursion level
    assigned_in_this_step = []

    # 2. Boolean Constraint Propagation (BCP)
    while True:
        unit_lit = None
        # Check watchers for existing units
        for clause in formula.clauses:
            unit = clause.get_unit_literal(model)
            if unit:
                unit_lit = unit
                break
        
        if unit_lit is None:
            break
        
        var, pos = parse_literal(unit_lit)
        
        # If variable is already set...
        if var in model:
            if model[var] != pos:
                # CONFLICT: Undo changes made in this loop and return failure
                _backtrack(model, assigned_in_this_step)
                return None
            continue
        
        # ASSIGN: Mutate the shared model
        model[var] = pos
        assigned_in_this_step.append(var)
        
        # Propagate changes to watchers
        new_unit, conflict = formula.propagate(unit_lit, model)
        if conflict:
            # CONFLICT: Undo changes and return failure
            _backtrack(model, assigned_in_this_step)
            return None
        
        if new_unit:
            # If propagation found a new unit immediately, handle it next loop
            # (Your original code handled the immediate new_unit here, 
            # but letting the loop handle it is cleaner and safer)
            pass 

    # 3. Check for SAT
    if formula.is_satisfied(model):
        return model
    
    # 4. Pick a decision variable
    # (Simple heuristic: pick first undefined variable)
    remaining = [v for v in vars if v not in model]
    if not remaining:
        # If no variables left but formula not satisfied? 
        # Usually implies the formula is empty or valid, but for safety:
        if all(c.is_satisfied(model) for c in formula.clauses):
            return model
        _backtrack(model, assigned_in_this_step)
        return None
    
    var = remaining[0]
    
    # 5. Try Branch 1: Positive
    model[var] = True
    # Recursive call passes the SAME model
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    # FAILURE on Branch 1: Backtrack the decision variable
    del model[var]
    
    # 6. Try Branch 2: Negative
    model[var] = False
    if solve_2wl_recursive(vars, formula, model) is not None:
        return model
    
    # FAILURE on Branch 2: Backtrack the decision variable
    del model[var]
    
    # 7. Total Failure for this node
    # We must undo the BCP assignments we made at the start of this function
    _backtrack(model, assigned_in_this_step)
    return None

def _backtrack(model: Dict[str, bool], vars_to_remove: List[str]):
    """Helper to remove variables from the model in reverse order."""
    for var in reversed(vars_to_remove):
        if var in model:
            del model[var]
# llm generated code ends

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


# heugghhhristics

def unit_propagate(clauses: List[List[str]], model: Dict[str, bool]) -> Tuple[List[List[str]], Dict[str, bool], bool]:
    model = model.copy()
    
    while True:
        unit_literal = None
        for clause in clauses:
            if len(clause) == 1:
                unit_literal = clause[0]
                break
        
        if unit_literal is None:
            break
        
        var, is_positive = parse_literal(unit_literal)
        
        if var in model:
            if model[var] != is_positive:
                return clauses, model, True
            clauses = simplify_clauses(clauses, unit_literal)
            continue
        
        model[var] = is_positive
        clauses = simplify_clauses(clauses, unit_literal)
    
    return clauses, model, False


def eliminate_pure_literals(clauses: List[List[str]], model: Dict[str, bool]) -> Tuple[List[List[str]], Dict[str, bool]]:
    model = model.copy()
    polarity = {}
    
    for clause in clauses:
        for literal in clause:
            var, is_positive = parse_literal(literal)
            
            if var in model:
                continue
            
            if var not in polarity:
                polarity[var] = is_positive
            elif polarity[var] != is_positive:
                polarity[var] = None
    
    for var, pol in polarity.items():
        if pol is not None:
            model[var] = pol
            literal = var if pol else '-' + var
            clauses = simplify_clauses(clauses, literal)
    
    return clauses, model


# a pee eye


def solve_iterative(vars: List[str], clauses: List[List[str]], model: Dict[str, bool]) -> Optional[Dict[str, bool]]:
    formula = WatchedFormula(clauses)

    trail = []
    decision_stack = []  # list of [var, tried_flipped]

    # Level 0 propagation
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


def get_vars(clauses):
    vars_set = set()
    for clause in clauses:
        for literal in clause:
            var = literal.lstrip('-')
            vars_set.add(var)
    return sorted(list(vars_set))


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