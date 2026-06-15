from graphviz import Digraph

from aws_architecture_schema import (
    Architecture,
    Container,
    Node
)


class GraphvizClusterGenerator:
    """
    Production-grade AWS container hierarchy builder.

    Creates Graphviz clusters for:

        Region
          └ VPC
               └ AZ
                    └ Subnet

    while preserving node ownership.
    """

    def __init__(self, architecture: Architecture):

        self.arch = architecture

        self.graph = Digraph(
            "AWS",
            graph_attr={
                "compound": "true",
                "newrank": "true",
                "splines": "ortho",
                "ranksep": "1.2",
                "nodesep": "0.8",
                "pad": "0.4"
            }
        )

        self.container_map = {
            c.id: c
            for c in architecture.containers
        }

        self.children = self._build_container_tree()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build(self) -> Digraph:

        roots = [
            c for c in self.arch.containers
            if c.parent_id is None
        ]

        for root in roots:
            self._render_container(root, self.graph)

        return self.graph

    # ---------------------------------------------------------
    # Tree Construction
    # ---------------------------------------------------------

    def _build_container_tree(self):

        tree = {}

        for c in self.arch.containers:
            tree[c.id] = []

        for c in self.arch.containers:

            if c.parent_id:
                tree[c.parent_id].append(c)

        return tree

    # ---------------------------------------------------------
    # Container Rendering
    # ---------------------------------------------------------

    def _render_container(
        self,
        container: Container,
        parent_graph
    ):

        cluster_name = f"cluster_{container.id}"

        with parent_graph.subgraph(name=cluster_name) as sub:

            self._apply_cluster_style(
                sub,
                container
            )

            self._add_container_label(
                sub,
                container
            )

            self._add_nodes(
                sub,
                container.id
            )

            for child in self.children.get(container.id, []):

                self._render_container(
                    child,
                    sub
                )

            self._add_alignment_guides(
                sub,
                container
            )

    # ---------------------------------------------------------
    # Node Placement
    # ---------------------------------------------------------

    def _add_nodes(
        self,
        graph,
        container_id
    ):

        nodes = [
            n for n in self.arch.nodes
            if n.container_id == container_id
        ]

        for node in nodes:

            graph.node(
                node.id,
                label=node.label,
                shape="box",
                width="1.0",
                height="1.0"
            )

    # ---------------------------------------------------------
    # AWS Styling
    # ---------------------------------------------------------

    def _apply_cluster_style(
        self,
        graph,
        container: Container
    ):

        styles = {

            "region": {
                "labeljust": "l",
                "style": "rounded",
                "color": "#6B7280",
                "penwidth": "2"
            },

            "vpc": {
                "style": "rounded",
                "color": "#3B82F6",
                "penwidth": "2"
            },

            "availability_zone": {
                "style": "rounded,dashed",
                "color": "#9CA3AF",
                "penwidth": "1.5"
            },

            "subnet": {
                "style": "filled,rounded",
                "fillcolor": "#F9FAFB",
                "color": "#D1D5DB"
            }
        }

        cfg = styles.get(container.type, {})

        graph.attr(**cfg)

    # ---------------------------------------------------------
    # Labels
    # ---------------------------------------------------------

    def _add_container_label(
        self,
        graph,
        container
    ):

        graph.attr(
            label=container.name,
            fontsize="18",
            fontname="Arial Bold"
        )

    # ---------------------------------------------------------
    # Alignment Rules
    # ---------------------------------------------------------

    def _add_alignment_guides(
        self,
        graph,
        container
    ):
        """
        AWS diagrams rely heavily on
        invisible alignment edges.

        Example:

            Public-AZ1 ---- Public-AZ2
            Private-AZ1 --- Private-AZ2
        """

        children = self.children.get(
            container.id,
            []
        )

        if len(children) < 2:
            return

        for left, right in zip(
            children[:-1],
            children[1:]
        ):

            graph.edge(
                f"anchor_{left.id}",
                f"anchor_{right.id}",
                style="invis",
                weight="100"
            )
