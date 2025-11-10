def solve(vars: list, clauses: list, heuristics: list):
    model = {}
    
    if "unit" in heuristics:
        while True:
            unit_clause = None
            for clause in clauses:
                if len(clause) == 1:
                    unit_clause = clause
                    break
            
            if unit_clause:
                val = unit_clause[0]
                var = val.lstrip('-')
                assignment = val[0] != '-'
                
                if var in model and model[var] != assignment:
                    return False
                model[var] = assignment
                
                clauses = unit_propagate(clauses, unit_clause)
            else:
                break

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
    
    out_true = solve(rest_vars, true_clauses, heuristics)

    if out_true is not False:
        out_true[chosen] = True
        out_true.update(model)
        return out_true

    false_clauses = []
    for clause in clauses:
        if neg_chosen not in clause:
            updated_clause = [var for var in clause if var != chosen]
            false_clauses.append(updated_clause)
    
    out_false = solve(rest_vars, false_clauses, heuristics)
    
    if out_false is not False:
        out_false[chosen] = False
        out_false.update(model)
        return out_false
    else:
        return False
    
def unit_propagate(clauses: list, unit_clause: list) -> list:
    val = unit_clause[0]
    neg_val = val[1:] if val[0]=='-' else '-'+val 
    new_clauses = [[literal for literal in clause if literal != neg_val] for clause in clauses if val not in clause]
    return new_clauses


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

    print(f"Solve answer: {solve(vars_list, clauses, [])}")
    print(f"Solve with unit propagation answer: {solve(vars_list, clauses, ['unit'])}")
