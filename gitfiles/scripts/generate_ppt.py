from __future__ import annotations

import argparse
import json

from pptx import Presentation

from architecture_schema import Architecture

from graphviz_layout_engine import GraphvizLayoutEngine
from coordinate_normalizer import (
    CoordinateNormalizer,
    NormalizationConfig,
)
from ppt_renderer import PowerPointRenderer


def generate_ppt(
    architecture: Architecture,
    output_file: str,
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


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Architecture JSON"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output PPTX"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    with open(args.input, "r", encoding="utf-8") as f:

        architecture = (
            Architecture.model_validate(
                json.load(f)
            )
        )

    generate_ppt(
        architecture=architecture,
        output_file=args.output,
    )

    print(
        f"PPT generated: {args.output}"
    )


if __name__ == "__main__":
    main()
