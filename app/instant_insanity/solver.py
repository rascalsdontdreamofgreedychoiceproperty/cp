import sys
import os
import time
import copy

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars

# ==============================================================================
# 1. CUBE GEOMETRY & UTILS
# ==============================================================================

# Standard face indices: 0:Front, 1:Back, 2:Left, 3:Right, 4:Top, 5:Bottom
# We need to generate all 24 rotations. 
# We define a rotation by specifying which original face ends up at [F, B, L, R, T, B]
# But we mostly care about the SIDE faces (F, R, B, L) for the puzzle constraints.

def get_permutations():
    """
    Returns list of 24 permutations. 
    Each perm is a list of 6 indices mapping (F,B,L,R,T,B) to original indices.
    """
    # Base faces
    # F B L R T B
    # 0 1 2 3 4 5
    
    # We generate rotations by fixing a Top face, then rotating around it.
    # Pairs are (0,1), (2,3), (4,5).
    
    # (Top, Bottom) pairs and the corresponding ring of sides (F, R, B, L)
    axes = [
        (4, 5, [0, 3, 1, 2]), # Top=4, Bottom=5, Ring=Front, Right, Back, Left
        (5, 4, [0, 2, 1, 3]), # Top=5, Bottom=4 (flipped Z)
        (0, 1, [4, 3, 5, 2]), # Top=0, Bottom=1 (Front becomes Top)
        (1, 0, [4, 2, 5, 3]), # Top=1, Bottom=0
        (2, 3, [4, 0, 5, 1]), # Top=2, Bottom=3 (Left becomes Top)
        (3, 2, [4, 1, 5, 0]), # Top=3, Bottom=2
    ]
    
    perms = []
    
    for top, bot, ring in axes:
        # Rotate the ring 4 times
        for i in range(4):
            # Current ring configuration
            # sides: F, R, B, L
            f = ring[i]
            r = ring[(i+1)%4]
            b = ring[(i+2)%4]
            l = ring[(i+3)%4]
            
            # Map to standard output format: F, B, L, R, T, B
            # Note: The solver mainly cares about indices 0(F), 3(R), 1(B), 2(L) for constraints
            perm = [f, b, l, r, top, bot]
            perms.append(perm)
            
    return perms

PERMUTATIONS = get_permutations()

def get_cube_state(cube_colors, state_idx):
    """
    Returns the colors of the cube in a specific orientation.
    Returns list of colors: [F, B, L, R, T, B]
    """
    perm = PERMUTATIONS[state_idx]
    return [cube_colors[i] for i in perm]

# ==============================================================================
# 2. SAT REDUCTION
# ==============================================================================

def variable(cube_idx, state_idx):
    """Variable: Cube C is in State S."""
    return f"c{cube_idx}_{state_idx}"

def generate_insanity_clauses(cubes):
    clauses = []
    num_cubes = len(cubes)
    num_states = 24
    
    # 1. State Constraints: Each cube must be in exactly one state
    for i in range(num_cubes):
        # At least one state
        clauses.append([variable(i, s) for s in range(num_states)])
        
        # At most one state (pairwise exclusion)
        for s1 in range(num_states):
            for s2 in range(s1 + 1, num_states):
                clauses.append([f"-{variable(i, s1)}", f"-{variable(i, s2)}"])

    # 2. Puzzle Constraints: Sides must have unique colors
    # For every pair of cubes, if their chosen states put the SAME color 
    # on the SAME side (Front, Back, Left, or Right), forbid that pair.
    
    # Pre-calculate faces for all cubes in all states to speed up generation
    cube_configs = []
    for i in range(num_cubes):
        configs = []
        for s in range(num_states):
            # [F, B, L, R, T, B]
            configs.append(get_cube_state(cubes[i], s))
        cube_configs.append(configs)

    # Indices of side faces in the state array: Front=0, Back=1, Left=2, Right=3
    side_indices = [0, 1, 2, 3] 
    
    for i in range(num_cubes):
        for j in range(i + 1, num_cubes):
            for si in range(num_states):
                for sj in range(num_states):
                    # Check for conflict
                    conflict = False
                    faces_i = cube_configs[i][si]
                    faces_j = cube_configs[j][sj]
                    
                    for face_idx in side_indices:
                        if faces_i[face_idx] == faces_j[face_idx]:
                            conflict = True
                            break
                    
                    if conflict:
                        # Logic: NOT (Cube i is Si AND Cube j is Sj)
                        # CNF: NOT Cube i is Si OR NOT Cube j is Sj
                        clauses.append([f"-{variable(i, si)}", f"-{variable(j, sj)}"])
                        
    return clauses

