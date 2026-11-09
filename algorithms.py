"""
Search algorithms on an osmnx graph.

All functions need to follow the signature:
    algo(G, start, dest) -> (path, expanded)

path:     list of node IDs from start to goal
expanded: list of node IDs in the order they were expanded
"""

from collections import deque
import osmnx

START = (53.5572099, 10.0232364)
DEST = (53.5416732, 9.9839894)


def construct_path(parent, start, dest):
    path = []
    node = dest
    while node != start:
        path.append(node)
        node = parent[node]

    path.append(node)
    path.reverse()
    return path


def bfs(G, start, dest):
    q = deque([start])
    visited = {start}
    parent = {}
    expanded = []

    while q:
        node = q.popleft()
        expanded.append(node)

        if node == dest:
            return construct_path(parent, start, dest), expanded

        for neighbour in G.successors(node):
            if neighbour not in visited:
                visited.add(neighbour)
                q.append(neighbour)
                parent[neighbour] = node

    return None, expanded

if __name__ == "__main__":
    G = osmnx.load_graphml("data/hamburg.graphml")

    start = osmnx.distance.nearest_nodes(G, START[1], START[0])
    destination = osmnx.distance.nearest_nodes(G, DEST[1], DEST[0])

    path, expanded = bfs(G, start, destination)
