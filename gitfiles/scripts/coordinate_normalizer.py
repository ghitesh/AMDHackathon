"""
coordinate_normalizer.py

Production-grade Graphviz → PowerPoint coordinate transformation.

Graphviz:
    Origin = bottom-left
    Units  = points (1/72 inch)

PowerPoint:
    Origin = top-left
    Units  = EMU

Responsibilities:

1. Flip Y axis
2. Normalize graph origin
3. Scale diagram into slide region
4. Apply margins
5. Preserve aspect ratio
6. Transform nodes, containers, labels, edges
"""

from __future__ import annotations

from dataclasses import replace
from typing import Optional

from diagram_model import (
    DiagramModel,
    DiagramNode,
    DiagramEdge,
    DiagramContainer,
    Point,
    BoundingBox,
)

# ---------------------------------------------------------
# PowerPoint constants
# ---------------------------------------------------------

EMU_PER_INCH = 914400
POINTS_PER_INCH = 72.0

EMU_PER_POINT = EMU_PER_INCH / POINTS_PER_INCH


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

class NormalizationConfig:

    def __init__(
        self,
        slide_width_emu: int,
        slide_height_emu: int,
        margin_left_emu: int = int(0.4 * EMU_PER_INCH),
        margin_right_emu: int = int(0.4 * EMU_PER_INCH),
        margin_top_emu: int = int(0.4 * EMU_PER_INCH),
        margin_bottom_emu: int = int(0.4 * EMU_PER_INCH),
        preserve_aspect_ratio: bool = True,
    ):
        self.slide_width_emu = slide_width_emu
        self.slide_height_emu = slide_height_emu

        self.margin_left_emu = margin_left_emu
        self.margin_right_emu = margin_right_emu
        self.margin_top_emu = margin_top_emu
        self.margin_bottom_emu = margin_bottom_emu

        self.preserve_aspect_ratio = preserve_aspect_ratio


# ---------------------------------------------------------
# Normalizer
# ---------------------------------------------------------

class CoordinateNormalizer:

    """
    Converts Graphviz coordinates into
    PowerPoint slide coordinates.
    """

    def __init__(
        self,
        config: NormalizationConfig,
    ):
        self.config = config

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def normalize(
        self,
        diagram: DiagramModel,
    ) -> DiagramModel:

        graph_width_pts = diagram.width
        graph_height_pts = diagram.height

        if graph_width_pts <= 0:
            raise ValueError("Invalid graph width")

        if graph_height_pts <= 0:
            raise ValueError("Invalid graph height")

        usable_width = (
            self.config.slide_width_emu
            - self.config.margin_left_emu
            - self.config.margin_right_emu
        )

        usable_height = (
            self.config.slide_height_emu
            - self.config.margin_top_emu
            - self.config.margin_bottom_emu
        )

        graph_width_emu = graph_width_pts * EMU_PER_POINT
        graph_height_emu = graph_height_pts * EMU_PER_POINT

        scale_x = usable_width / graph_width_emu
        scale_y = usable_height / graph_height_emu

        if self.config.preserve_aspect_ratio:
            scale = min(scale_x, scale_y)
            scale_x = scale
            scale_y = scale

        offset_x = self.config.margin_left_emu
        offset_y = self.config.margin_top_emu

        self._normalize_nodes(
            diagram,
            graph_height_pts,
            scale_x,
            scale_y,
            offset_x,
            offset_y,
        )

        self._normalize_edges(
            diagram,
            graph_height_pts,
            scale_x,
            scale_y,
            offset_x,
            offset_y,
        )

        self._normalize_containers(
            diagram,
            graph_height_pts,
            scale_x,
            scale_y,
            offset_x,
            offset_y,
        )

        return diagram

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    def _normalize_nodes(
        self,
        diagram,
        graph_height_pts,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
    ):

        for node in diagram.nodes:

            node.x = self._x_transform(
                node.x,
                scale_x,
                offset_x,
            )

            node.y = self._y_transform(
                node.y,
                graph_height_pts,
                scale_y,
                offset_y,
            )

            node.width = (
                node.width
                * EMU_PER_INCH
                * scale_x
            )

            node.height = (
                node.height
                * EMU_PER_INCH
                * scale_y
            )

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

    def _normalize_edges(
        self,
        diagram,
        graph_height_pts,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
    ):

        for edge in diagram.edges:

            transformed = []

            for point in edge.points:

                transformed.append(
                    Point(
                        x=self._x_transform(
                            point.x,
                            scale_x,
                            offset_x,
                        ),
                        y=self._y_transform(
                            point.y,
                            graph_height_pts,
                            scale_y,
                            offset_y,
                        ),
                    )
                )

            edge.points = transformed

    # -----------------------------------------------------
    # Containers
    # -----------------------------------------------------

    def _normalize_containers(
        self,
        diagram,
        graph_height_pts,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
    ):

        for container in diagram.containers:

            bbox = container.bbox

            new_x = self._x_transform(
                bbox.x,
                scale_x,
                offset_x,
            )

            new_y = self._y_transform(
                bbox.y + bbox.height,
                graph_height_pts,
                scale_y,
                offset_y,
            )

            new_width = (
                bbox.width
                * EMU_PER_POINT
                * scale_x
            )

            new_height = (
                bbox.height
                * EMU_PER_POINT
                * scale_y
            )

            container.bbox = BoundingBox(
                x=new_x,
                y=new_y,
                width=new_width,
                height=new_height,
            )

    # -----------------------------------------------------
    # Coordinate transforms
    # -----------------------------------------------------

    def _x_transform(
        self,
        x_pts,
        scale,
        offset,
    ):

        return (
            x_pts
            * EMU_PER_POINT
            * scale
            + offset
        )

    def _y_transform(
        self,
        y_pts,
        graph_height_pts,
        scale,
        offset,
    ):

        flipped = graph_height_pts - y_pts

        return (
            flipped
            * EMU_PER_POINT
            * scale
            + offset
        )
