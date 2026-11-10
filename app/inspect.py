from __future__ import annotations
import argparse, json, os
from pathlib import Path
from agent.config import ROOT
from agent.skills import catalog, match_skill
from agent.context import load_agents_context
from agent import hooks

def approx_tokens(text:str)->int:
    return max(1,(len(text)+3)//4)

def skills_report():
    items=catalog()
    catalog_text="\n".join(f"{x['name']}: {x['description']}" for x in items)
    full_text=""
    detail=[]
    for p in sorted((ROOT/"skills").glob("*/SKILL.md")):
        t=p.read_text(encoding="utf-8")
        full_text+=t+"\n"
        detail.append({
            "name":p.parent.name,
            "has_scripts":(p.parent/"scripts").exists(),
            "uses_mcp":"MCP" in t or "mcp" in t,
        })
    c=approx_tokens(catalog_text); f=approx_tokens(full_text)
    trials_in=[
        ("帮我跑一下测试","run-tests"),
        ("为什么挂了","run-tests"),
        ("把这段 diff 审一遍","review-diff"),
        ("看看改了什么","review-diff"),
        ("帮我查 issue 101","fetch-issue"),
        ("今天天气怎么样",None),
    ]
    trials=[]
    fp=0
    for q,exp in trials_in:
        hit=match_skill(q)
        ok=hit==exp
        if exp is None and hit is not None: fp += 1
        trials.append({"query":q,"expected":exp,"hit":hit,"ok":ok})
    return {"skills":detail,"catalog_tokens":c,"full_tokens":f,"disclosure_ratio":round(f/c,2),"trials":trials,"false_positive":fp}

def custom_report():
    text,layers=load_agents_context()
    # These two probes are genuine code-level denials performed by inspect itself.
    hooks.before_tool("write",{"path":".env","content":"X"})
    hooks.before_tool("bash",{"command":"rm -rf build/"})
    metrics=hooks.get_metrics()
    auto=dict(metrics["autotest"])
    auto.pop("last_was_red", None)
    return {
        "agents_md":{"found":bool(layers),"bytes":len(text.encode("utf-8")),"layers":[x[0] for x in layers]},
        "denied":metrics["denied"][-20:],
        "autotest":auto,
        "reviewer":metrics["reviewer"],
    }

def daemon_report():
    return {"enabled":False,"note":"v1.3 is optional and not implemented in this v1.2 delivery."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("kind", choices=["skills","custom","daemon"])
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    data={"skills":skills_report,"custom":custom_report,"daemon":daemon_report}[args.kind]()
    Path(args.out).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False))

if __name__=="__main__":
    main()
