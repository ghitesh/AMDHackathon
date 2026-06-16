"""
graphviz_layout_engine.py

Production Graphviz Layout Engine.

Pipeline:

Architecture
    ->
LayoutGraph
    ->
Graphviz DOT
    ->
XDOT
    ->
DiagramModel
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from dataclasses import asdict

from graph_builder import GraphBuilder
from graphviz_cluster_generator import (
    GraphvizClusterGenerator,
)
from graphviz_xdot_parser import (
    GraphvizXDotParser,
)

from aws_architecture_schema import (
    Architecture,
)

from diagram_model import (
    DiagramModel,
)


class GraphvizLayoutEngine:

    def __init__(
        self,
        cache_dir: str | Path = ".layout_cache",
    ):

        self.builder = GraphBuilder()

        self.parser = GraphvizXDotParser()

        self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ======================================================
    # Public API
    # ======================================================

    def layout(
        self,
        architecture: Architecture,
    ) -> DiagramModel:

        cache_key = self._compute_hash(
            architecture
        )

        cached = self._load_cache(
            cache_key
        )

        if cached:
            return cached

        layout_graph = self.builder.build(
            architecture
        )

        dot_graph = (
            GraphvizClusterGenerator(
                layout_graph
            ).build()
        )

        xdot = self._render_xdot(
            dot_graph
        )

        diagram = self.parser.parse(
            xdot
        )

        self._save_cache(
            cache_key,
            xdot,
        )

        return diagram

    # ======================================================
    # XDOT Rendering
    # ======================================================

    def _render_xdot(
        self,
        dot_graph,
    ) -> str:

        process = subprocess.run(
            [
                "dot",
                "-Txdot",
            ],
            input=dot_graph.source,
            text=True,
            capture_output=True,
            check=True,
        )

        return process.stdout

    # ======================================================
    # Cache
    # ======================================================

    def _compute_hash(
        self,
        architecture,
    ):

        payload = json.dumps(
            asdict(architecture),
            sort_keys=True,
        )

        return hashlib.sha256(
            payload.encode()
        ).hexdigest()

    def _cache_file(
        self,
        cache_key,
    ):

        return (
            self.cache_dir
            / f"{cache_key}.xdot"
        )

    def _save_cache(
        self,
        cache_key,
        xdot,
    ):

        self._cache_file(
            cache_key
        ).write_text(
            xdot,
            encoding="utf-8",
        )

    def _load_cache(
        self,
        cache_key,
    ):

        file = self._cache_file(
            cache_key
        )

        if not file.exists():
            return None

        return self.parser.parse(
            file.read_text(
                encoding="utf-8"
            )
        )

    # ======================================================
    # Debug
    # ======================================================

    def export_dot(
        self,
        architecture,
        output_file,
    ):

        graph = self.builder.build(
            architecture
        )

        dot = (
            GraphvizClusterGenerator(
                graph
            ).build()
        )

        Path(output_file).write_text(
            dot.source,
            encoding="utf-8",
        )

    def export_xdot(
        self,
        architecture,
        output_file,
    ):

        graph = self.builder.build(
            architecture
        )

        dot = (
            GraphvizClusterGenerator(
                graph
            ).build()
        )

        xdot = self._render_xdot(
            dot
        )

        Path(output_file).write_text(
            xdot,
            encoding="utf-8",
        )
