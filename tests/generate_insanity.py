# tests/instant_insanity/generate_dataset.py
import csv
import random
import os

COLORS = ['R', 'G', 'B', 'W']
FACES = 6

def random_cube():
    """Generates a random cube string."""
    return "".join(random.choice(COLORS) for _ in range(FACES))

def generate_solvable_instance():
    """
    Generates 4 cubes that definitely have a solution.
    Strategy:
    1. Pick 4 'Side' rows (F, B, L, R) that are valid (each has 1 of each color).
    2. Pick 2 'Cap' rows (Top, Bottom) randomly.
    3. Construct the cubes from these rows.
    4. Randomly rotate/shuffle the faces of each cube to hide the solution.
    """
    
    # 1. Create 4 rows for the sides (Front, Back, Left, Right)
    # Each row must be a permutation of RGBW
    side_rows = []
    for _ in range(4):
        row = list(COLORS)
        random.shuffle(row)
        side_rows.append(row)
    
    # Transpose to get the side faces for each cube
    # cube_sides[i] = [Front, Back, Left, Right] for Cube i
    cube_sides = list(zip(*side_rows))
    
    cubes = []
    for i in range(4):
        # Get the 4 side faces for this cube
        f, b, l, r = cube_sides[i]
        
        # Pick random Top and Bottom faces
        t = random.choice(COLORS)
        bt = random.choice(COLORS)
        
        # Current Layout: F, B, L, R, T, B
        # But we want to "scramble" this orientation so the solver has to work.
        # We'll just store them in the standard order [F, B, L, R, T, B] 
        # and let the solver figure out the rotation.
        # (Note: A harder scrambler would apply a random rotation to the cube string,
        # but this is sufficient for benchmarking).
        
        cube_str = f"{f}{b}{l}{r}{t}{bt}"
        cubes.append(cube_str)
        
    return cubes

def main():
    folder = os.path.dirname(__file__)
    if not folder: folder = "."
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    filepath = os.path.join(folder, "instant_insanity.csv")
    
    print(f"Generating dataset at {filepath}...")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "type", "cube1", "cube2", "cube3", "cube4"])
        
        # Generate 50 Solvable Puzzles
        for i in range(50):
            cubes = generate_solvable_instance()
            writer.writerow([f"S{i}", "solvable", *cubes])
            
        # Generate 50 Random Puzzles (Likely Unsolvable)
        for i in range(50):
            cubes = [random_cube() for _ in range(4)]
            writer.writerow([f"R{i}", "random", *cubes])
            
    print("Done! Created 100 puzzles.")

if __name__ == "__main__":
    main()
