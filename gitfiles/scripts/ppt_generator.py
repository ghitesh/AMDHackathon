from __future__ import annotations

from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.enum.shapes import (
    MSO_AUTO_SHAPE_TYPE,
    MSO_CONNECTOR,
)
from pptx.dml.color import RGBColor


class PowerPointRenderer:
    """
    Render DiagramModel into PowerPoint.

    Input coordinates must already be normalized
    into PowerPoint EMU space.
    """

    def __init__(
        self,
        prs: Presentation,
        icon_mapper=None,
    ):
        self.prs = prs
        self.icon_mapper = icon_mapper
        self.node_shapes = {}

    # =====================================================
    # Public API
    # =====================================================

    def render(self, diagram):

        slide = self.prs.slides.add_slide(
            self.prs.slide_layouts[6]
        )

        self._render_containers(
            slide,
            diagram,
        )

        self._render_nodes(
            slide,
            diagram,
        )

        self._render_edges(
            slide,
            diagram,
        )

        return slide

    # =====================================================
    # Containers
    # =====================================================

    def _render_containers(
        self,
        slide,
        diagram,
    ):

        for container in diagram.containers:

            bbox = container.bbox

            shape = slide.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                int(bbox.x),
                int(bbox.y),
                int(bbox.width),
                int(bbox.height),
            )

            shape.text = container.label

            shape.fill.background()

            shape.line.color.rgb = RGBColor(
                180,
                180,
                180,
            )

            shape.line.width = 12700

    # =====================================================
    # Nodes
    # =====================================================

    def _render_nodes(
        self,
        slide,
        diagram,
    ):

        for node in diagram.nodes:

            icon_path = self._resolve_icon(
                node.service
            )

            if icon_path:

                shape = slide.shapes.add_picture(
                    str(icon_path),
                    int(node.x),
                    int(node.y),
                    width=int(node.width),
                    height=int(node.height),
                )

            else:

                shape = slide.shapes.add_shape(
                    MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                    int(node.x),
                    int(node.y),
                    int(node.width),
                    int(node.height),
                )

            self.node_shapes[node.id] = shape

            self._render_node_label(
                slide,
                node,
            )

    def _resolve_icon(
        self,
        service: Optional[str],
    ):

        if (
            not service
            or not self.icon_mapper
        ):
            return None

        try:

            path = self.icon_mapper(
                service
            )

            if (
                path
                and Path(path).exists()
            ):
                return path

        except Exception:
            pass

        return None

    def _render_node_label(
        self,
        slide,
        node,
    ):

        label_height = 250000

        textbox = slide.shapes.add_textbox(
            int(node.x),
            int(node.y + node.height),
            int(max(node.width, 500000)),
            label_height,
        )

        textbox.text = node.label

    # =====================================================
    # Edges
    # =====================================================

    def _render_edges(
        self,
        slide,
        diagram,
    ):

        for edge in diagram.edges:

            points = getattr(
                edge,
                "points",
                None,
            )

            if not points:
                continue

            if len(points) < 2:
                continue

            for p1, p2 in zip(
                points,
                points[1:],
            ):

                try:

                    connector = (
                        slide.shapes.add_connector(
                            MSO_CONNECTOR.STRAIGHT,
                            int(p1.x),
                            int(p1.y),
                            int(p2.x),
                            int(p2.y),
                        )
                    )

                    connector.line.width = 12700

                except Exception as ex:

                    print(
                        f"Edge render failed "
                        f"{edge.source}->{edge.target}: "
                        f"{ex}"
                    )

    # =====================================================
    # Save helper
    # =====================================================

    def save(
        self,
        output_file,
    ):

        self.prs.save(
            str(output_file)
        )


# =========================================================
# Backwards Compatibility
# =========================================================

def build_ppt(
    prs: Presentation,
    icon_mapper=None,
):

    return PowerPointRenderer(
        prs,
        icon_mapper,
    )
