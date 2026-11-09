import osmnx

CENTER = (53.5490, 10.0030)
DIST = 5000
OUT_FILE = "data/hamburg.graphml"

G = osmnx.graph.graph_from_point(center_point=CENTER, dist=DIST, network_type="drive")

osmnx.save_graphml(G, OUT_FILE)
