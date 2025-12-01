from typing import List, Dict, Optional, Tuple
from .helpers import parse_literal, negate_literal


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
