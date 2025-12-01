import copy
import sys
import os
import time

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.battleship.backtracking import solve_battleship as backtracking_solve
from app.battleship.backtracking import UNKNOWN, WATER, SHIP

def variable(i, r, c, o):
    return f"{i:02d}-{r:02d}-{c:02d}-{o}"

def parse_variable(var_str):
    parts = var_str.split('-')
    return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])

def get_occupied_cells(r, c, length, orientation):
    cells = set()
    if orientation == 0:
        for k in range(length):
            cells.add((r, c + k))
    else:
        for k in range(length):
            cells.add((r + k, c))
    return cells

def get_conflict_zone(r, c, length, orientation, rows, cols):
    occupied = get_occupied_cells(r, c, length, orientation)
    zone = set(occupied)
    
    for (or_r, or_c) in occupied:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = or_r + dr, or_c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    zone.add((nr, nc))
    return zone

def generate_battleship_clauses(board, fleet):
    rows = len(board)
    cols = len(board[0])
    clauses = []
    
    vars_by_ship = {i: [] for i in range(len(fleet))}
    var_info = {}

    for i, length in enumerate(fleet):
        for r in range(rows):
            for c in range(cols - length + 1):
                occupied = get_occupied_cells(r, c, length, 0)
                if any(board[rr][cc] == WATER for rr, cc in occupied):
                    continue
                    
                var = variable(i, r, c, 0)
                vars_by_ship[i].append(var)
                var_info[var] = {
                    'occupied': occupied,
                    'conflict': get_conflict_zone(r, c, length, 0, rows, cols)
                }
        
        for r in range(rows - length + 1):
            for c in range(cols):
                occupied = get_occupied_cells(r, c, length, 1)
                if any(board[rr][cc] == WATER for rr, cc in occupied):
                    continue

                var = variable(i, r, c, 1)
                vars_by_ship[i].append(var)
                var_info[var] = {
                    'occupied': occupied,
                    'conflict': get_conflict_zone(r, c, length, 1, rows, cols)
                }

    for i in range(len(fleet)):
        ship_vars = vars_by_ship[i]
        
        clauses.append(ship_vars)
        
        for idx1 in range(len(ship_vars)):
            for idx2 in range(idx1 + 1, len(ship_vars)):
                clauses.append([f"-{ship_vars[idx1]}", f"-{ship_vars[idx2]}"])
        
    for i in range(len(fleet)):
        for j in range(i + 1, len(fleet)):
            for var1 in vars_by_ship[i]:
                occ1 = var_info[var1]['occupied']
                for var2 in vars_by_ship[j]:
                    conf2 = var_info[var2]['conflict']
                    
                    if not occ1.isdisjoint(conf2):
                        clauses.append([f"-{var1}", f"-{var2}"])

    return clauses

def solve_battleship(board, fleet, heuristics_list):
    if "backtracking" in heuristics_list:
        result = backtracking_solve(board, fleet)
        if result:
            rows = len(board)
            cols = len(board[0])
            for r in range(rows):
                for c in range(cols):
                    if board[r][c] == UNKNOWN:
                        board[r][c] = WATER
        return result
    
    clauses = generate_battleship_clauses(board, fleet)
    vars_list = get_vars(clauses)
    
    model = solve(vars_list, clauses, heuristics_list)
    
    if model is False:
        return False
    
    rows = len(board)
    cols = len(board[0])
    
    for r in range(rows):
        for c in range(cols):
            board[r][c] = WATER
            
    for var, val in model.items():
        if val is True:
            try:
                i, r, c, orient = parse_variable(var)
                length = fleet[i]
                
                if orient == 0:
                    for k in range(length):
                        board[r][c + k] = SHIP
                else:
                    for k in range(length):
                        board[r + k][c] = SHIP
            except ValueError:
                continue

    return True

def print_board(board):
    GREY = '\033[90m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    
    PRINT_MAP = {
        UNKNOWN: f'{YELLOW}?{RESET}',
        WATER:   f'{BLUE}~{RESET}',
        SHIP:    f'{RED}x{RESET}'
    }

    ROWS = len(board)
    COLS = len(board[0])
    
    col_headers = " ".join([str(i) for i in range(COLS)])
    print(f"  {GREY}{col_headers}{RESET}")
    
    for r in range(ROWS):
        print(f"{GREY}{r}{RESET} ", end="")
        for c in range(COLS):
            print(PRINT_MAP[board[r][c]] + " ", end="")
        print()

U, W = UNKNOWN, WATER

example_board = [
    [W, U, U, U, U, W],
    [U, U, U, U, U, U],
    [U, U, W, U, U, U],
    [U, U, U, U, U, U],
    [U, U, U, U, U, U],
    [W, U, U, U, U, W]
]

example_fleet = [4, 3, 2, 2]

if __name__ == "__main__":
    heuristics = sys.argv[1:]
    
    if not heuristics:
        heuristics = ["unit"]

    print("heuristics:", heuristics)
        
    print("board:")
    print_board(example_board)
    print(f"\nfleet to place: {example_fleet}")

    start_time = time.time()
    if solve_battleship(example_board, example_fleet, heuristics):
        elapsed_time = time.time() - start_time
        print("\nsolved :)")
        print_board(example_board)
        print(f"\ntime: {elapsed_time:.6f}s")
    else:
        elapsed_time = time.time() - start_time
        print("\n\033[91munsolvable :(\033[0m")
        print(f"\ntime: {elapsed_time:.6f}s")