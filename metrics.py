import time

import osmnx

from algorithms import DEST, START, bfs, bi_dir_bfs, dijkstra, a_stern

ALGORITHMS = [
    ("BFS", bfs),
    ("Bidirectional BFS", bi_dir_bfs),
    ("Dijkstra", dijkstra),
    ("A*", a_stern),
]

RUNS = 50


def path_length(G, path):
    total = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        # there can be several parallel edges from u to v, take the shortest
        shortest = float("inf")
        for edge in G[u][v].values():
            shortest = min(shortest, edge["length"])

        total += shortest
    return total


def measure(G, start, dest, algo):
    path, expanded = algo(G, start, dest)

    start_time = time.perf_counter()
    for _ in range(RUNS):
        algo(G, start, dest)
    ms = (time.perf_counter() - start_time) / RUNS * 1000

    return len(path) - 1, len(expanded), ms, path_length(G, path) / 1000


if __name__ == "__main__":
    G = osmnx.load_graphml("data/hamburg.graphml")
    start = osmnx.distance.nearest_nodes(G, START[1], START[0])
    dest = osmnx.distance.nearest_nodes(G, DEST[1], DEST[0])

    print("algorithm, edges, expanded, ms, km")
    for name, algo in ALGORITHMS:
        edges, expanded, ms, km = measure(G, start, dest, algo)
        print("%s %d %d %.2f %.2f" % (name, edges, expanded, ms, km))
