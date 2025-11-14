import pytest
from dpll.solver import solve, get_vars
from dpll.verifier import verify

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
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == True

def test_single_variable_sat():
    """Formula: (A)"""
    clauses = [['A']]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == True

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
    assert verify(clauses, solve(vars_list, clauses, []))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == False

def test_pigeonhole_principle_unsat():
    """Formula: (A or B) and (-A) and (-B)"""
    # This forces A=False and B=False, making the first clause False.
    clauses = [
        ['A', 'B'],
        ['-A'],
        ['-B']
    ]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == False

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
    assert verify(clauses, solve(vars_list, clauses, []))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == False

# ====================================================================
# EDGE CASE TEST CASES
# ====================================================================

def test_empty_formula_sat():
    """Formula: (Empty set of clauses)"""
    # This must trigger your first base case (if not clauses: return True)
    clauses = []
    vars_list = []
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == True

def test_empty_clause_unsat():
    """Formula: (A) and ()"""
    # An empty clause means the formula is immediately unsatisfiable
    clauses = [['A'], []]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == False

# ====================================================================
# UNIT PROP TEST CASES
# ====================================================================

def test_unit_prop_chain_sat():
    """
    Tests a chain of unit propagations:
    (A) -> (-A or B) becomes (B)
    (B) -> (-B or C) becomes (C)
    ...which is SAT.
    """
    clauses = [
        ['A'],
        ['-A', 'B'],
        ['-B', 'C']
    ]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == True

def test_unit_prop_chain_unsat():
    """
    Tests a chain of unit propagations that leads to a contradiction:
    (A) -> (-A or B) becomes (B)
    (B) -> (-B or C) becomes (C)
    (C) and (-C) -> ()
    ...which is UNSAT.
    """
    clauses = [
        ['A'],
        ['-A', 'B'],
        ['-B', 'C'],
        ['-C']
    ]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == False
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == False

# ====================================================================
# MISC TEST CASES
# ====================================================================

def test_pure_literal_sat():
    """
    Tests a formula with a 'pure literal' (one that only appears
    in one form, e.g., 'C' is only positive).
    These are always satisfiable.
    Formula: (A or -B) and (B or C) and (-A or C)
    """
    clauses = [
        ['A', '-B'],
        ['B', 'C'],
        ['-A', 'C']
    ]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit", "pure"]))  == True

def test_branch_heavy_sat():
    """
    Tests a problem with no unit clauses, forcing the
    solver to branch immediately.
    Formula: (A or B) and (-A or C) and (B or -C)
    """
    clauses = [
        ['A', 'B'],
        ['-A', 'C'],
        ['B', '-C']
    ]
    vars_list = get_vars(clauses)
    assert verify(clauses, solve(vars_list, clauses, []))  == True
    assert verify(clauses, solve(vars_list, clauses, ["unit"]))  == True