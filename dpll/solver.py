def solve(vars: list, clauses: list) -> bool:
    if len(clauses) == 0:
        return True
    if [] in clauses or not vars:
        return False
    chosen = vars[0]
    neg_chosen = '-'+chosen

    true_clauses = []
    for clause in clauses:
        if chosen not in clause:
            updated_clause = [var for var in clause if var != neg_chosen]
            true_clauses.append(updated_clause)
    
    out_true = solve(vars[1:], true_clauses)

    false_clauses = []
    for clause in clauses:
        if neg_chosen not in clause:
            updated_clause = [var for var in clause if var != chosen]
            false_clauses.append(updated_clause)
    
    out_false = solve(vars[1:], false_clauses)
    
    if out_true or out_false:
        return True
    else:
        return False
    
def unit_propagate(clauses: list, unit_clause: list) -> list:
    val = unit_clause[0]
    neg_val = val[1:] if val[0]=='-' else '-'+val 
    new_clauses = [[literal for literal in clause if literal != neg_val] for clause in clauses if val not in clause]
    return new_clauses

def solve_with_unit_propagation(vars: list, clauses: list) -> bool:
    while True:
        unit_clause = None
        for clause in clauses:
            if len(clause) == 1:
                unit_clause = clause
                break
        
        if unit_clause:
            clauses = unit_propagate(clauses, unit_clause)
        else:
            break

    if len(clauses) == 0:
        return True
    if [] in clauses or not vars:
        return False
    
    chosen = vars[0]
    neg_chosen = '-'+chosen

    true_clauses = []
    for clause in clauses:
        if chosen not in clause:
            updated_clause = [var for var in clause if var != neg_chosen]
            true_clauses.append(updated_clause)
    
    out_true = solve_with_unit_propagation(vars[1:], true_clauses)

    false_clauses = []
    for clause in clauses:
        if neg_chosen not in clause:
            updated_clause = [var for var in clause if var != chosen]
            false_clauses.append(updated_clause)
    
    out_false = solve_with_unit_propagation(vars[1:], false_clauses)
    
    if out_true or out_false:
        return True
    else:
        return False
    
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

    vars = get_vars(clauses)

    print(f"Solve answer: {solve(vars, clauses)}")
    print(f"Solve with unit propagation answer: {solve(vars, clauses)}")