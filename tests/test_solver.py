import pytest
from dpll.solver import solve, get_vars

# ====================================================================
# SATISFIABLE TEST CASES (Expected Result: True)
# ====================================================================

def test_simple_sat():
    """Formula: (A or B) and (-A or B) and (-B or C)"""
    clauses = [
        ['A', 'B'],
        ['-A', 'B'],
        ['-B', 'C']
    ]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == True

def test_single_variable_sat():
    """Formula: (A)"""
    clauses = [['A']]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == True

# ====================================================================
# UNSATISFIABLE TEST CASES (Expected Result: False)
# ====================================================================

def test_trivial_unsat():
    """Formula: (A) and (-A)"""
    clauses = [
        ['A'],
        ['-A']
    ]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == False

def test_pigeonhole_principle_unsat():
    """Formula: (A or B) and (-A) and (-B)"""
    # This forces A=False and B=False, making the first clause False.
    clauses = [
        ['A', 'B'],
        ['-A'],
        ['-B']
    ]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == False

def test_small_contradiction_unsat():
    """Formula: (A or B) and (-A or B) and (A or -B) and (-A or -B)"""
    # Contradiction on A and B (requires B=True and B=False simultaneously)
    clauses = [
        ['A', 'B'],
        ['-A', 'B'],
        ['A', '-B'],
        ['-A', '-B']
    ]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == False

# ====================================================================
# EDGE CASE TEST CASES
# ====================================================================

def test_empty_formula_sat():
    """Formula: (Empty set of clauses)"""
    # This must trigger your first base case (if not clauses: return True)
    clauses = []
    vars_list = []
    assert solve(vars_list, clauses) == True

def test_empty_clause_unsat():
    """Formula: (A) and ()"""
    # An empty clause means the formula is immediately unsatisfiable
    clauses = [['A'], []]
    vars_list = get_vars(clauses)
    assert solve(vars_list, clauses) == False