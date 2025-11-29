import time

def solve(vars: list, clauses: list, heuristics: list, model=None, depth=0, literal_counts=None):
    if model is None:
        model = {}
    
    if literal_counts is None and "pureplus" in heuristics:
        literal_counts = build_literal_counts(clauses)

    if "unit" in heuristics:
        clauses, model, conflict = unit_propagate_full(clauses, model)
        if conflict:
            return False
    
    if "pureplus" in heuristics:
        pure_vars = find_pure_literals_fast(literal_counts, model)
        if pure_vars:
            clauses = pure_assign_literal(clauses, pure_vars, model)
            literal_counts = update_literal_counts(literal_counts, pure_vars)
    
    if "pure" in heuristics and depth == 0:
        pure_check = {}

        for clause in clauses:
            for literal in clause:
                var = literal.lstrip("-")

                if var in model:
                    continue

                polarity = literal[0] != '-'

                if var not in pure_check:
                    pure_check[var] = polarity
                elif pure_check[var] != polarity:
                    pure_check[var] = None

        pure_check = {var: pol for var, pol in pure_check.items() if pol is not None}

        if pure_check:
            clauses = pure_assign_literal(clauses, pure_check, model)

    if len(clauses) == 0:
        return model
    if [] in clauses:
        return False
    
    remaining_vars = [v for v in vars if v not in model]
    
    if not remaining_vars:
        return False
    
    chosen = remaining_vars[0]
    rest_vars = remaining_vars[1:]
    neg_chosen = '-'+chosen

    true_clauses = []
    for clause in clauses:
        if chosen not in clause:
            updated_clause = [var for var in clause if var != neg_chosen]
            true_clauses.append(updated_clause)
    
    new_model = model.copy()
    new_model[chosen] = True
    
    new_literal_counts = None
    if literal_counts:
        new_literal_counts = update_literal_counts_for_assignment(literal_counts, chosen, True, clauses)
    
    out_true = solve(rest_vars, true_clauses, heuristics, new_model, depth+1, new_literal_counts)

    if out_true is not False:
        return out_true

    false_clauses = []
    for clause in clauses:
        if neg_chosen not in clause:
            updated_clause = [var for var in clause if var != chosen]
            false_clauses.append(updated_clause)
    
    new_model = model.copy()
    new_model[chosen] = False
    
    new_literal_counts = None
    if literal_counts:
        new_literal_counts = update_literal_counts_for_assignment(literal_counts, chosen, False, clauses)
    
    out_false = solve(rest_vars, false_clauses, heuristics, new_model, depth+1, new_literal_counts)
    
    if out_false is not False:
        return out_false
    else:
        return False

def unit_propagate_full(clauses: list, model: dict):
    model = model.copy()
    
    while True:
        unit_clause = None
        for clause in clauses:
            if len(clause) == 1:
                unit_clause = clause
                break
        
        if not unit_clause:
            break
        
        val = unit_clause[0]
        var = val.lstrip('-')
        assignment = val[0] != '-'
        
        if var in model:
            if model[var] != assignment:
                return clauses, model, True
            clauses = [c for c in clauses if val not in c]
            continue
        
        model[var] = assignment
        neg_val = val[1:] if val[0]=='-' else '-'+val
        
        new_clauses = []
        for clause in clauses:
            if val in clause:
                continue
            updated_clause = [literal for literal in clause if literal != neg_val]
            new_clauses.append(updated_clause)
        
        clauses = new_clauses
    
    return clauses, model, False

def pure_assign_literal(clauses: list, pure_check: dict, model: dict):
    literals_to_satisfy = set()
    for var, polarity in pure_check.items():
        model[var] = polarity
        literals_to_satisfy.add(var if polarity else '-' + var)
    
    new_clauses = [clause for clause in clauses 
                   if not any(lit in literals_to_satisfy for lit in clause)]
    
    return new_clauses

