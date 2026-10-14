#!/usr/bin/env python3
"""Write a self-contained HTML graph of the knowledge/ bundle: one node per
concept file, colored by OKF type, with an edge for each relative markdown
link between them. Output: <root>/knowledge_graph.html (gitignored).

The page loads vis-network from unpkg at a pinned version.

Usage:
    python scripts/build_visualizer.py
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from claude_home import CLAUDE_DIR, KNOWLEDGE_DIR, as_str, parse_frontmatter, utf8_stdout

OUTPUT = CLAUDE_DIR / "knowledge_graph.html"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")

TYPE_COLORS = {
    "Convention": "#4e79a7",
    "Skill": "#59a14f",
    "Agent": "#f28e2b",
    "Marketplace": "#e15759",
}


def parse_file(path: Path) -> dict:
    fm = parse_frontmatter(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    links = []
    for m in LINK_RE.finditer(text):
        target = (path.parent / m.group(2)).resolve()
        if target.is_file():
            links.append(str(target))
    return {
        "id": str(path.resolve()),
        "title": as_str(fm.get("title")) or path.stem,
        "type": as_str(fm.get("type")) or "Unknown",
        "links": links,
    }


def main() -> None:
    utf8_stdout()
    nodes = [parse_file(f) for f in sorted(KNOWLEDGE_DIR.rglob("*.md"))]
    id_map = {n["id"]: i for i, n in enumerate(nodes)}

    graph_nodes = [
        {"id": i, "label": n["title"], "color": TYPE_COLORS.get(n["type"], "#aaaaaa"), "title": n["type"]}
        for i, n in enumerate(nodes)
    ]
    graph_edges = [
        {"from": id_map[n["id"]], "to": id_map[link]} for n in nodes for link in n["links"] if link in id_map
    ]
    legend = " &nbsp; ".join(
        f'<span style="color:{color}">&#9632;</span> {html.escape(kind)}' for kind, color in TYPE_COLORS.items()
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge Graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/dist/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #1a1a2e; }}
  #graph {{ width: 100vw; height: 100vh; }}
  #legend {{ position: fixed; top: 12px; right: 12px; background: rgba(0,0,0,.7);
             padding: 10px 14px; border-radius: 6px; color: #eee; font: 13px/1.6 monospace; }}
</style>
</head>
<body>
<div id="graph"></div>
<div id="legend"><b>knowledge/</b><br>{legend}</div>
<script>
const nodes = new vis.DataSet({json.dumps(graph_nodes)});
const edges = new vis.DataSet({json.dumps(graph_edges)});
new vis.Network(document.getElementById('graph'), {{ nodes, edges }}, {{
  nodes: {{ shape: 'dot', size: 14, font: {{ color: '#eee', size: 13 }} }},
  edges: {{ arrows: 'to', color: {{ color: '#555' }}, smooth: true }},
  physics: {{ stabilization: false }},
  interaction: {{ hover: true }}
}});
</script>
</body>
</html>
"""
    OUTPUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"Visualizer written to {OUTPUT} ({len(nodes)} nodes, {len(graph_edges)} edges)")


if __name__ == "__main__":
    main()
