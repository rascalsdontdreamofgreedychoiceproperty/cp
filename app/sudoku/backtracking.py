import copy

def solve_sudoku(board):
    find = find_empty(board)
    if not find:
        return True
    row, col = find

    for num in range(1, 10):
        if is_valid(board, num, row, col):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False

def is_valid(board, num, r, c):
    for i in range(9):
        if board[r][i] == num:
            return False
    for i in range(9):
        if board[i][c] == num:
            return False
    box_x = (c // 3) * 3
    box_y = (r // 3) * 3
    for i in range(box_y, box_y + 3):
        for j in range(box_x, box_x + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

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
    print("unsolved:")
    print_board(original_example_board)

    if solve_sudoku(example_board):
        print("\nsolved :)")
        print_board(example_board, original_example_board)
    else:
        print("\n\033[91munsolvable :(\033[0m")
