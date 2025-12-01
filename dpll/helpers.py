from typing import List, Tuple


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


def get_vars(clauses):
    vars_set = set()
    for clause in clauses:
        for literal in clause:
            var = literal.lstrip('-')
            vars_set.add(var)
    return sorted(list(vars_set))
