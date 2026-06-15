from graphviz_layout_runner import (
    GraphvizLayoutRunner
)

from graphviz_xdot_parser import (
    GraphvizXDotParser
)

from coordinate_normalizer import (
    CoordinateNormalizer
)


class LayoutPipeline:

    def run(
        self,
        dot_source: str
    ):

        xdot = (
            GraphvizLayoutRunner()
            .generate_xdot(dot_source)
        )

        diagram = (
            GraphvizXDotParser()
            .parse(xdot)
        )

        diagram = (
            CoordinateNormalizer()
            .normalize(diagram)
        )

        return diagram
