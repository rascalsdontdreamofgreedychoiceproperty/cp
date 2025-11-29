import copy

def find_minimum_vertex_cover(graph):
    """Find minimum vertex cover using backtracking with optimization."""
    n = len(graph)
    best_cover = list(range(n))  # Start with all vertices
    current_cover = []
    
    def backtrack(vertex_idx, current_cover, uncovered_edges):
        nonlocal best_cover
        
        # Pruning: if current cover already >= best, abandon this branch
        if len(current_cover) >= len(best_cover):
            return
        
        # Base case: all vertices considered
        if vertex_idx == n:
            if len(uncovered_edges) == 0:
                best_cover = current_cover[:]
            return
        
        # Early termination: if no uncovered edges remain
        if len(uncovered_edges) == 0:
            best_cover = current_cover[:]
            return
        
        # Branch 1: Include current vertex in cover
        edges_covered = get_edges_covered(graph, vertex_idx, uncovered_edges)
        if edges_covered:
            new_uncovered = uncovered_edges - edges_covered
            backtrack(vertex_idx + 1, current_cover + [vertex_idx], new_uncovered)
        
        # Branch 2: Exclude current vertex from cover
        backtrack(vertex_idx + 1, current_cover, uncovered_edges)
    
    all_edges = get_all_edges(graph)
    backtrack(0, [], all_edges)
    return best_cover

def get_all_edges(graph):
    """Get set of all edges in the graph."""
    edges = set()
    for u in range(len(graph)):
        for v in graph[u]:
            if u < v:  # Avoid duplicate edges
                edges.add((u, v))
    return edges

def get_edges_covered(graph, vertex, uncovered_edges):
    """Get edges that would be covered by including this vertex."""
    covered = set()
    for edge in uncovered_edges:
        if vertex in edge:
            covered.add(edge)
    return covered

def is_vertex_cover(graph, cover):
    """Verify if a set of vertices forms a valid vertex cover."""
    cover_set = set(cover)
    for u in range(len(graph)):
        for v in graph[u]:
            if u < v:  # Check each edge once
                if u not in cover_set and v not in cover_set:
                    return False
    return True

def print_graph(graph, vertex_names=None):
    """Print graph in a readable format."""
    GREY = '\033[90m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    
    if vertex_names is None:
        vertex_names = [str(i) for i in range(len(graph))]
    
    print(f"{CYAN}Graph (adjacency list):{RESET}")
    for i, neighbors in enumerate(graph):
        neighbor_names = [vertex_names[n] for n in neighbors]
        print(f"  {vertex_names[i]}: {neighbor_names}")

def print_solution(graph, cover, vertex_names=None):
    """Print the minimum vertex cover solution."""
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    RESET = '\033[0m'
    
    if vertex_names is None:
        vertex_names = [str(i) for i in range(len(graph))]
    
    cover_set = set(cover)
    cover_names = [vertex_names[i] for i in sorted(cover)]
    
    print(f"\n{GREEN}Minimum Vertex Cover (size {len(cover)}):{RESET}")
    print(f"  Vertices: {cover_names}")
    
    print(f"\n{WHITE}Vertex status:{RESET}")
    for i in range(len(graph)):
        status = f"{GREEN}✓ IN COVER{RESET}" if i in cover_set else f"{GREY}✗ not in cover{RESET}"
        print(f"  {vertex_names[i]}: {status}")
    
    print(f"\n{WHITE}Edge coverage verification:{RESET}")
    all_covered = True
    for u in range(len(graph)):
        for v in graph[u]:
            if u < v:
                covered = u in cover_set or v in cover_set
                status = f"{GREEN}✓{RESET}" if covered else f"{GREY}✗{RESET}"
                print(f"  {status} ({vertex_names[u]}, {vertex_names[v]})")
                if not covered:
                    all_covered = False
    
    if all_covered:
        print(f"\n{GREEN}All edges covered ✓{RESET}")
    else:
        print(f"\n\033[91mSome edges not covered ✗{RESET}")

# Example graph 1: Simple triangle
example_graph_1 = [
    [1, 2],  # 0 connects to 1, 2
    [0, 2],  # 1 connects to 0, 2
    [0, 1]   # 2 connects to 0, 1
]

# Example graph 2: More complex graph
example_graph_2 = [
    [1, 2],     # 0
    [0, 2, 3],  # 1
    [0, 1, 3],  # 2
    [1, 2, 4],  # 3
    [3, 5],     # 4
    [4]         # 5
]

if __name__ == "__main__":
    print("=" * 50)
    print("EXAMPLE 1: Triangle Graph")
    print("=" * 50)
    print_graph(example_graph_1)
    
    cover = find_minimum_vertex_cover(example_graph_1)
    print_solution(example_graph_1, cover)
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Complex Graph")
    print("=" * 50)
    print_graph(example_graph_2)
    
    cover = find_minimum_vertex_cover(example_graph_2)
    print_solution(example_graph_2, cover)
    
    # Verify the solution
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
    is_valid = is_vertex_cover(example_graph_2, cover)
    if is_valid:
        print("\033[92mSolution is valid ✓\033[0m")
    else:
        print("\033[91mSolution is invalid ✗\033[0m")
