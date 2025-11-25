import os

def parse_dimacs_cnf(filename):
    """
    Parses a DIMACS CNF file.

    Args:
        filename (str): The path to the .cnf file.

    Returns:
        (int, int, list): A tuple (num_vars, num_clauses, clauses)
        - num_vars: The number of variables declared.
        - num_clauses: The number of clauses declared.
        - clauses: A list of lists, where each inner list is a clause
                   represented by integers.
    """
    clauses = []
    num_vars = 0
    num_clauses = 0
    
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
            
            # Parse the problem line (e.g., "p cnf 5 3")
            if line.startswith('p'):
                if found_problem_line:
                    raise ValueError("Found multiple 'p' lines in DIMACS file.")
                
                parts = line.split()
                if len(parts) != 4 or parts[1] != 'cnf':
                    raise ValueError(f"Invalid DIMACS 'p' line: {line}")
                
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
                found_problem_line = True
                continue

            # If we haven't found the 'p' line yet, but this isn't a comment,
            # it's an error (or we should just skip it).
            if not found_problem_line:
                print(f"Warning: Skipping line before 'p' line: {line}")
                continue

            # --- Parse clause lines ---
            # Any other non-empty, non-comment line is a clause
            
            # Split the line into literals (as strings)
            literals_str = line.split()
            
            clause = []
            for lit_str in literals_str:
                lit_int = int(lit_str)
                
                if lit_int == 0:
                    # '0' terminates the clause, so we stop reading
                    break 
                
                # Check for validity (optional but good)
                if abs(lit_int) > num_vars:
                    print(f"Warning: Literal {lit_int} exceeds declared var count {num_vars}")
                
                clause.append(lit_int)
            
            # Add the valid clause to our list
            # A line with just '0' or an empty line will result
            # in an empty 'clause' list, which we skip.
            if clause:
                clauses.append(clause)

    # A final check to see if the declared number of clauses matches
    if len(clauses) != num_clauses:
        print(f"Warning: Declared {num_clauses} clauses, but parsed {len(clauses)}")

    return num_vars, num_clauses, clauses
# ---clauses contains the list of classes for our purpose
# --- Example Usage ---

#Commenting out example usage to avoid execution during import
# 1. Define the content for a dummy test file
'''cnf_content = """c This is a comment.
c
p cnf 5 3
1 -5 4 0
-1 5 3 2 0
-3 -4 0
"""

test_filename = "test_problem.cnf"

try:
    # 2. Create the dummy file
    with open(test_filename, "w") as f:
        f.write(cnf_content)

    # 3. Parse the file
    num_vars, num_clauses, clauses_list = parse_dimacs_cnf(test_filename)
    
    print(f"--- Successfully Parsed {test_filename} ---")
    print(f"Declared Variables: {num_vars}")
    print(f"Declared Clauses: {num_clauses}")
    print("\nClauses Found:")
    for i, clause in enumerate(clauses_list):
        print(f"  Clause {i+1}: {clause}")

except FileNotFoundError:
    print(f"Error: File '{test_filename}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 4. Clean up (remove) the dummy file
    if os.path.exists(test_filename):
        os.remove(test_filename)
        print(f"\nCleaned up {test_filename}.")
'''