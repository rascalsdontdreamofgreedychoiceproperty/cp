import copy
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.vertexcover.backtracking import find_minimum_vertex_cover as backtracking_solve

def variable(vertex):
    """Variable representing vertex in cover."""
    return f"v{vertex}"

def generate_vertex_cover_clauses(graph, k):
    """
    Generate SAT clauses for vertex cover of size k.
    - For each edge (u,v): at least one of u or v must be in cover
    - Exactly k vertices in the cover (using at-most-k and at-least-k)
    """
    clauses = []
    n = len(graph)
    
    # Edge coverage constraints: for each edge, at least one endpoint in cover
    for u in range(n):
        for v in graph[u]:
            if u < v:  # Each edge once
                clauses.append([variable(u), variable(v)])
    
    # At-most-k constraint: no more than k vertices
    # For all combinations of (k+1) vertices, at least one must be false
    if k < n:
        from itertools import combinations
        for combo in combinations(range(n), k + 1):
            clauses.append([f"-{variable(v)}" for v in combo])
    
    # At-least-k constraint: at least k vertices must be true
    # This is harder to encode efficiently, but for small k we can use:
    # "At most (n-k) vertices are NOT in the cover"
    if k > 0:
        from itertools import combinations
        for combo in combinations(range(n), n - k + 1):
            clauses.append([variable(v) for v in combo])
    
    return clauses

def solve_vertex_cover(graph, k=None, heuristics_list=None):
    """
    Solve vertex cover problem.
    If k is None, find minimum k.
    If 'backtracking' in heuristics_list, use backtracking algorithm.
    
    Returns: list of vertex indices in cover, or False if no solution
    """
    if heuristics_list is None:
        heuristics_list = ["unit"]
    
    if "backtracking" in heuristics_list:
        cover = backtracking_solve(graph)
        return cover if cover else False
    
    n = len(graph)
    
    # If k not specified, find minimum k by trying incrementally
    if k is None:
        lower = 0
        upper = n
        
        # Try to find minimum k
        for test_k in range(lower, upper + 1):
            clauses = generate_vertex_cover_clauses(graph, test_k)
            vars_list = get_vars(clauses)
            model = solve(vars_list, clauses, heuristics_list)
            
            if model is not False:
                cover = [v for v in range(n) if variable(v) in model and model[variable(v)] is True]
                return cover
        
        return False
    
    # Solve for specific k
    clauses = generate_vertex_cover_clauses(graph, k)
    vars_list = get_vars(clauses)
    model = solve(vars_list, clauses, heuristics_list)
    
    if model is False:
        return False
    
    cover = [v for v in range(n) if variable(v) in model and model[variable(v)] is True]
    return cover

def is_valid_cover(graph, cover):
    """Verify if cover is valid (all edges covered)."""
    cover_set = set(cover)
    for u in range(len(graph)):
        for v in graph[u]:
            if u < v:
                if u not in cover_set and v not in cover_set:
                    return False
    return True

def get_edge_count(graph):
    """Count total edges in graph."""
    return sum(len(neighbors) for neighbors in graph) // 2

# Example graphs
example_graph_1 = [
    [1, 2],  # 0
    [0, 2],  # 1
    [0, 1]   # 2
]

example_graph_2 = [
    [1, 2],     # 0
    [0, 2, 3],  # 1
    [0, 1, 3],  # 2
    [1, 2, 4],  # 3
    [3, 5],     # 4
    [4]         # 5
]

example_graph_3 = [
    [1, 2, 3, 4],  # 0 (center)
    [0],           # 1
    [0],           # 2
    [0],           # 3
    [0]            # 4
]

if __name__ == "__main__":
    # Simple test when run directly
    import time
    
    heuristics = sys.argv[1:] if len(sys.argv) > 1 else ["unit"]
    graph = example_graph_2
    
    print("heuristics:", heuristics)
    print(f"vertices: {len(graph)}, edges: {get_edge_count(graph)}")
    
    start_time = time.time()
    cover = solve_vertex_cover(graph, k=None, heuristics_list=heuristics)
    elapsed_time = time.time() - start_time
    
    if cover is not False:
        print(f"\nsolved :)")
        print(f"cover: {cover}")
        print(f"size: {len(cover)}")
        print(f"valid: {is_valid_cover(graph, cover)}")
        print(f"\ntime: {elapsed_time:.6f}s")
    else:
        print("\n\033[91munsolvable :(\033[0m")
        print(f"\ntime: {elapsed_time:.6f}s")
