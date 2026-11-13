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

def bi_dir_bfs(G, start, dest):
    q_start = deque([start])
    q_dest = deque([dest])
    visited_start = {start}
    visited_dest = {dest}
    parent_start  = {}
    parent_dest = {}
    expanded = []

    while q_start and q_dest:
        hit = expand_level(G.successors, q_start, parent_start, visited_start, visited_dest, expanded)
        if hit is None:
            hit = expand_level(G.predecessors, q_dest, parent_dest, visited_dest, visited_start, expanded)
        if hit is not None:
            first = construct_path(parent_start, start, hit)
            second = construct_path(parent_dest, dest, hit)
            second.reverse()
            return first + second[1:], expanded
    return None, expanded
            
def expand_level(neighbours, q, parent, visited_own, visited_other, expanded):
    level_size = len(q)
    for _ in range(level_size):
        node = q.popleft()
        expanded.append(node)

        for n in neighbours(node):
            if n in visited_other:
                parent[n] = node
                return n
            if n not in visited_own:
                visited_own.add(n)
                q.append(n)
                parent[n] = node
    return None

