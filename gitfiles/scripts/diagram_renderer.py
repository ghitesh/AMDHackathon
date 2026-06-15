from PIL import Image
from PIL import ImageDraw


def render_png(
    architecture,
    positions,
    output_file
):
    img = Image.new(
        "RGB",
        (1600, 900),
        "white"
    )

    draw = ImageDraw.Draw(img)

    for edge in architecture["edges"]:

        s = positions[edge["source"]]
        t = positions[edge["target"]]

        draw.line(
            (
                s["x"] * 100,
                s["y"] * 100,
                t["x"] * 100,
                t["y"] * 100
            ),
            fill="black",
            width=3
        )

    img.save(output_file)
