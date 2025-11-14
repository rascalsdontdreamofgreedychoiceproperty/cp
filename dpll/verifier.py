def verify(clauses: list, solution) -> bool:
    if solution == False:
        return False
    for clause in clauses:
        valid = False
        for literal in clause:
            if solution.get(literal) == True:
                valid = True
                break
        if valid == False:
            return False
    return True
