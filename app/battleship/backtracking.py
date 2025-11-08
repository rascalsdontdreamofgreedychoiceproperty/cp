UNKNOWN = -1
WATER = 0
SHIP = 1

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

def solve_battleship(board, fleet):
    ROWS = len(board)
    COLS = len(board[0])
    
    if not fleet:
        return True
    
    ship_length = fleet[0]
    remaining_fleet = fleet[1:]

    for r in range(ROWS):
        for c in range(COLS):
            for orientation in ['horizontal', 'vertical']:
                
                if can_place_ship(board, ship_length, r, c, orientation):
                    
                    set_ship(board, ship_length, r, c, orientation, SHIP)
                    
                    if solve_battleship(board, remaining_fleet):
                        return True
                        
                    set_ship(board, ship_length, r, c, orientation, UNKNOWN)

    return False

def can_place_ship(board, length, r_start, c_start, orientation):
    ROWS = len(board)
    COLS = len(board[0])
    
    ship_cells = []
    
    if orientation == 'horizontal':
        if c_start + length > COLS:
            return False
        
        for c in range(c_start, c_start + length):
            ship_cells.append((r_start, c))
            
    else:
        if r_start + length > ROWS:
            return False
            
        for r in range(r_start, r_start + length):
            ship_cells.append((r, c_start))

    for r, c in ship_cells:
        if board[r][c] == WATER:
            return False
        if board[r][c] == SHIP:
            return False 

    for r, c in ship_cells:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue 

                nr, nc = r + dr, c + dc
                
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if board[nr][nc] == SHIP and (nr, nc) not in ship_cells:
                        return False
                        
    return True

def set_ship(board, length, r_start, c_start, orientation, value):
    if orientation == 'horizontal':
        for c in range(c_start, c_start + length):
            board[r_start][c] = value
            
    else:
        for r in range(r_start, r_start + length):
            board[r][c_start] = value

def print_board_battleship(board):
    ROWS = len(board)
    COLS = len(board[0])
    
    col_headers = " ".join([str(i) for i in range(COLS)])
    print(f"  {GREY}{col_headers}{RESET}")
    
    for r in range(ROWS):
        print(f"{GREY}{r}{RESET} ", end="")
        for c in range(COLS):
            print(PRINT_MAP[board[r][c]] + " ", end="")
        print()

if __name__ == "__main__":
    U, W = UNKNOWN, WATER
    
    example_board = [
        [W, U, U, U, U, W], # 0
        [U, U, U, U, U, U], # 1
        [U, U, W, U, U, U], # 2
        [U, U, U, U, U, U], # 3
        [U, U, U, U, U, U], # 4
        [W, U, U, U, U, W]  # 5
    #    0  1  2  3  4  5
    ]

    board_size = len(example_board)

    fleet_to_place = [4, 3, 2, 2] 

    print("board:")
    print_board_battleship(example_board)
    print(f"\nfleet to place: {fleet_to_place}")

    if solve_battleship(example_board, fleet_to_place):
        print("\nsolved :)")
        
        ROWS = len(example_board)
        COLS = len(example_board[0])
        for r in range(ROWS):
            for c in range(COLS):
                if example_board[r][c] == UNKNOWN:
                    example_board[r][c] = WATER
        
        print_board_battleship(example_board)
    else:
        print("\nno solution :(")