def build_literal_counts(clauses):
    pos_count = {}
    neg_count = {}
    
    for clause in clauses:
        for literal in clause:
            var = literal.lstrip('-')
            if literal[0] == '-':
                neg_count[var] = neg_count.get(var, 0) + 1
            else:
                pos_count[var] = pos_count.get(var, 0) + 1
    
    return {'pos': pos_count, 'neg': neg_count}

def find_pure_literals_fast(literal_counts, model):
    pure_vars = {}
    pos_count = literal_counts['pos']
    neg_count = literal_counts['neg']
    
    all_vars = set(pos_count.keys()) | set(neg_count.keys())
    
    for var in all_vars:
        if var in model:
            continue
        
        pos = pos_count.get(var, 0)
        neg = neg_count.get(var, 0)
        
        if pos > 0 and neg == 0:
            pure_vars[var] = True
        elif neg > 0 and pos == 0:
            pure_vars[var] = False
    
    return pure_vars

def update_literal_counts(literal_counts, pure_vars):
    new_counts = {
        'pos': literal_counts['pos'].copy(),
        'neg': literal_counts['neg'].copy()
    }
    
    for var in pure_vars:
        new_counts['pos'].pop(var, None)
        new_counts['neg'].pop(var, None)
    
    return new_counts

def update_literal_counts_for_assignment(literal_counts, var, assignment, clauses):
    new_counts = {
        'pos': literal_counts['pos'].copy(),
        'neg': literal_counts['neg'].copy()
    }
    
    satisfied_literal = var if assignment else '-' + var
    removed_literal = '-' + var if assignment else var
    
    for clause in clauses:
        if satisfied_literal in clause:
            for lit in clause:
                v = lit.lstrip('-')
                if lit[0] == '-':
                    new_counts['neg'][v] = max(0, new_counts['neg'].get(v, 0) - 1)
                else:
                    new_counts['pos'][v] = max(0, new_counts['pos'].get(v, 0) - 1)
    
    return new_counts


def get_vars(clauses):
    vars_set = set()
    for clause in clauses:
        for literal in clause:
            var = literal.lstrip('-')
            vars_set.add(var)
    return sorted(list(vars_set))

clauses = []

if __name__ == "__main__":
    t = input("Enter the number of clauses: ")
    print("Enter each clause in a new line with spaces between variables (use '-' for negation):")
    for _ in range(int(t)):
        clause = input().split()
        clauses.append(clause)

    vars_list = get_vars(clauses)

    start_time = time.time()
    result_no_heuristics = solve(vars_list, clauses, [])
    elapsed_no_heuristics = time.time() - start_time
    print(f"Solve (no heuristics) answer: {result_no_heuristics}")
    print(f"time: {elapsed_no_heuristics:.6f}s")

    start_time = time.time()
    result_unit = solve(vars_list, clauses, ['unit'])
    elapsed_unit = time.time() - start_time
    print(f"\nSolve (unit prop) answer: {result_unit}")
    print(f"time: {elapsed_unit:.6f}s")

    start_time = time.time()
    result_unit_pure = solve(vars_list, clauses, ['unit', 'pure'])
    elapsed_unit_pure = time.time() - start_time
    print(f"\nSolve (unit prop + pure) answer: {result_unit_pure}")
    print(f"time: {elapsed_unit_pure:.6f}s")

    start_time = time.time()
    result_pureplus = solve(vars_list, clauses, ['pureplus'])
    elapsed_pureplus = time.time() - start_time
    print(f"\nSolve (pureplus) answer: {result_pureplus}")
    print(f"time: {elapsed_pureplus:.6f}s")

    start_time = time.time()
    result_unit_pureplus = solve(vars_list, clauses, ['unit', 'pureplus'])
    elapsed_unit_pureplus = time.time() - start_time
    print(f"\nSolve (unit prop + pureplus) answer: {result_unit_pureplus}")
    print(f"time: {elapsed_unit_pureplus:.6f}s")
