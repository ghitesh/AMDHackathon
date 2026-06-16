"""
graphviz_cluster_generator.py

Production-grade AWS Graphviz cluster generator.

Responsibilities:
- Build nested Graphviz clusters
- Render AWS hierarchy
- Enforce AZ balancing
- Apply AWS styles
- Generate invisible alignment edges
- Generate node definitions
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from graphviz import Digraph

from graph_builder import LayoutGraph


# ==========================================================
# AWS Styles
# ==========================================================

CONTAINER_STYLES = {
    "region": {
        "style": "rounded",
        "color": "#6B7280",
        "penwidth": "2",
    },
    "vpc": {
        "style": "rounded",
        "color": "#2563EB",
        "penwidth": "2",
    },
    "availability_zone": {
        "style": "rounded,dashed",
        "color": "#9CA3AF",
        "penwidth": "1.5",
    },
    "subnet": {
        "style": "rounded,filled",
        "fillcolor": "#F8FAFC",
        "color": "#CBD5E1",
        "penwidth": "1",
    },
}


class GraphvizClusterGenerator:
    """
    Generates AWS hierarchy clusters.
    """

    def __init__(self, graph: LayoutGraph):

        self.graph_data = graph

        self.dot = Digraph(
            "AWS",
            graph_attr={
                "compound": "true",
                "newrank": "true",
                "splines": "ortho",
                "rankdir": "TB",
                "nodesep": "0.8",
                "ranksep": "1.2",
                "pad": "0.4",
            },
        )

        #self.graph_data.container_children
        self.children = self._build_container_tree()

    # ======================================================
    # Public API
    # ======================================================

    def build(self) -> Digraph:

        self._configure_graph()

        roots = [
            c
            for c in self.graph_data.containers.values()
            if c.parent_id is None
        ]

        for container in roots:
            self._render_container(
                container,
                self.dot,
            )

        self._render_orphan_nodes()

        self._render_rank_groups()

        self._render_edges()

        self._create_layer_structure()

        return self.dot

    # ======================================================
    # Graph Config
    # ======================================================

    def _configure_graph(self):

        self.dot.attr(
            "node",
            shape="box",
            width="1.0",
            height="1.0",
            fixedsize="false",
            fontsize="10",
        )

        self.dot.attr(
            "edge",
            arrowsize="0.8",
            penwidth="1.2",
        )

    # ======================================================
    # Container Tree
    # ======================================================

    def _build_container_tree_deletethis(self):

        tree = defaultdict(list)

        for container in self.graph_data.containers.values():

            if container.parent_id:
                tree[container.parent_id].append(container)

        return tree

    # ======================================================
    # Containers
    # ======================================================

    def _render_container(
        self,
        container,
        parent_graph,
    ):

        cluster_name = f"cluster_{container.id}"

        with parent_graph.subgraph(
            name=cluster_name
        ) as sub:

            self._apply_style(
                sub,
                container.type,
            )

            sub.attr(
                label=container.name,
                fontsize="16",
                fontname="Arial",
            )

            self._render_nodes(
                sub,
                container.id,
            )

            for child in self.children.get(
                container.id,
                [],
            ):
                self._render_container(
                    child,
                    sub,
                )

            self._align_children(
                sub,
                container.id,
            )

    # ======================================================
    # Nodes
    # ======================================================
    def _render_nodes(
        self,
        graph,
        container_id,
    ):
    
        node_ids = self.graph_data.container_nodes.get(
            container_id,
            []
        )
    
        for node_id in node_ids:
    
            node = self.graph_data.nodes[node_id]
    
            graph.node(
                node.id,
                label=node.label,
            )
        

    def _render_orphan_nodes(self):

        for node in self.graph_data.nodes.values():

            if node.container_id:
                continue

            self.dot.node(
                node.id,
                label=node.label,
            )

    # ======================================================
    # Styling
    # ======================================================

    def _apply_style(
        self,
        graph,
        container_type,
    ):

        graph.attr(
            **CONTAINER_STYLES.get(
                container_type,
                {}
            )
        )

    # ======================================================
    # Alignment
    # ======================================================

    def _align_children(
        self,
        graph,
        container_id,
    ):

        children = self.children.get(
            container_id,
            [],
        )

        if len(children) < 2:
            return

        for left, right in zip(
            children[:-1],
            children[1:]
        ):

            anchor_a = f"align_{left.id}"
            anchor_b = f"align_{right.id}"

            graph.node(
                anchor_a,
                style="invis",
                width="0",
                height="0",
            )

            graph.node(
                anchor_b,
                style="invis",
                width="0",
                height="0",
            )

            graph.edge(
                anchor_a,
                anchor_b,
                style="invis",
                weight="100",
            )

    # ======================================================
    # Layer Ranks
    # ======================================================

    def _create_layer_ranks_deletethis(self):

        grouped = defaultdict(list)

        for node_id, layer in self.graph_data.layers.items():
            grouped[layer].append(node_id)

        for nodes in grouped.values():

            with self.dot.subgraph() as rank:

                rank.attr(rank="same")

                for node_id in nodes:
                    rank.node(node_id)

    # ======================================================
    # Edges
    # ======================================================

    def _render_edges(self):

        for edge in self.graph_data.edges:

            self.dot.edge(
                edge.source,
                edge.target,
            )


    def _render_rank_groups(self):
    
        for service, node_ids in (
            self.graph_data.rank_groups.items()
        ):
    
            if len(node_ids) < 2:
                continue
    
            with self.dot.subgraph() as rank:
    
                rank.attr(rank="same")
    
                for node_id in node_ids:
                    rank.node(node_id)

    def _create_layer_structure(self):
    
        grouped = defaultdict(list)
    
        for node_id, layer in (
            self.graph_data.layers.items()
        ):
            grouped[layer].append(node_id)
    
        previous_anchor = None
    
        for layer in sorted(grouped):
    
            anchor = f"layer_{layer}"
    
            self.dot.node(
                anchor,
                shape="point",
                width="0",
                height="0",
                style="invis",
            )
    
            with self.dot.subgraph() as rank:
    
                rank.attr(rank="same")
    
                rank.node(anchor)
    
                for node_id in grouped[layer]:
                    rank.node(node_id)
    
            if previous_anchor:
    
                self.dot.edge(
                    previous_anchor,
                    anchor,
                    style="invis",
                    weight="100",
                )
    
            previous_anchor = anchor
        