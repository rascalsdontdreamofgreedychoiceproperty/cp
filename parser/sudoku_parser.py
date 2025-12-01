# parser/sudoku_parser.py
import csv
import os

def parse_sudoku_csv(filepath, limit=None):
    """
    Parses the Sudoku CSV dataset.
    Expected columns: id, puzzle, solution, clues, difficulty
    Returns a list of 9x9 grids (list of lists of ints).
    """
    puzzles = []
    
    if not os.path.exists(filepath):
        print(f"Warning: Sudoku file not found at {filepath}")
        return []

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        
        # skip header if it exists
        try:
            header = next(reader)
            # Heuristic: if the second column isn't a puzzle string (doesn't contain digits/dots), skip it
            if not any(c.isdigit() or c == '.' for c in header[1]):
                pass 
            else:
                # It wasn't a header, reset
                f.seek(0)
                reader = csv.reader(f)
        except StopIteration:
            return []

        count = 0
        for row in reader:
            if not row: continue
            if limit and count >= limit: break
            
            # Row format: [id, puzzle, solution, clues, difficulty]
            # We want row[1] -> the puzzle string
            puzzle_str = row[1]
            
            board = []
            for r in range(9):
                row_vals = []
                for c in range(9):
                    idx = r * 9 + c
                    char = puzzle_str[idx]
                    # Convert '.' to 0, otherwise int
                    val = 0 if char == '.' else int(char)
                    row_vals.append(val)
                board.append(row_vals)
            
            puzzles.append(board)
            count += 1
            
    return puzzles
