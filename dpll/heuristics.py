import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import heapq

try:
    from .helpers import parse_literal, simplify_clauses
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from helpers import parse_literal, simplify_clauses


def unit_propagate(clauses: List[List[str]], model: Dict[str, bool]) -> Tuple[List[List[str]], Dict[str, bool], bool]:
    model = model.copy()
    unit_clauses = {i for i, c in enumerate(clauses) if len(c) == 1}
    
    while unit_clauses:
        idx = unit_clauses.pop()
        if idx >= len(clauses):
            continue
        clause = clauses[idx]
        if len(clause) != 1:
            continue
        
        unit_literal = clause[0]
        var, is_positive = parse_literal(unit_literal)
        
        if var in model:
            if model[var] != is_positive:
                return clauses, model, True
            clauses = simplify_clauses(clauses, unit_literal)
            unit_clauses = {i for i, c in enumerate(clauses) if len(c) == 1}
            continue
        
        model[var] = is_positive
        clauses = simplify_clauses(clauses, unit_literal)
        unit_clauses = {i for i, c in enumerate(clauses) if len(c) == 1}
    
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
    
    pure_literals = []
    for var, pol in polarity.items():
        if pol is not None:
            model[var] = pol
            literal = var if pol else '-' + var
            pure_literals.append(literal)
    
    for literal in pure_literals:
        clauses = simplify_clauses(clauses, literal)
    
    return clauses, model


class VSIDSScorer:
    __slots__ = ['scores', 'increment', 'decay_factor', 'heap', 'heap_valid']
    
    def __init__(self, clauses: List[List[str]], decay_factor: float = 0.95):
        self.scores: Dict[str, float] = {}
        self.increment = 1.0
        self.decay_factor = decay_factor
        self.heap: List[Tuple[float, str]] = []
        self.heap_valid: Dict[str, float] = {}
        self._initialize(clauses)
    
    def _initialize(self, clauses: List[List[str]]):
        for clause in clauses:
            for lit in clause:
                var, _ = parse_literal(lit)
                self.scores[var] = self.scores.get(var, 0.0) + 1.0
        self._rebuild_heap()
    
    def _rebuild_heap(self):
        self.heap = [(-score, var) for var, score in self.scores.items()]
        heapq.heapify(self.heap)
        self.heap_valid = {var: score for var, score in self.scores.items()}
    
    def bump(self, var: str):
        if var in self.scores:
            self.scores[var] += self.increment
            heapq.heappush(self.heap, (-self.scores[var], var))
            self.heap_valid[var] = self.scores[var]
    
    def bump_clause(self, clause: List[str]):
        for lit in clause:
            var, _ = parse_literal(lit)
            self.bump(var)
    
    def decay(self):
        self.increment /= self.decay_factor
    
    def pick_variable(self, model: Dict[str, bool]) -> Optional[str]:
        while self.heap:
            neg_score, var = heapq.heappop(self.heap)
            if var in model:
                continue
            if self.heap_valid.get(var) != -neg_score:
                continue
            heapq.heappush(self.heap, (neg_score, var))
            return var
        return None
    
    def copy(self) -> 'VSIDSScorer':
        new = object.__new__(VSIDSScorer)
        new.scores = self.scores.copy()
        new.increment = self.increment
        new.decay_factor = self.decay_factor
        new.heap = list(self.heap)
        new.heap_valid = self.heap_valid.copy()
        return new
