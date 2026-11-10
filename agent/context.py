from __future__ import annotations
from pathlib import Path
from .config import ROOT, GLOBAL_AGENTS

def _find_project_agents(start: Path) -> Path | None:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        p = candidate / "AGENTS.md"
        if p.exists():
            return p
    return None

def load_agents_context():
    layers = []
    if GLOBAL_AGENTS.exists():
        text = GLOBAL_AGENTS.read_text(encoding="utf-8")
        layers.append(("global", str(GLOBAL_AGENTS), text))
    project = _find_project_agents(ROOT)
    if project and (not layers or project.resolve() != Path(layers[0][1]).resolve()):
        text = project.read_text(encoding="utf-8")
        layers.append(("project", str(project), text))
    merged = "\n\n".join(f"## {name} AGENTS.md\n{text}" for name, _, text in layers)
    return merged, layers
