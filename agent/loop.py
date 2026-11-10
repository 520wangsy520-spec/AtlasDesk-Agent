from __future__ import annotations
import json, threading
from .model import chat
from .tools import TOOLS, TOOL_SCHEMAS
from .hooks import before_tool, after_tool, on_user_prompt
from .skills import catalog_prompt, match_skill, load_skill
from .mcp_client import load_clients
from .context import load_agents_context

SYSTEM="""你是 AtlasDesk，一个桌面代码智能体。
你只有四个内置工具：read/write/edit/bash。
先读后改；小范围修改优先 edit；完成前必须给出验证证据。
工具执行权在宿主程序，任何 hook 拒绝都必须遵守。"""

def _mcp_schemas(clients):
    schemas=[]; mapping={}
    for server,client in clients.items():
        try:
            for tool in client.list_tools():
                ext=f"mcp__{server}__{tool['name']}"
                mapping[ext]=(client,tool["name"])
                schemas.append({"type":"function","function":{"name":ext,"description":f"[MCP:{server}] {tool.get('description','')}",
                    "parameters":tool.get("inputSchema",{"type":"object","properties":{}})}})
        except Exception:
            continue
    return schemas,mapping

def run_agent(prompt, emit=lambda e:None, cancel_event=None, max_steps=8):
    cancel_event=cancel_event or threading.Event()
    agents_text,_=load_agents_context()
    skill_name=match_skill(prompt)
    skill_body=load_skill(skill_name) if skill_name else ""
    system=SYSTEM+"\n\n"+agents_text+"\n\n"+catalog_prompt()
    if skill_body:
        system += f"\n\nLoaded skill: {skill_name}\n{skill_body}"
        emit({"type":"skill","name":skill_name})
    clients=load_clients()
    mcp_tools,mcp_map=_mcp_schemas(clients)
    messages=[{"role":"system","content":system},
              {"role":"user","content":(on_user_prompt(prompt)+"\n"+prompt).strip()}]
    all_tools=TOOL_SCHEMAS+mcp_tools

    for step in range(1,max_steps+1):
        if cancel_event.is_set():
            emit({"type":"cancelled"}); return "已中断。"
        emit({"type":"status","text":f"step {step}/{max_steps}"})
        reply=chat(messages, tools=all_tools)
        messages.append(reply)
        calls=reply.get("tool_calls") or []
        if not calls:
            text=reply.get("content") or "完成。"
            emit({"type":"final","text":text}); return text
        for call in calls:
            name=call["function"]["name"]
            try: args=json.loads(call["function"].get("arguments") or "{}")
            except Exception: args={}
            emit({"type":"tool_start","name":name,"args":args})
            if name in TOOLS:
                allowed,reason=before_tool(name,args)
                if not allowed:
                    result={"error":reason}
                    emit({"type":"tool_error","name":name,"result":result})
                else:
                    try:
                        result=TOOLS[name](**args)
                        hint=after_tool(name,args,result)
                        emit({"type":"tool_result","name":name,"result":result,"hint":hint})
                    except Exception as exc:
                        result={"error":f"{type(exc).__name__}: {exc}"}
                        emit({"type":"tool_error","name":name,"result":result})
            elif name in mcp_map:
                client,tool_name=mcp_map[name]
                try:
                    result=client.call(tool_name,args)
                    emit({"type":"tool_result","name":f"mcp:{client.name}/{tool_name}","result":result})
                except Exception as exc:
                    result={"error":f"MCP error: {exc}"}
                    emit({"type":"tool_error","name":name,"result":result})
            else:
                result={"error":"unknown tool"}
            messages.append({"role":"tool","tool_call_id":call["id"],"name":name,"content":json.dumps(result,ensure_ascii=False)[:16000]})
    text="达到最大步数，已安全停止。"
    emit({"type":"final","text":text}); return text
