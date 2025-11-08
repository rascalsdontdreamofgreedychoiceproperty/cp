def solve(vars: list, clauses: list):
    if len(clauses) == 0:
        return True
    if [] in clauses or not vars:
        return False
    chosen = vars[0]
    neg_chosen = chosen[1:] if '-' in chosen else '-'+chosen
    # print(vars)
    # print(clauses)
    # print(f"chosen: {chosen}")
    # print(f"-chosen: {neg_chosen}")
    # print()
    updated_vars = [var for var in vars if var != chosen and var != neg_chosen]
    true_clauses = []
    for clause in clauses:
        if chosen not in clause:
            updated_clause = [var for var in clause if var != neg_chosen]
            true_clauses.append(updated_clause)
    
    out_true = solve(updated_vars, true_clauses)

    false_clauses = []
    for clause in clauses:
        if neg_chosen not in clause:
            updated_clause = [var for var in clause if var != chosen]
            false_clauses.append(updated_clause)
    
    out_false = solve(updated_vars, false_clauses)

    if out_true or out_false:
        return True
    else:
        return False

vars = set()
clauses = []

t = input("Enter the number of clauses: ")
print("Enter each clause in a new line with spaces between variables (use '-' for negation):")
for _ in range(int(t)):
    clause = input().split()
    clauses.append(clause)
    vars.update(clause)

vars = sorted(vars)

ans = solve(vars, clauses)

print("SAT" if ans else "UNSAT")