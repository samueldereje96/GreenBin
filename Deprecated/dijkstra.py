import heapq

def dijkstra(grid, start, target):
    """
    grid: 2D list of chars, non-traversable cells are 'O', 'B', 'F', 'V'
    start, target: tuples (x, y)
    returns: list of (x, y) representing shortest path
    """
    rows, cols = len(grid), len(grid[0])
    visited = set()
    heap = [(0, start, [])]  # (distance, current_node, path)

    while heap:
        dist, (x, y), path = heapq.heappop(heap)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        path = path + [(x, y)]

        if (x, y) == target:
            return path  # shortest path found

        # Explore neighbors (up, down, left, right)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                # Allow entering the target cell even if it's marked as B/F/V
                is_target = (nx, ny) == target
                if (nx, ny) not in visited and (is_target or grid[nx][ny] not in ('O', 'B', 'F', 'V')):
                    heapq.heappush(heap, (dist + 1, (nx, ny), path))

    return []  # no path found
