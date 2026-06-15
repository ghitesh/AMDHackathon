def calculate_positions(nodes):
    positions = {}

    x = 1.0

    for node in nodes:
        positions[node["id"]] = {
            "x": x,
            "y": 2
        }

        x += 2.5

    return positions
