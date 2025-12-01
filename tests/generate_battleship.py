import csv
import random
import os

# Constants matching your app
UNKNOWN = -1
WATER = 0
SHIP = 1

CHAR_MAP = {
    UNKNOWN: '?',
    WATER: '.',
    SHIP: 'X'
}

def create_empty_board(rows, cols):
    return [[WATER for _ in range(cols)] for _ in range(rows)]

def get_neighbors(r, c, rows, cols):
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

def can_place_ship_logic(board, r, c, length, orientation, rows, cols):
    # Check bounds and overlap/adjacency
    ship_cells = []
    if orientation == 'h':
        if c + length > cols: return False
        ship_cells = [(r, c + i) for i in range(length)]
    else:
        if r + length > rows: return False
        ship_cells = [(r + i, c) for i in range(length)]

    for (sr, sc) in ship_cells:
        # Check overlap
        if board[sr][sc] == SHIP: return False
        # Check neighbors (must be water)
        for nr, nc in get_neighbors(sr, sc, rows, cols):
            if board[nr][nc] == SHIP:
                # If the neighbor is part of THIS ship, it's fine. 
                # But since we are placing it new, any existing SHIP is a conflict.
                return False
    return True

def place_ship(board, r, c, length, orientation):
    if orientation == 'h':
        for i in range(length):
            board[r][c + i] = SHIP
    else:
        for i in range(length):
            board[r + i][c] = SHIP

def generate_solution_board(rows, cols, fleet):
    """Generates a fully solved valid board with the given fleet."""
    board = create_empty_board(rows, cols)
    
    # Sort fleet largest to smallest (easier to place)
    sorted_fleet = sorted(fleet, reverse=True)
    
    for length in sorted_fleet:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            orientation = random.choice(['h', 'v'])
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)
            
            if can_place_ship_logic(board, r, c, length, orientation, rows, cols):
                place_ship(board, r, c, length, orientation)
                placed = True
            attempts += 1
        
        if not placed:
            return None # Failed to place all ships
            
    return board

def mask_board(solution_board, clue_density=0.3):
    """
    Takes a solution and hides cells to create the puzzle.
    clue_density: Probability a cell remains visible (as Water or Ship).
    """
    rows = len(solution_board)
    cols = len(solution_board[0])
    puzzle = []
    
    for r in range(rows):
        row_str = []
        for c in range(cols):
            val = solution_board[r][c]
            # Randomly decide to hide it
            if random.random() > clue_density:
                row_str.append(CHAR_MAP[UNKNOWN])
            else:
                row_str.append(CHAR_MAP[val])
        puzzle.append("".join(row_str))
        
    return puzzle

def generate_random_board_string(rows, cols):
    """Generates a random string of ?, ., X characters."""
    chars = ['?', '.', 'X']
    board_str = []
    for _ in range(rows):
        row = "".join(random.choice(chars) for _ in range(cols))
        board_str.append(row)
    return board_str

def main():
    # Ensure directory exists
    folder = os.path.dirname(__file__)
    if not folder: folder = "."
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filepath = os.path.join(folder, "battleship.csv")
    print(f"Generating Battleship dataset at {filepath}...")

    # Configuration
    ROWS, COLS = 10, 10
    FLEET = [5, 4, 3, 3, 2] # Standard-ish fleet
    FLEET_STR = "5,4,3,3,2"
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(["id", "type", "rows", "cols", "fleet", "board"])
        
        count = 0
        # 1. Generate 100 Solvable Puzzles
        while count < 100:
            sol_board = generate_solution_board(ROWS, COLS, FLEET)
            if sol_board:
                # Create a puzzle representation (list of row strings joined by |)
                puzzle_rows = mask_board(sol_board, clue_density=0.25)
                puzzle_str = "|".join(puzzle_rows)
                
                writer.writerow([f"S{count}", "solvable", ROWS, COLS, FLEET_STR, puzzle_str])
                count += 1
                if count % 20 == 0: print(f"  Generated {count} solvable...")

        # 2. Generate 100 Random Puzzles (Likely Unsolvable)
        for i in range(100):
            # Create random strings
            puzzle_rows = generate_random_board_string(ROWS, COLS)
            puzzle_str = "|".join(puzzle_rows)
            writer.writerow([f"R{i}", "random", ROWS, COLS, FLEET_STR, puzzle_str])
            
    print("Done! Created 200 Battleship puzzles.")

if __name__ == "__main__":
    main()
