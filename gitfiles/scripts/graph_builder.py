"""
graph_builder.py

Architecture JSON
    ->
Layout Graph

Responsibilities:
- validate architecture
- build adjacency maps
- resolve containers
- assign layers
- detect disconnected components
- prepare Graphviz input
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set

from architecture_schema import (
    Architecture,
    Node,
    Edge,
    Container,
)


class LayoutGraph:
    """
    Internal graph representation.

    Independent of Graphviz.
    """

    def __init__(self):

        self.nodes: Dict[str, Node] = {}

        self.edges: List[Edge] = []

        self.containers: Dict[str, Container] = {}

        self.adjacency = defaultdict(set)

        self.reverse_adjacency = defaultdict(set)

        self.layers: Dict[str, int] = {}

        self.roots: Set[str] = set()


class GraphBuilder:

    def build(
        self,
        architecture: Architecture,
    ) -> LayoutGraph:

        graph = LayoutGraph()

        self._load_nodes(
            graph,
            architecture.nodes
        )

        self._load_edges(
            graph,
            architecture.edges
        )

        self._load_containers(
            graph,
            architecture.containers
        )

        self._validate(graph)

        self._compute_roots(graph)

        self._assign_layers(graph)

        return graph

    # -------------------------------------------------

    def _load_nodes(
        self,
        graph,
        nodes
    ):

        for node in nodes:
            graph.nodes[node.id] = node

    def _load_edges(
        self,
        graph,
        edges
    ):

        graph.edges.extend(edges)

        for edge in edges:

            graph.adjacency[
                edge.source
            ].add(edge.target)

            graph.reverse_adjacency[
                edge.target
            ].add(edge.source)

    def _load_containers(
        self,
        graph,
        containers
    ):

        for c in containers:
            graph.containers[c.id] = c

    # -------------------------------------------------

    def _validate(self, graph):

        for edge in graph.edges:

            if edge.source not in graph.nodes:
                raise ValueError(
                    f"Unknown source {edge.source}"
                )

            if edge.target not in graph.nodes:
                raise ValueError(
                    f"Unknown target {edge.target}"
                )

    # -------------------------------------------------

    def _compute_roots(self, graph):

        for node_id in graph.nodes:

            if not graph.reverse_adjacency[node_id]:
                graph.roots.add(node_id)

    # -------------------------------------------------

    def _assign_layers(self, graph):

        visited = set()

        queue = []

        for root in graph.roots:

            graph.layers[root] = 0

            queue.append(root)

        while queue:

            current = queue.pop(0)

            visited.add(current)

            current_layer = graph.layers[current]

            for child in graph.adjacency[current]:

                graph.layers[child] = max(
                    graph.layers.get(child, 0),
                    current_layer + 1
                )

                if child not in visited:
                    queue.append(child)
