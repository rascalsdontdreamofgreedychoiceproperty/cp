import sys
import os
import time
import argparse

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.vertexcover.solver import (
    solve_vertex_cover,
    is_valid_cover,
    get_edge_count,
    example_graph_1,
    example_graph_2,
    example_graph_3
)

def visualize_graph(graph, cover=None, title="Vertex Cover", layout="spring"):
    """Visualize graph with matplotlib and networkx."""
    try:
        import networkx as nx
        import matplotlib
        import matplotlib.pyplot as plt
        
        # Try to use an interactive backend if available
        backend = matplotlib.get_backend()
        can_display = backend not in ['agg', 'Agg', 'AGG']
        
        if not can_display:
            # Try to switch to an interactive backend
            for gui_backend in ['TkAgg', 'Qt5Agg', 'GTK3Agg', 'WXAgg']:
                try:
                    matplotlib.use(gui_backend, force=True)
                    import matplotlib.pyplot as plt
                    can_display = True
                    break
                except:
                    continue
            
    except ImportError as e:
        print(f"\n\033[93mWarning: Failed to import visualization libraries: {e}\033[0m")
        print("Install with: pip install matplotlib networkx")
        return
    except Exception as e:
        print(f"\n\033[93mWarning: Unexpected error importing libraries: {e}\033[0m")
        return
    
    # Create NetworkX graph
    G = nx.Graph()
    n = len(graph)
    
    # Add all vertices
    G.add_nodes_from(range(n))
    
    # Add edges from adjacency list
    for u in range(n):
        for v in graph[u]:
            if u < v:  # Add each edge once
                G.add_edge(u, v)
    
    # Choose layout
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42, k=1.5, iterations=50)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)
    
    # Create figure
    plt.figure(figsize=(10, 8))
    plt.title(title, fontsize=16, fontweight='bold')
    
    # Draw edges
    if cover is not None:
        cover_set = set(cover)
        
        # Separate covered and uncovered edges
        covered_edges = []
        uncovered_edges = []
        
        for u, v in G.edges():
            if u in cover_set or v in cover_set:
                covered_edges.append((u, v))
            else:
                uncovered_edges.append((u, v))
        
        # Draw covered edges (green)
        nx.draw_networkx_edges(G, pos, edgelist=covered_edges, 
                              edge_color='#2ecc71', width=2, alpha=0.7)
        
        # Draw uncovered edges (red, dashed)
        if uncovered_edges:
            nx.draw_networkx_edges(G, pos, edgelist=uncovered_edges,
                                  edge_color='#e74c3c', width=2, 
                                  style='dashed', alpha=0.7)
        
        # Draw vertices with colors
        node_colors = ['#2ecc71' if v in cover_set else '#95a5a6' for v in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=800, alpha=0.9)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold',
                               font_color='white')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label=f'In Cover ({len(cover)} vertices)'),
            Patch(facecolor='#95a5a6', label='Not in Cover'),
            Patch(facecolor='#2ecc71', label='Covered Edge'),
        ]
        if uncovered_edges:
            legend_elements.append(Patch(facecolor='#e74c3c', label='Uncovered Edge'))
        
        plt.legend(handles=legend_elements, loc='upper right', fontsize=10)
    else:
        # No cover specified, draw plain graph
        nx.draw_networkx_edges(G, pos, edge_color='#34495e', width=2, alpha=0.7)
        nx.draw_networkx_nodes(G, pos, node_color='#3498db', 
                              node_size=800, alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold',
                               font_color='white')
    
    plt.axis('off')
    plt.tight_layout()
    
    # Display the plot or save if no display available
    if can_display:
        plt.show()
    else:
        # Fallback: save to file if display is not available
        fallback_path = f"vertex_cover_{int(time.time())}.png"
        plt.savefig(fallback_path, dpi=150, bbox_inches='tight')
        print(f"\n\033[93mNo display available. Saved to: {fallback_path}\033[0m")
        plt.close()


