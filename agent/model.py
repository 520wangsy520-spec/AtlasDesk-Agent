from __future__ import annotations
import json, urllib.request, urllib.error
from .config import API_KEY, BASE_URL, MODEL

def chat(messages, tools=None):
    if not API_KEY:
        raise RuntimeError("未配置 OPENAI_API_KEY。请在系统环境变量中设置；不要写入前端或提交到 Git。")
    payload={"model":MODEL,"messages":messages,"temperature":0.2}
    if tools:
        payload["tools"]=tools
        payload["tool_choice"]="auto"
    req=urllib.request.Request(BASE_URL+"/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data=json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body=exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"模型 API HTTP {exc.code}: {body[:1000]}")
    return data["choices"][0]["message"]
