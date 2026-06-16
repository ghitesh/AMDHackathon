from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Set

from architecture_schema import (
    Architecture,
    Node,
    Edge,
    Container,
)


AWS_LAYER_MAP = {
    "Route53": 0,
    "CloudFront": 0,
    "WAF": 0,
    "ALB": 1,
    "NLB": 1,
    "API Gateway": 1,
    "EC2": 2,
    "ECS": 2,
    "EKS": 2,
    "Lambda": 2,
    "Fargate": 2,
    "Aurora": 3,
    "RDS": 3,
    "DynamoDB": 3,
    "Redshift": 3,
    "OpenSearch": 3,
    "SQS": 4,
    "SNS": 4,
    "EventBridge": 4,
}


class LayoutGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.containers: Dict[str, Container] = {}

        self.adjacency = defaultdict(set)
        self.reverse_adjacency = defaultdict(set)

        self.layers: Dict[str, int] = {}
        self.roots: Set[str] = set()

        self.container_nodes = defaultdict(list)
        self.container_children = defaultdict(list)

        self.rank_groups = defaultdict(list)
        self.az_nodes = defaultdict(list)

        self.disconnected_nodes = set()


class GraphBuilder:

    def build(self, architecture: Architecture) -> LayoutGraph:

        graph = LayoutGraph()

        self._load_nodes(graph, architecture.nodes)
        self._load_edges(graph, architecture.edges)
        self._load_containers(graph, architecture.containers)

        self._validate(graph)
        self._resolve_containers(graph)
        self._compute_roots(graph)
        self._assign_layers(graph)
        self._assign_aws_layers(graph)
        self._detect_rank_groups(graph)
        self._detect_disconnected(graph)

        return graph

    def _load_nodes(self, graph, nodes):

        for node in nodes:
            graph.nodes[node.id] = node

    def _load_edges(self, graph, edges):

        graph.edges.extend(edges)

        for edge in edges:
            graph.adjacency[edge.source].add(edge.target)
            graph.reverse_adjacency[edge.target].add(edge.source)

    def _load_containers(self, graph, containers):

        for container in containers:
            graph.containers[container.id] = container

    def _validate(self, graph):

        for edge in graph.edges:

            if edge.source not in graph.nodes:
                raise ValueError(f"Unknown source node: {edge.source}")

            if edge.target not in graph.nodes:
                raise ValueError(f"Unknown target node: {edge.target}")

    def _resolve_containers(self, graph):

        for node in graph.nodes.values():

            container_id = getattr(node, "container_id", None)

            if container_id:
                graph.container_nodes[container_id].append(node.id)
                self._assign_az(graph, container_id, node.id)

        for container in graph.containers.values():

            parent_id = getattr(container, "parent_id", None)

            if parent_id:
                graph.container_children[parent_id].append(container.id)

    def _assign_az(
        self,
        graph,
        container_id,
        node_id
    ):
    
        current = graph.containers.get(
            container_id
        )
    
        while current:
    
            if (
                getattr(current, "type", "").lower()
                in (
                    "availability_zone",
                    "az"
                )
            ):
    
                graph.az_nodes[
                    current.id
                ].append(node_id)
    
                return
    
            if getattr(
                current,
                "availability_zone",
                None
            ):
    
                graph.az_nodes[
                    current.id
                ].append(node_id)
    
                return
    
            parent_id = getattr(
                current,
                "parent_id",
                None
            )
    
            if not parent_id:
                return
    
            current = graph.containers.get(
                parent_id
            )
        
    def _compute_roots(self, graph):

        for node_id in graph.nodes:

            if not graph.reverse_adjacency[node_id]:
                graph.roots.add(node_id)

    def _assign_layers(self, graph):

        queue = deque()
        visited = set()
        queued = set()

        for root in graph.roots:

            graph.layers[root] = 0
            queue.append(root)
            queued.add(root)

        while queue:

            current = queue.popleft()
            visited.add(current)

            current_layer = graph.layers[current]

            for child in graph.adjacency[current]:

                graph.layers[child] = max(
                    graph.layers.get(child, 0),
                    current_layer + 1,
                )

                if child not in visited and child not in queued:
                    queue.append(child)
                    queued.add(child)

    def _assign_aws_layers(self, graph):
    
        for node_id, node in graph.nodes.items():
    
            # Explicit layer from architecture JSON wins
            if getattr(node, "layer", 0) > 0:
                graph.layers[node_id] = node.layer
                continue
    
            service = getattr(node, "service", None)
    
            if not service:
                continue
    
            aws_layer = AWS_LAYER_MAP.get(service)
    
            if aws_layer is not None:
                graph.layers[node_id] = aws_layer
            
    def _detect_rank_groups(self, graph):

        for node in graph.nodes.values():

            service = getattr(node, "service", None)

            if service:
                graph.rank_groups[service].append(node.id)

    def _detect_disconnected(self, graph):

        reachable = set()
        queue = deque(graph.roots)

        while queue:

            current = queue.popleft()

            if current in reachable:
                continue

            reachable.add(current)

            for child in graph.adjacency[current]:
                queue.append(child)

        graph.disconnected_nodes = (
            set(graph.nodes.keys()) - reachable
        )
