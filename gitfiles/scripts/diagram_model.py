from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Point:
    x: float
    y: float


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class DiagramNode:
    id: str
    label: str

    x: float
    y: float

    width: float
    height: float

    service: str | None = None

    attrs: Dict = field(default_factory=dict)


@dataclass
class DiagramEdge:
    source: str
    target: str

    points: List[Point] = field(default_factory=list)

    attrs: Dict = field(default_factory=dict)


@dataclass
class DiagramContainer:
    id: str
    label: str

    bbox: BoundingBox

    attrs: Dict = field(default_factory=dict)


@dataclass
class DiagramModel:

    width: float
    height: float

    nodes: List[DiagramNode] = field(default_factory=list)

    edges: List[DiagramEdge] = field(default_factory=list)

    containers: List[DiagramContainer] = field(default_factory=list)
