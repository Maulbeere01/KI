import osmnx

G = osmnx.load_graphml("data/hamburg.graphml")

print("Type: ", type(G).__name__)
print("Nodes: ", len(G.nodes))
print("Edges: ", len(G.edges))

node_id, node_data = next(iter(G.nodes(data=True)))
print("\nnode:", node_id)
for name, value in node_data.items():
    print(f" {name}: {value}")

u, v, key, edge_data = next(iter(G.edges(keys=True, data=True)))
print(f"\nedge: {u} -> {v} (key={key})")
for name, value in edge_data.items():
    print(f" {name}: {str(value)[:80]}")
