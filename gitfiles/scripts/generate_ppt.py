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
from aws_icon_registry import AwsIconRegistry
from ppt_generator import PowerPointRenderer


def generate_ppt(
    architecture: Architecture,
    output_file: str,
):

    prs = Presentation()

    layout_engine = GraphvizLayoutEngine()

    
    # layout_engine.export_dot(
    #     architecture,
    #     "debug.dot"
    # )

    diagram = layout_engine.layout(
        architecture
    )

    print("\n=== DIAGRAM NODES ===")
    
    for n in diagram.nodes:
        print(
            n.id,
            n.x,
            n.y,
            n.width,
            n.height
        )
    
    print("\n=== DIAGRAM CONTAINERS ===")
    
    for c in diagram.containers:
        print(
            c.id,
            c.bbox.x,
            c.bbox.y,
            c.bbox.width,
            c.bbox.height
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

    print("\n=== DIAGRAM NODES AFTER===")
    
    for n in diagram.nodes:
        print(
            n.id,
            n.x,
            n.y,
            n.width,
            n.height
        )
    
    print("\n=== DIAGRAM CONTAINERS AFTER ===")
    
    for c in diagram.containers:
        print(
            c.id,
            c.bbox.x,
            c.bbox.y,
            c.bbox.width,
            c.bbox.height
        )
    
    icon_registry = AwsIconRegistry(
        catalog_path = "aws_icon_catalog.json",
        #icon_root = "/workspace/shared/aws_icons"
        icon_root = r"C:\\Users\\ghitesh\\Downloads\\Icon-package"
    )

    renderer = PowerPointRenderer(
        prs,
        icon_registry
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
