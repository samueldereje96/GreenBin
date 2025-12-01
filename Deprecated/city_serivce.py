import sys
import os

# make file path robust relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "bins.json")

import json

def load_json(file_path):
    """Load JSON data from file."""
    with open(file_path, "r") as f:
        return json.load(f)

def create_city_grid(grid_size=13,
                     blocked_file=None,
                     facilities_file=None,
                     bins_file=None,
                     vehicles_file=None):
    """Create a 13x13 grid with obstacles, facilities, bins, and vehicles."""
    
    # Use absolute paths if not provided
    if blocked_file is None: blocked_file = os.path.join(PROJECT_ROOT, "data", "blocked.json")
    if facilities_file is None: facilities_file = os.path.join(PROJECT_ROOT, "data", "facilities.json")
    if bins_file is None: bins_file = os.path.join(PROJECT_ROOT, "data", "bins.json")
    if vehicles_file is None: vehicles_file = os.path.join(PROJECT_ROOT, "data", "vehicles.json")

    # 1️⃣ Initialize empty grid
    grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]
    
    # 2️⃣ Mark blocked cells
    if os.path.exists(blocked_file):
        blocked_data = load_json(blocked_file)
        for cell in blocked_data:
            x, y = cell["x"], cell["y"]
            grid[y][x] = "O"  # O = obstacle
    
    # 3️⃣ Mark facilities
    if os.path.exists(facilities_file):
        facilities = load_json(facilities_file)
        for f in facilities:
            x, y = f["x"], f["y"]
            grid[y][x] = "F"
    
    # 4️⃣ Mark bins
    if os.path.exists(bins_file):
        bins = load_json(bins_file)
        for b in bins:
            x, y = int(b["x"]), int(b["y"])
            grid[y][x] = "B"
    
    # 5️⃣ Mark vehicles
    if os.path.exists(vehicles_file):
        vehicles = load_json(vehicles_file)
        for v in vehicles:
            x, y = int(v["x"]), int(v["y"])
            grid[y][x] = "V"
    
    return grid

def print_grid(grid):
    """Simple function to display the grid in the console."""
    for row in grid:
        print(" ".join(row))

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    city_grid = create_city_grid()
    print_grid(city_grid)
