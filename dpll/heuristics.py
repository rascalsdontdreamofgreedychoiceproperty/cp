from typing import List, Dict, Tuple
from .helpers import parse_literal, simplify_clauses


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
