"""
Search algorithms on an osmnx graph.

All functions need to follow the signature:
    algo(G, start, dest) -> (path, expanded)

path:     list of node IDs from start to goal
expanded: list of node IDs in the order they were expanded
"""

from collections import deque
import osmnx
import heapq

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

def dijkstra(G, start, dest):
    # Init
    dist = {start: 0.0} # Dict: Zuordnung von erreichten Knoten und bisher bekannte günstigste Kosten vom Start zu jedem erreichten Knoten (Start->Start = 0)
    parent = {} # Dict: Zuordnung von Knoten zu seinem parent
    expanded = [] # Liste: expandierte Knoten
    heap = [(0.0, start)] # prio queue (Min-Heap) mit (Kosten vom Start, Knoten)

    while heap: # solange queue noch Knoten beinhaltet
        cost, node = heapq.heappop(heap) # Knoten mit den kleinsten Kosten entnehmen (= höchste Priorität) 

        # es ist bereits ein günstigerer Weg zu diesem Knoten bekannt -> skip
        if cost > dist.get(node, float("inf")): # holt Kosten vom Start für Knoten, falls nicht vorhanden - default inf
            continue

        expanded.append(node) # Knoten als expandiert markieren

        # falls Ziel erreicht
        if node == dest:
            return construct_path(parent, start, dest), expanded # Weg rekonstruieren & zsm mit Expansionsreihenfolge zurückgeben

        # ausgehende Kanten des aktuellen Knoten durchlaufen
        for neighbour in G.successors(node):
            weight = min(edge["length"] for edge in G[node][neighbour].values()) # kürzeste der parallelen Kanten nehmen
            new_cost = cost + weight # vorläufige Kosten zum Nachbarn über den aktuellen Knoten

            # falls neuer Weg kürzer als bisher bekannter Weg
            if new_cost < dist.get(neighbour, float("inf")):
                dist[neighbour] = new_cost # für den Nachbarknoten die günstigsten Kosten vom Start speichern
                parent[neighbour] = node # aktueller Knoten als parent des Nachbarn merken
                heapq.heappush(heap, (new_cost, neighbour)) # für Nachbarn wurde günstigerer Weg gefunden -> mit neuem Wert in queue/heap legen

    return None, expanded # kein Weg gefunden -> Expansionsreihenfolge zurückgeben

def a_stern(G, start, dest):
    # Koordinaten des Ziel-Knotens für die Heuristik (y = Breite, x = Länge)
    dest_lat = G.nodes[dest]["y"]
    dest_lon = G.nodes[dest]["x"]

    # Heuristik: Luftlinie zum Ziel in Metern
    # great_circle(lat, lon, lat, lon) -> Meter
    def h(node):
        return osmnx.distance.great_circle(
            G.nodes[node]["y"], G.nodes[node]["x"], dest_lat, dest_lon
        )

    # Init
    dist = {start: 0.0} # Dict: Zuordnung von erreichten Knoten und bisher bekannte günstigste Kosten vom Start zu jedem erreichten Knoten (Start->Start = 0) - g-Werte: bisher günstigste Kosten
    parent = {} # Dict: Zuordnung von Knoten zu seinem parent
    expanded = [] # Liste: expandierte Knoten
    heap = [(h(start), 0.0, start)] # prio queue (Min-Heap) mit (Kosten/Prio: f = g + h, bisherige Kosten vom Start = g, Knoten)

    while heap: # solange queue noch Knoten beinhaltet
        _f, cost, node = heapq.heappop(heap) # Knoten mit den kleinsten Gesamtkosten (kleinstes f) entnehmen (= höchste Priorität)
        # heappop gibt immer das kleinste Tupel zurück, Tupel werden von links verglichen (zuerst f, bei Gleichstand g, dann node) -> deshalb kommt der Knoten mit dem kleinsten f zuerst raus 

        # es ist bereits ein günstigerer Weg zu diesem Knoten bekannt (laut cost bzw. g, nicht Gesamtkosten f) -> skip
        if cost > dist.get(node, float("inf")):  # holt Kosten vom Start für Knoten, falls nicht vorhanden - default inf
            continue

        expanded.append(node) # Knoten als expandiert markieren

        # falls Ziel erreicht
        if node == dest:
            return construct_path(parent, start, dest), expanded # Weg rekonstruieren & zsm mit Expansionsreihenfolge zurückgeben

        # ausgehende Kanten des aktuellen Knoten durchlaufen
        for neighbour in G.successors(node):
            weight = min(edge["length"] for edge in G[node][neighbour].values()) # kürzeste der parallelen Kanten nehmen
            new_cost = cost + weight # vorläufige Kosten zum Nachbarn über den aktuellen Knoten

            # falls neuer Weg kürzer als bisher bekannter Weg
            if new_cost < dist.get(neighbour, float("inf")):
                dist[neighbour] = new_cost # für den Nachbarknoten die günstigsten Kosten vom Start speichern
                parent[neighbour] = node # aktueller Knoten als parent des Nachbarn merken
                heapq.heappush(heap, (new_cost + h(neighbour), new_cost, neighbour)) # für Nachbarn wurde günstigerer Weg gefunden -> mit neuem Wert in queue/heap legen

    return None, expanded # kein Weg gefunden -> Expansionsreihenfolge zurückgeben