def print_text_solution(graph, cover, vertex_names=None):
    """Print text-based solution."""
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    
    if vertex_names is None:
        vertex_names = [str(i) for i in range(len(graph))]
    
    if cover is False:
        print(f"\n\033[91mNo solution found :(\033[0m")
        return
    
    cover_set = set(cover)
    cover_names = [vertex_names[i] for i in sorted(cover)]
    
    print(f"\n{GREEN}Vertex Cover (size {len(cover)}):{RESET}")
    print(f"  Vertices: {cover_names}")
    
    print(f"\n{CYAN}Vertex status:{RESET}")
    for i in range(len(graph)):
        status = f"{GREEN}✓ IN COVER{RESET}" if i in cover_set else f"{GREY}✗ not in cover{RESET}"
        print(f"  {vertex_names[i]}: {status}")
    
    # Verify all edges covered
    all_covered = True
    uncovered = []
    for u in range(len(graph)):
        for v in graph[u]:
            if u < v:
                if u not in cover_set and v not in cover_set:
                    all_covered = False
                    uncovered.append((vertex_names[u], vertex_names[v]))
    
    if all_covered:
        print(f"\n{GREEN}All edges covered ✓{RESET}")
    else:
        print(f"\n\033[91mUncovered edges: {uncovered} ✗{RESET}")

def print_graph_info(graph):
    """Print graph information."""
    CYAN = '\033[96m'
    GREY = '\033[90m'
    RESET = '\033[0m'
    
    print(f"{CYAN}Graph Info:{RESET}")
    print(f"  Vertices: {len(graph)}")
    print(f"  Edges: {get_edge_count(graph)}")
    
    print(f"\n{CYAN}Adjacency List:{RESET}")
    for i, neighbors in enumerate(graph):
        print(f"  {i}: {neighbors}")

def main():
    parser = argparse.ArgumentParser(description='Vertex Cover Solver')
    parser.add_argument('heuristics', nargs='*', default=['unit'],
                       help='SAT heuristics: unit, pure, backtracking, etc.')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Show graph visualization')
    parser.add_argument('--graph', '-g', type=int, default=2, choices=[1, 2, 3],
                       help='Example graph to use (1, 2, or 3)')
    parser.add_argument('--layout', '-l', default='spring',
                       choices=['spring', 'circular', 'kamada'],
                       help='Graph layout algorithm')
    parser.add_argument('--no-text', action='store_true',
                       help='Skip text output (visualization only)')
    
    args = parser.parse_args()
    
    # Select graph
    graphs = {1: example_graph_1, 2: example_graph_2, 3: example_graph_3}
    graph = graphs[args.graph]
    
    # Print configuration
    print("=" * 60)
    print(f"VERTEX COVER SOLVER")
    print("=" * 60)
    print(f"Heuristics: {args.heuristics}")
    print(f"Graph: example_{args.graph}")
    
    if not args.no_text:
        print_graph_info(graph)
    
    # SOLVE (timing excludes visualization)
    print(f"\n{'=' * 60}")
    print("SOLVING...")
    print("=" * 60)
    
    start_time = time.time()
    cover = solve_vertex_cover(graph, k=None, heuristics_list=args.heuristics)
    elapsed_time = time.time() - start_time
    
    # Print results
    if cover is not False:
        print(f"\n\033[92msolved :)\033[0m")
        print(f"time: {elapsed_time:.6f}s")
        
        if not args.no_text:
            print_text_solution(graph, cover)
    else:
        print(f"\n\033[91munsolvable :(\033[0m")
        print(f"time: {elapsed_time:.6f}s")
        return
    
    # VISUALIZE (after timing)
    if args.visualize:
        print(f"\n{'=' * 60}")
        print("VISUALIZATION")
        print("=" * 60)
        visualize_graph(graph, cover, 
                       title=f"Vertex Cover (size {len(cover)})",
                       layout=args.layout)

if __name__ == "__main__":
    main()
