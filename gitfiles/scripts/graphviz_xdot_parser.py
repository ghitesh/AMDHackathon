import re

from diagram_model import (
    DiagramModel,
    DiagramNode,
    DiagramEdge,
    DiagramContainer,
    BoundingBox,
    Point
)


class GraphvizXDotParser:
    """
    Parses Graphviz XDOT output.

    Extracts:

    - graph size
    - node positions
    - node sizes
    - edge splines
    - cluster bounding boxes
    """

    CLUSTER_RE = re.compile(
        r'cluster_(?P<id>[^ ]+)'
    )

    def parse(
        self,
        xdot_data: str
    ) -> DiagramModel:

        width = 0
        height = 0

        nodes = []
        edges = []
        containers = []

        graph_bbox = self._extract_graph_bbox(
            xdot_data
        )

        if graph_bbox:
            width = graph_bbox[2]
            height = graph_bbox[3]

        lines = xdot_data.splitlines()

        current_cluster = None

        for line in lines:

            line = line.strip()

            if "subgraph cluster_" in line:

                cluster = self._parse_cluster(
                    line
                )

                if cluster:
                    containers.append(cluster)

            elif "pos=" in line and "->" not in line:

                node = self._parse_node(line)

                if node:
                    nodes.append(node)

            elif "->" in line:

                edge = self._parse_edge(line)

                if edge:
                    edges.append(edge)

        return DiagramModel(
            width=width,
            height=height,
            nodes=nodes,
            edges=edges,
            containers=containers
        )

    # --------------------------------------------------
    # Graph
    # --------------------------------------------------

    def _extract_graph_bbox(
        self,
        xdot
    ):

        match = re.search(
            r'bb="([\d.]+),([\d.]+),([\d.]+),([\d.]+)"',
            xdot
        )

        if not match:
            return None

        x0, y0, x1, y1 = map(
            float,
            match.groups()
        )

        return (
            x0,
            y0,
            x1 - x0,
            y1 - y0
        )

    # --------------------------------------------------
    # Node
    # --------------------------------------------------

    def _parse_node(
        self,
        line
    ):

        try:

            node_id = line.split("[")[0].strip()

            pos_match = re.search(
                r'pos="([\d.]+),([\d.]+)"',
                line
            )

            width_match = re.search(
                r'width=([\d.]+)',
                line
            )

            height_match = re.search(
                r'height=([\d.]+)',
                line
            )

            label_match = re.search(
                r'label="([^"]+)"',
                line
            )

            if not pos_match:
                return None

            x, y = map(
                float,
                pos_match.groups()
            )

            width = (
                float(width_match.group(1))
                if width_match
                else 1
            )

            height = (
                float(height_match.group(1))
                if height_match
                else 1
            )

            label = (
                label_match.group(1)
                if label_match
                else node_id
            )

            return DiagramNode(
                id=node_id,
                label=label,
                x=x,
                y=y,
                width=width,
                height=height
            )

        except Exception:
            return None

    # --------------------------------------------------
    # Edge
    # --------------------------------------------------

    def _parse_edge(
        self,
        line
    ):

        try:

            source, rest = line.split(
                "->",
                1
            )

            target = rest.split("[")[0].strip()

            points = []

            pos_match = re.search(
                r'pos="([^"]+)"',
                line
            )

            if pos_match:

                points = self._parse_spline(
                    pos_match.group(1)
                )

            return DiagramEdge(
                source=source.strip(),
                target=target,
                points=points
            )

        except Exception:
            return None

    def _parse_spline(
        self,
        pos
    ):

        result = []

        pos = pos.replace("e,", "")
        pos = pos.replace("s,", "")

        coords = re.findall(
            r'([\d.]+),([\d.]+)',
            pos
        )

        for x, y in coords:

            result.append(
                Point(
                    float(x),
                    float(y)
                )
            )

        return result

    # --------------------------------------------------
    # Cluster
    # --------------------------------------------------

    def _parse_cluster(
        self,
        line
    ):

        cluster_match = self.CLUSTER_RE.search(
            line
        )

        if not cluster_match:
            return None

        cluster_id = cluster_match.group("id")

        bbox_match = re.search(
            r'bb="([\d.]+),([\d.]+),([\d.]+),([\d.]+)"',
            line
        )

        if not bbox_match:
            return None

        x0, y0, x1, y1 = map(
            float,
            bbox_match.groups()
        )

        return DiagramContainer(
            id=cluster_id,
            label=cluster_id,
            bbox=BoundingBox(
                x=x0,
                y=y0,
                width=x1 - x0,
                height=y1 - y0
            )
        )
