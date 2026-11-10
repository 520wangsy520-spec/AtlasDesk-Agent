from __future__ import annotations
import json, subprocess, threading, sys
from .config import ROOT, ENABLE_MCP

class MCPClient:
    def __init__(self,name,command):
        self.name=name; self.command=command; self.proc=None; self.next_id=1; self.lock=threading.Lock()
    def start(self):
        if not ENABLE_MCP: raise RuntimeError("MCP disabled")
        if self.proc and self.proc.poll() is None: return
        self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def request(self,method,params=None):
        self.start()
        with self.lock:
            rid=self.next_id; self.next_id+=1
            payload={"jsonrpc":"2.0","id":rid,"method":method}
            if params is not None: payload["params"]=params
            self.proc.stdin.write(json.dumps(payload,ensure_ascii=False)+"\n"); self.proc.stdin.flush()
            line=self.proc.stdout.readline()
            if not line:
                raise RuntimeError("MCP server closed")
            msg=json.loads(line)
            if "error" in msg: raise RuntimeError(msg["error"]["message"])
            return msg["result"]
    def list_tools(self): return self.request("tools/list").get("tools",[])
    def call(self,tool,args): return self.request("tools/call",{"name":tool,"arguments":args})

def load_clients():
    if not ENABLE_MCP: return {}
    path=ROOT/"mcp.json"
    if not path.exists(): return {}
    cfg=json.loads(path.read_text(encoding="utf-8"))
    out={}
    for name,spec in cfg.get("mcpServers",{}).items():
        exe=sys.executable if spec["command"]=="$SELF" else spec["command"]
        out[name]=MCPClient(name,[exe,*spec.get("args",[])])
    return out
