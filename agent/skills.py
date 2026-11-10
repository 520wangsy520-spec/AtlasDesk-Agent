from __future__ import annotations
import re
from pathlib import Path
from .config import ROOT, ENABLE_SKILLS

SKILLS_DIR = ROOT / "skills"

def _parse(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", text, flags=re.S)
    if not m:
        return None
    meta_text, body = m.groups()
    meta = {}
    for line in meta_text.splitlines():
        if ":" in line:
            k,v = line.split(":",1)
            meta[k.strip()] = v.strip().strip('"')
    return {"name":meta.get("name",path.parent.name),"description":meta.get("description",""),"body":body.strip(),"path":path}

def catalog():
    if not ENABLE_SKILLS:
        return []
    out=[]
    for p in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        item=_parse(p)
        if item:
            out.append({"name":item["name"],"description":item["description"]})
    return out

def load_skill(name: str) -> str:
    if not ENABLE_SKILLS:
        raise RuntimeError("Skills disabled")
    for p in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        item=_parse(p)
        if item and item["name"]==name:
            return item["body"]
    raise KeyError(name)

def catalog_prompt():
    items=catalog()
    if not items:
        return "Skills disabled."
    return "Available skills (load body only after trigger):\n" + "\n".join(f"- {x['name']}: {x['description']}" for x in items)

def match_skill(prompt: str):
    p=prompt.lower()
    rules=[
        ("run-tests",("跑测试","跑一下测试","测一下","为什么挂了","run tests","test failure")),
        ("review-diff",("审一下 diff","审一遍 diff","把这段 diff 审一遍","代码审查","看看改了什么","检查 diff","review diff")),
        ("fetch-issue",("查 issue","看任务单","获取 issue","fetch issue","外部 issue")),
    ]
    for name,phrases in rules:
        if any(x in p for x in phrases):
            return name
    return None
