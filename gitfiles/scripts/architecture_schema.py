from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Node:
    id: str
    label: str
    service: str
    group: str
    layer: int = 0


@dataclass
class Edge:
    source: str
    target: str


@dataclass
class Container:
    name: str
    children: List[str]


@dataclass
class Architecture:
    title: str
    description: str
    nodes: List[Node]
    edges: List[Edge]
    containers: Optional[List[Container]] = None
