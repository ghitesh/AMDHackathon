import json

from layout_engine import calculate_positions
from ppt_generator import build_ppt
from diagram_renderer import render_png
from aws_icon_mapper import get_icon


with open("architecture.json") as f:
    architecture = json.load(f)

positions = calculate_positions(
    architecture
)

render_png(
    architecture,
    positions,
    "outputs/architecture.png"
)

build_ppt(
    architecture,
    positions,
    lambda svc: get_icon(
        svc,
        "/workspace/shared/aws_icons"
    ),
    "outputs/final.pptx"
)
