"""
Style adapted from https://github.com/felipearosr/Shortest_Path (MIT License)
"""

import math
import itertools
import matplotlib.pyplot as plt
import numpy as np
import osmnx
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba

from algorithms import DEST, START, bfs

# animation settings
NODES_PER_FRAME = 20
PATH_EDGES_PER_FRAME = 2
HOLD_FRAMES = 40
FIGSIZE = (8, 8)

BG = "#0F1126"

# edge states
UNVISITED, VISITED, ACTIVE, PATH = 0, 1, 2, 3
# style of edges: (color, alpha, linewidth)
STYLE = {
    UNVISITED: ("#2432B0", 0.3, 0.5),
    VISITED: ("#2432B0", 1.0, 1.0),
    ACTIVE: ("#3F50E7", 1.0, 1.0),
    PATH: ("#FFFFFF", 1.0, 1.0),
}
RGBA = np.array([to_rgba(c, a) for c, a, _ in STYLE.values()])
LINEWIDTH = np.array([w for _, _, w in STYLE.values()])


def _edges_to_lines(G):
    # curved streets are a single edge in G, their shape is stored seperatly
    # gdfs gives us the shape of every edge
    edges = osmnx.graph_to_gdfs(G, nodes=False)
    lines = [np.asarray(geom.coords) for geom in edges.geometry]

    # edge (u, v, key) to its position in lines, used to color the route
    index = {edge: i for i, edge in enumerate(edges.index)}

    # node to positions of its outgoing edges, used to color expanded nodes
    out_edges = {n: [] for n in G.nodes}
    for (u, v, k), i in index.items():
        out_edges[u].append(i)
    return lines, index, out_edges


def animate_search(G, path, expanded):
    lines, index, out_edges = _edges_to_lines(G)
    state = np.full(len(lines), UNVISITED)

    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG)
    ax.set_axis_off()
    lc = LineCollection(lines, colors=RGBA[state], linewidths=LINEWIDTH[state])
    ax.add_collection(lc)

    start, dest = expanded[0], path[-1]
    ax.scatter(
        [G.nodes[start]["x"], G.nodes[dest]["x"]],
        [G.nodes[start]["y"], G.nodes[dest]["y"]],
        c="#FFFFFF",
        zorder=999,
    )
    fig.tight_layout()

    path_edges = []
    for u, v in itertools.pairwise(path):
        path_edges.append(index[(u, v, 0)])

    # number of frames of the search phase
    n_search = math.ceil(len(expanded) / NODES_PER_FRAME)
    # number of frames of the final path phase
    n_path = math.ceil(len(path_edges) / PATH_EDGES_PER_FRAME)
    done = set()

    def update(frame):
        # search phase
        if frame < n_search:
            # next batch of expanded nodes for this frame
            batch = expanded[frame * NODES_PER_FRAME : (frame + 1) * NODES_PER_FRAME]
            for node in batch:
                done.add(node)
                state[out_edges[node]] = VISITED
                for succ in G.successors(node):
                    # discovered but not expanded yet
                    if succ not in done:
                        state[out_edges[succ]] = ACTIVE
        # path phase
        elif frame < n_search + n_path:
            if frame == n_search:
                # clear map first
                state.fill(UNVISITED)
            path_frame = frame - n_search
            first = path_frame * PATH_EDGES_PER_FRAME
            batch = path_edges[first : first + PATH_EDGES_PER_FRAME]
            state[batch] = PATH
        lc.set_color(RGBA[state])
        lc.set_linewidth(LINEWIDTH[state])

    anim = FuncAnimation(
        fig, update, frames=n_search + n_path + HOLD_FRAMES, interval=50
    )
    plt.close(fig)
    return anim


if __name__ == "__main__":
    G = osmnx.load_graphml("data/hamburg.graphml")
    start = osmnx.distance.nearest_nodes(G, START[1], START[0])
    dest = osmnx.distance.nearest_nodes(G, DEST[1], DEST[0])

    path, expanded = bfs(G, start, dest)
    anim = animate_search(G, path, expanded)
    anim.save("bfs.gif", writer="pillow", fps=20)  # pillow for gif, ffmpeg for mp4
