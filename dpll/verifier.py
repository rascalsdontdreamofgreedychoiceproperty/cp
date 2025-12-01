def verify(clauses: list, solution) -> bool:
    """Verify if a solution satisfies all clauses.
    
    Args:
        clauses: List of clauses, each clause is a list of literals (str)
        solution: Variable assignment (Dict[str, bool]) or False
    
    Returns:
        True if solution satisfies all clauses, False otherwise (bool)
    """
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
