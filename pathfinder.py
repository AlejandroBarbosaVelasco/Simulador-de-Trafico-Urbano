# pathfinder.py
import heapq

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def neighbors(node, grid_size):
    r, c = node
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        nr, nc = r+dr, c+dc
        if 0 <= nr < grid_size and 0 <= nc < grid_size:
            yield (nr, nc)

def astar(start, goal, grid_size):
    """
    A* on a uniform grid (cost = 1 per step). Returns list of nodes from start to goal inclusive.
    If no path, returns empty list.
    """
    open_heap = []
    heapq.heappush(open_heap, (manhattan(start, goal), 0, start, None))
    came_from = {}
    gscore = {start: 0}
    closed = set()

    while open_heap:
        f, g, current, parent = heapq.heappop(open_heap)
        if current in closed:
            continue
        came_from[current] = parent

        if current == goal:
            # reconstruct
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        closed.add(current)

        for nb in neighbors(current, grid_size):
            tentative_g = g + 1
            if nb in gscore and tentative_g >= gscore[nb]:
                continue
            gscore[nb] = tentative_g
            fscore = tentative_g + manhattan(nb, goal)
            heapq.heappush(open_heap, (fscore, tentative_g, nb, current))

    return []
