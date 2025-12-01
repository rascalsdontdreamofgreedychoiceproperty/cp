import os
import pdb

def parse_dimacs_clq(filename):
    """
    Parses a DIMACS CLQ file, for a vertex cover dataset graph.

    Args:
        filename (str): The path to the .clq file.

    Returns:
        list of (list of int): an adjacency matrix
    """
    # A flag to ensure we only see one 'p' line
    found_problem_line = False

    with open(filename, 'r') as f:
        for line in f:
            # Remove leading/trailing whitespace
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comment lines
            if line.startswith('c'):
                continue

            # Skip DIMACS terminator
            if line == '%' or line.startswith('%'):
                break

            # Parse the problem line (e.g., "p col 5 3")
            if line.startswith('p'):
                if found_problem_line:
                    raise ValueError("Found multiple 'p' lines in DIMACS file.")

                parts = line.split()
                # if len(parts) != 4 or parts[1] != 'cnf':
                # don't check for prob type since we just use a max clique prob
                if len(parts) != 4:
                    raise ValueError(f"Invalid DIMACS 'p' line: {line}")

                # problem line tells us the number of vertices and edges
                v = int(parts[2])
                e = int(parts[3])
                # initialize the adjacency list
                graph = [[] for _ in range(v)]

                found_problem_line = True
                continue

            # If we haven't found the 'p' line yet, but this isn't a comment,
            # it's an error (or we should just skip it).
            if not found_problem_line:
                print(f"Warning: Skipping line before 'p' line: {line}")
                continue

            # --- Parse edge lines ---

            parts = line.split()
            # add edge to adjlist
            # NOTE the dataset is 1-indexed, while solver is 0-indexed
            graph[int(parts[1]) - 1].append(int(parts[2]) - 1)

    return graph
