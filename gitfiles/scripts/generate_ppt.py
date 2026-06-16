from graphviz_layout_engine import GraphvizLayoutEngine
from coordinate_normalizer import (
    CoordinateNormalizer,
    NormalizationConfig,
)
from ppt_renderer import PowerPointRenderer

from pptx import Presentation


def generate_ppt(
    architecture,
    output_file,
):
    prs = Presentation()

    layout_engine = GraphvizLayoutEngine()

    diagram = layout_engine.layout(
        architecture
    )

    normalizer = CoordinateNormalizer(
        NormalizationConfig(
            slide_width_emu=prs.slide_width,
            slide_height_emu=prs.slide_height,
        )
    )

    diagram = normalizer.normalize(
        diagram
    )

    renderer = PowerPointRenderer(
        prs
    )

    renderer.render(
        diagram
    )

    prs.save(output_file)
