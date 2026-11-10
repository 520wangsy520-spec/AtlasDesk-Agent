from __future__ import annotations
import os, sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
ROOT = RESOURCE_ROOT

if FROZEN:
    WORKSPACE = Path.home() / "Documents" / "AtlasDesk-workspace"
else:
    WORKSPACE = ROOT / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)

GLOBAL_AGENTS = Path.home() / ".atlasdesk" / "AGENTS.md"

def flag(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() not in {"0", "false", "off", "no", ""}

ENABLE_SKILLS = flag("ENABLE_SKILLS", "1")
ENABLE_HOOKS = flag("ENABLE_HOOKS", "1")
ENABLE_REVIEWER = flag("ENABLE_REVIEWER", "1")
ENABLE_MCP = flag("ENABLE_MCP", "1")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY", "")
