from collections import defaultdict
import networkx as nx


def calculate_positions(architecture):
    """
    Calculate node positions using Graphviz.
    
    Returns:
        {
            "node_id": {
                "x": float,
                "y": float
            }
        }
    """

    G = nx.DiGraph()

    # Add nodes
    for node in architecture["nodes"]:
        G.add_node(node["id"])

    # Add edges
    for edge in architecture["edges"]:
        G.add_edge(
            edge["source"],
            edge["target"]
        )

    try:
        from networkx.drawing.nx_agraph import graphviz_layout

        pos = graphviz_layout(
            G,
            prog="dot"
        )

    except Exception:
        # Fallback if graphviz unavailable
        pos = nx.spring_layout(
            G,
            seed=42
        )

    # Normalize coordinates
    positions = {}

    xs = [v[0] for v in pos.values()]
    ys = [v[1] for v in pos.values()]

    min_x = min(xs)
    min_y = min(ys)

    scale = 100.0

    for node_id, (x, y) in pos.items():

        positions[node_id] = {
            "x": ((x - min_x) / scale) + 1,
            "y": ((y - min_y) / scale) + 1
        }

    return positions
