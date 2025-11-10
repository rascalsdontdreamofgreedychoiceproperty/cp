import copy
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.sudoku.backtracking import solve_sudoku as backtracking_solve

def variable(r, c, n):
    return f"{r}-{c}-{n}"

def generate_sudoku_clauses():
    clauses = []
    
    for r in range(9):
        for c in range(9):
            clauses.append([variable(r, c, n) for n in range(1, 10)])
            for n1 in range(1, 10):
                for n2 in range(n1 + 1, 10):
                    clauses.append([f"-{variable(r, c, n1)}", f"-{variable(r, c, n2)}"])

    for n in range(1, 10):
        for r in range(9):
            clauses.append([variable(r, c, n) for c in range(9)])
            for c1 in range(9):
                for c2 in range(c1 + 1, 9):
                    clauses.append([f"-{variable(r, c1, n)}", f"-{variable(r, c2, n)}"])
        
        for c in range(9):
            clauses.append([variable(r, c, n) for r in range(9)])
            for r1 in range(9):
                for r2 in range(r1 + 1, 9):
                    clauses.append([f"-{variable(r1, c, n)}", f"-{variable(r2, c, n)}"])

    for br in range(3):
        for bc in range(3):
            for n in range(1, 10):
                cells_in_box = []
                for r_offset in range(3):
                    for c_offset in range(3):
                        cells_in_box.append(variable(br * 3 + r_offset, bc * 3 + c_offset, n))
                
                clauses.append(cells_in_box)
                for i in range(len(cells_in_box)):
                    for j in range(i + 1, len(cells_in_box)):
                        clauses.append([f"-{cells_in_box[i]}", f"-{cells_in_box[j]}"])
                        
    return clauses

BASE_SUDOKU_CLAUSES = generate_sudoku_clauses()

def solve_sudoku(board, heuristics_list):
    if "backtracking" in heuristics_list:
        return backtracking_solve(board)
    
    clauses = copy.deepcopy(BASE_SUDOKU_CLAUSES)
    
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                clauses.append([variable(r, c, board[r][c])])

    vars_list = get_vars(clauses)
    model = solve(vars_list, clauses, heuristics_list)
    
    if model is False:
        return False
    
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for n in range(1, 10):
                    var = variable(r, c, n)
                    if var in model and model[var] is True:
                        board[r][c] = n
                        break
    return True

def print_board(board, original_board=None):
    GREY = '\033[90m'
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    is_solved_board = original_board is not None

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print(f"{GREY}- - - - - - - - - - -{RESET}")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(f"{GREY}|{RESET} ", end="")
            
            cell = board[i][j]
            if cell == 0:
                print("  ", end="")
                continue

            if is_solved_board:
                if original_board[i][j] != 0:
                    print(f"{WHITE}{cell}{RESET} ", end="")
                else:
                    print(f"{GREEN}{cell}{RESET} ", end="")
            else:
                print(f"{WHITE}{cell}{RESET} ", end="")
        print()

example_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

original_example_board = copy.deepcopy(example_board)

if __name__ == "__main__":
    heuristics = sys.argv[1:]
    
    if not heuristics:
        heuristics = ["unit"]
        
    print("unsolved:")
    print_board(original_example_board)

    if solve_sudoku(example_board, heuristics):
        print("\nsolved :)")
        print_board(example_board, original_example_board)
    else:
        print("\n\033[91munsolvable :(\033[0m")
