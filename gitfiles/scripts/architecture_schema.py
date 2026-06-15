from dataclasses import dataclass
from typing import List


@dataclass
class Node:
    id: str
    label: str
    service: str
    group: str


@dataclass
class Edge:
    source: str
    target: str


@dataclass
class Zone:
    name: str
    nodes: List[str]
