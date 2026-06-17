from dataclasses import dataclass, field
from typing import List, Optional
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import TypeAdapter

@pydantic_dataclass
class Container:
    id: str
    name: str
    type: str
    region: Optional[str] = None
    vpc: Optional[str] = None
    availability_zone: Optional[str] = None
    subnet: Optional[str] = None
    parent_id: Optional[str] = None

@pydantic_dataclass
class Node:
    id: str
    label: str
    service: str
    container_id: Optional[str] = None
    layer: int = 0

@pydantic_dataclass
class Edge:
    source: str
    target: str

@dataclass
class Architecture:
    title: str
    description: str
    nodes: List[Node]
    edges: List[Edge]
    containers: List[Container] = field(default_factory=list)

    @classmethod
    def model_validate(cls, data):
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            nodes=[Node(**n) for n in data.get("nodes", [])],
            edges=[Edge(**e) for e in data.get("edges", [])],
            containers=[Container(**c) for c in data.get("containers", [])]
        )

    @classmethod
    def model_json_schema(cls):
        """Generates a JSON schema for the Architecture class."""
        # We use TypeAdapter to generate the schema from the dataclass structure
        adapter = TypeAdapter(cls)
        return adapter.json_schema()
