import csv
import os

def parse_battleship_csv(filepath, limit=None):
    """
    Parses the Battleship CSV dataset.
    Expected columns: id, type, rows, cols, fleet, board
    
    Returns a list of tuples: (board_grid, fleet_list)
    where board_grid is a list of strings (rows) and fleet_list is a list of integers.
    """
    puzzles = []
    
    if not os.path.exists(filepath):
        print(f"Warning: Battleship file not found at {filepath}")
        return []

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        
        try:
            header = next(reader)
            # Basic validation to ensure we have the right file format
            if not header or 'fleet' not in header:
                f.seek(0)
                reader = csv.reader(f)
        except StopIteration:
            return []

        count = 0
        for row in reader:
            if not row: continue
            if limit and count >= limit: break
            
            # Row structure: id, type, rows, cols, fleet, board
            # Example Fleet: "5,4,3,3,2"
            fleet_str = row[4]
            fleet = [int(x) for x in fleet_str.replace('"', '').split(',') if x.strip()]
            
            # Example Board: "..??..|..?X.."
            board_str = row[5]
            # Split into rows
            board_rows = board_str.split('|')
            # Convert strings into list of characters for mutability if needed later, 
            # though the benchmark fixture handles conversion to constants.
            grid = [list(r) for r in board_rows]
            
            puzzles.append((grid, fleet))
            count += 1
            
    return puzzles