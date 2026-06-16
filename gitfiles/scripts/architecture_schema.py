from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Container:

    id: str
    name: str
    type: str
    # region
    # vpc
    # availability_zone
    # subnet

    parent_id: str | None = None

@dataclass
class Node:
    id: str
    label: str
    service: str
    container_id: Optional[str] = None
    layer: int = 0


@dataclass
class Edge:
    source: str
    target: str

@dataclass
class Architecture:
    title: str
    description: str
    nodes: List[Node]
    edges: List[Edge]
    containers: Optional[List[Container]] = None

    @classmethod
    def model_validate(cls, data):

        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            nodes=[
                Node(**n)
                for n in data.get("nodes", [])
            ],
            edges=[
                Edge(**e)
                for e in data.get("edges", [])
            ],
            containers=[
                Container(**c)
                for c in data.get("containers", [])
            ]
        )
