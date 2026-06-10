from pydantic import BaseModel
from typing import List, Optional


class Node(BaseModel):
    id: str
    service: str
    label: str
    category: Optional[str] = None


class Edge(BaseModel):
    source: str
    target: str
    relation: str


class Architecture(BaseModel):
    title: str
    description: str
    nodes: List[Node]
    edges: List[Edge]
