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

    ans = solve(vars, clauses)

    print("SAT" if ans else "UNSAT")