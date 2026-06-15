from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE


ICON_SIZE = 0.8


def build_ppt(
    architecture,
    positions,
    icon_mapper,
    output_file
):
    prs = Presentation()

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    node_shapes = {}

    # ------------------------------------------------
    # Draw containers first
    # ------------------------------------------------

    for container in architecture.get(
        "containers",
        []
    ):

        nodes = container["children"]

        xs = []
        ys = []

        for node_id in nodes:

            pos = positions[node_id]

            xs.append(pos["x"])
            ys.append(pos["y"])

        left = min(xs) - 0.5
        top = min(ys) - 0.5

        width = (
            max(xs) - min(xs)
        ) + 2.0

        height = (
            max(ys) - min(ys)
        ) + 2.0

        box = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(left),
            Inches(top),
            Inches(width),
            Inches(height)
        )

        box.text = container["name"]

    # ------------------------------------------------
    # Draw nodes
    # ------------------------------------------------

    for node in architecture["nodes"]:

        pos = positions[node["id"]]

        icon = icon_mapper(
            node["service"]
        )

        if icon:

            picture = slide.shapes.add_picture(
                str(icon),
                Inches(pos["x"]),
                Inches(pos["y"]),
                width=Inches(ICON_SIZE)
            )

            node_shapes[node["id"]] = picture

        textbox = slide.shapes.add_textbox(
            Inches(pos["x"] - 0.3),
            Inches(pos["y"] + 0.8),
            Inches(2),
            Inches(0.3)
        )

        textbox.text = node["label"]

    # ------------------------------------------------
    # Draw edges
    # ------------------------------------------------

for edge in architecture["edges"]:

    src = node_shapes.get(edge["source"])
    dst = node_shapes.get(edge["target"])

    if src is None or dst is None:
        print(f"Skipping edge {edge}")
        continue

    x1 = int(src.left + src.width / 2)
    y1 = int(src.top + src.height / 2)

    x2 = int(dst.left + dst.width / 2)
    y2 = int(dst.top + dst.height / 2)

    try:
        slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            x1,
            y1,
            x2,
            y2
        )
    except Exception as e:
        print(f"Failed edge {edge}: {e}")

    prs.save(output_file)
