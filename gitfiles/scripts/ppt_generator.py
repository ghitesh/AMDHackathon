from pptx import Presentation
from pptx.util import Inches


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

    for node in architecture["nodes"]:

        pos = positions[node["id"]]

        icon = icon_mapper(
            node["service"]
        )

        if icon:
            slide.shapes.add_picture(
                str(icon),
                Inches(pos["x"]),
                Inches(pos["y"]),
                width=Inches(0.8)
            )

        slide.shapes.add_textbox(
            Inches(pos["x"]),
            Inches(pos["y"] + 0.8),
            Inches(1.5),
            Inches(0.3)
        ).text = node["label"]

    prs.save(output_file)
