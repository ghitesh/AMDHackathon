from collections import defaultdict


LAYER_X_SPACING = 3.0
LAYER_Y_SPACING = 1.8


def calculate_positions(nodes):

    layers = defaultdict(list)

    for node in nodes:
        layer = node.get("layer", 0)
        layers[layer].append(node)

    positions = {}

    for layer, layer_nodes in layers.items():

        start_x = 1.0

        for idx, node in enumerate(layer_nodes):

            positions[node["id"]] = {
                "x": start_x + idx * LAYER_X_SPACING,
                "y": 1.0 + layer * LAYER_Y_SPACING
            }

    return positions
