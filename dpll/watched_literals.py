import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    from .helpers import parse_literal, negate_literal
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from helpers import parse_literal, negate_literal


class WatchedClause:
    __slots__ = ['literals', 'watch1', 'watch2']
    
    def __init__(self, literals: List[str]):
        """Initialize watched clause with two watched literals.
        
        Args:
            literals: List of literals (str) in the clause
        
        Returns:
            None
        """
        self.literals = literals
        n = len(literals)
        self.watch1 = 0 if n > 0 else -1
        self.watch2 = 1 if n > 1 else -1
    
    def is_satisfied(self, model: Dict[str, bool]) -> bool:
        """Check if clause is satisfied by current model.
        
        Args:
            model: Variable assignment mapping variable names to bool
        
        Returns:
            True if any literal is satisfied, False otherwise (bool)
        """
        for lit in self.literals:
            var, pos = parse_literal(lit)
            if var in model and model[var] == pos:
                return True
        return False
    
    def update_watch(self, watched_idx: int, model: Dict[str, bool]) -> Optional[int]:
        """Find new literal to watch after assignment.
        
        Args:
            watched_idx: Index (int) of current watched literal
            model: Variable assignment mapping variable names to bool
        
        Returns:
            Index (int) of new literal to watch, or None if no alternative found
        """
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
        """Get unit literal if clause is unit under current model.
        
        Args:
            model: Variable assignment mapping variable names to bool
        
        Returns:
            Unit literal (str) if exists, None otherwise
        """
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
        """Check if clause conflicts with current model.
        
        Args:
            model: Variable assignment mapping variable names to bool
        
        Returns:
            True if both watched literals are falsified, False otherwise (bool)
        """
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
        """Initialize watched formula with clauses.
        
        Args:
            clauses: List of clauses, each clause is a list of literals (str)
        
        Returns:
            None
        """
        self.clauses = [WatchedClause(c) for c in clauses]
        self.watch_lists = {}
        self._build_watch_lists()
    
    def save_state(self) -> Tuple[Dict[int, Tuple[int, int]], Dict[str, List[Tuple[int, int]]]]:
        """Save current state of watched literals for backtracking.
        
        Args:
            None
        
        Returns:
            Tuple of (clause watch positions (Dict), watch lists (Dict))
        """
        clause_watches = {}
        for idx, clause in enumerate(self.clauses):
            clause_watches[idx] = (clause.watch1, clause.watch2)
        watch_lists = {k: list(v) for k, v in self.watch_lists.items()}
        return clause_watches, watch_lists
    
    def restore_state(self, state: Tuple[Dict[int, Tuple[int, int]], Dict[str, List[Tuple[int, int]]]]):
        """Restore saved state of watched literals.
        
        Args:
            state: Tuple of (clause watch positions (Dict), watch lists (Dict))
        
        Returns:
            None
        """
        clause_watches, watch_lists = state
        for idx, (w1, w2) in clause_watches.items():
            self.clauses[idx].watch1 = w1
            self.clauses[idx].watch2 = w2
        self.watch_lists = {k: list(v) for k, v in watch_lists.items()}
    
    def _build_watch_lists(self):
        """Build initial watch lists for all clauses.
        
        Args:
            None
        
        Returns:
            None
        """
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
        """Propagate literal assignment through watched literals.
        
        Args:
            literal: Assigned literal (str)
            model: Variable assignment mapping variable names to bool
        
        Returns:
            Tuple of (new unit literal (str or None), conflict detected (bool))
        """
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
        """Check if all clauses are satisfied.
        
        Args:
            model: Variable assignment mapping variable names to bool
        
        Returns:
            True if all clauses satisfied, False otherwise (bool)
        """
        return all(c.is_satisfied(model) for c in self.clauses)
    
    def add_clause(self, literals: List[str]):
        """Add a new clause to the formula.
        
        Args:
            literals: List of literals (str) forming the clause
        
        Returns:
            None
        """
        clause = WatchedClause(literals)
        idx = len(self.clauses)
        self.clauses.append(clause)
        
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