# ==============================================================================
# 3. SOLVER INTERFACE
# ==============================================================================

def solve_instant_insanity(cubes, heuristics_list=None):
    if heuristics_list is None:
        heuristics_list = ["unit"]

    clauses = generate_insanity_clauses(cubes)
    vars_list = get_vars(clauses)
    
    model = solve(vars_list, clauses, heuristics_list)
    
    if model is False:
        return False
    
    # Decode solution
    solution = []
    for i in range(len(cubes)):
        found = False
        for s in range(24):
            var = variable(i, s)
            if var in model and model[var] is True:
                config = get_cube_state(cubes[i], s)
                solution.append({
                    "cube_idx": i,
                    "state_idx": s,
                    "colors": config, # [F, B, L, R, T, B]
                    "sides": [config[0], config[3], config[1], config[2]] # F, R, B, L order for printing
                })
                found = True
                break
        if not found:
            # Should not happen if model is valid
            return False
            
    return solution

def print_solution(solution):
    print("\nSOLUTION FOUND:")
    print("Stack configuration (Top to Bottom):")
    print("-" * 60)
    print(f"{'Cube':<6} | {'Front':<8} {'Right':<8} {'Back':<8} {'Left':<8} | {'Top':<8} {'Bottom':<8}")
    print("-" * 60)
    
    # We verify the column uniqueness visually
    cols = [[], [], [], []] # F, R, B, L
    
    for item in solution:
        c = item['colors']
        # c indices: 0:F, 1:B, 2:L, 3:R, 4:T, 5:B
        # Row output: F, R, B, L
        print(f"#{item['cube_idx']+1:<5} | {c[0]:<8} {c[3]:<8} {c[1]:<8} {c[2]:<8} | {c[4]:<8} {c[5]:<8}")
        
        cols[0].append(c[0])
        cols[1].append(c[3])
        cols[2].append(c[1])
        cols[3].append(c[2])

    print("-" * 60)
    print("Check Sides (Should be unique):")
    sides = ["Front", "Right", "Back", "Left"]
    for i in range(4):
        print(f"{sides[i]:<6}: {cols[i]} {'(OK)' if len(set(cols[i]))==4 else '(FAIL)'}")

# ==============================================================================
# 4. MAIN & EXAMPLES
# ==============================================================================

if __name__ == "__main__":
    # Example Instance
    # Format: Front, Back, Left, Right, Top, Bottom
    # Colors: R, G, B, W
    
    example_cubes = [
        # Cube 1: B G W G R R
        "BGWGRR",
        # Cube 2: W G B R R W
        "WGBRRW",
        # Cube 3: R W G G B R
        "RWGGBR",
        # Cube 4: R R W G B G
        "RRWGBG"
    ]
    
    # Note: If your input strings are different (e.g., standard unfolding), 
    # you simply map them to the [F, B, L, R, T, B] indices before passing here.
    
    heuristics = sys.argv[1:] if len(sys.argv) > 1 else ["unit"]
    
    print("Instant Insanity Solver")
    print(f"Heuristics: {heuristics}")
    print("Solving...")
    
    start_time = time.time()
    result = solve_instant_insanity(example_cubes, heuristics)
    elapsed = time.time() - start_time
    
    if result:
        print_solution(result)
    else:
        print("\nNo solution found.")
        
    print(f"\nTime: {elapsed:.4f}s")
