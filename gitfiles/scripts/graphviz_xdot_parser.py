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
    Parses Graphviz DOT/XDOT output.

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

        statements = self._build_statements(
            xdot_data
        )

        for stmt in statements:

            stmt = stmt.strip()

            if not stmt:
                continue

            if "subgraph cluster_" in stmt:

                cluster = self._parse_cluster(
                    stmt
                )

                if cluster:
                    containers.append(cluster)

            elif "->" in stmt:

                edge = self._parse_edge(
                    stmt
                )

                if edge:
                    edges.append(edge)

            elif "[" in stmt and "pos=" in stmt:

                node = self._parse_node(
                    stmt
                )

                if node:
                    nodes.append(node)

        # print(    "CONTAINERS:",    len(containers) )
        return DiagramModel(
            width=width,
            height=height,
            nodes=nodes,
            edges=edges,
            containers=containers
        )

    # --------------------------------------------------
    # Statement Builder
    # --------------------------------------------------

    def _build_statements(
        self,
        xdot_data: str
    ):

        statements = []

        current = []

        for raw_line in xdot_data.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            current.append(line)

            if (
                line.endswith("];")
                or line == "}"
            ):
                statements.append(
                    " ".join(current)
                )
                current = []

        if current:
            statements.append(
                " ".join(current)
            )

        return statements

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
        stmt
    ):

        try:

            #node_id = stmt.split("[")[0].strip()

            node_id = stmt.split("[")[0].strip()
            
            # Ignore malformed rank-group statements
            if ";" in node_id:
                return None
            
            # Ignore invisible layer anchors
            if node_id.startswith("layer_"):
                return None
            
            # Ignore alignment helpers
            if node_id.startswith("align_"):
                return None
    
            if (
                not node_id
                or node_id.startswith("align_")
            ):
                return None

            pos_match = re.search(
                r'pos="([\d.]+),([\d.]+)"',
                stmt
            )

            if not pos_match:
                return None

            width_match = re.search(
                r'width=([\d.]+)',
                stmt
            )

            height_match = re.search(
                r'height=([\d.]+)',
                stmt
            )

            label_match = re.search(
                r'label="([^"]+)"',
                stmt
            )

            if not label_match:
                label_match = re.search(
                    r'label=([^,\]]+)',
                    stmt
                )

            x, y = map(
                float,
                pos_match.groups()
            )

            width = (
                float(width_match.group(1))
                if width_match
                else 1.0
            )

            height = (
                float(height_match.group(1))
                if height_match
                else 1.0
            )

            label = (
                label_match.group(1).strip()
                if label_match
                else node_id
            )

            print(
                f"PARSED NODE: "
                f"id={node_id}, "
                f"label={label}, "
                f"x={x}, y={y}"
            )

            return DiagramNode(
                id=node_id,
                label=label,
                x=x,
                y=y,
                width=width,
                height=height
            )

        except Exception as ex:

            print(
                f"Failed parsing node: {ex}"
            )

            return None

    # --------------------------------------------------
    # Edge
    # --------------------------------------------------

    def _parse_edge(
        self,
        stmt
    ):

        try:

            source, rest = stmt.split(
                "->",
                1
            )

            target = (
                rest.split("[")[0]
                .strip()
            )

            points = []

            pos_match = re.search(
                r'pos="([^"]+)"',
                stmt
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

        pos = pos.replace(
            "e,",
            ""
        )

        pos = pos.replace(
            "s,",
            ""
        )

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
        stmt
    ):

        cluster_match = self.CLUSTER_RE.search(
            stmt
        )

        if not cluster_match:
            return None

        cluster_id = cluster_match.group(
            "id"
        )

        bbox_match = re.search(
            r'bb="([\d.]+),([\d.]+),([\d.]+),([\d.]+)"',
            stmt
        )

        if not bbox_match:
            return None

        x0, y0, x1, y1 = map(
            float,
            bbox_match.groups()
        )

        print( "CLUSTER FOUND:", cluster_id )

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