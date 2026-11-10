from __future__ import annotations
import json, mimetypes, queue, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from agent.config import ROOT
from agent.loop import run_agent

UI=ROOT/"ui"
ACTIVE={"cancel":threading.Event()}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): return
    def _json(self,status,data):
        raw=json.dumps(data,ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health": return self._json(200,{"ok":True})
        rel="index.html" if path=="/" else path.lstrip("/")
        p=(UI/rel).resolve()
        if UI.resolve() not in p.parents and p!=UI.resolve(): return self.send_error(403)
        if not p.exists(): return self.send_error(404)
        data=p.read_bytes()
        self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(p.name)[0] or "application/octet-stream")
        self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        path=urlparse(self.path).path
        if path=="/api/cancel":
            ACTIVE["cancel"].set(); return self._json(200,{"ok":True})
        if path!="/api/chat": return self._json(404,{"error":"not found"})
        body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
        prompt=str(body.get("prompt","")).strip()
        if not prompt: return self._json(400,{"error":"empty prompt"})
        q=queue.Queue(); cancel=threading.Event(); ACTIVE["cancel"]=cancel
        def emit(e): q.put(e)
        def worker():
            try: run_agent(prompt,emit=emit,cancel_event=cancel)
            except Exception as exc: q.put({"type":"fatal","text":f"{type(exc).__name__}: {exc}"})
            finally: q.put({"type":"_done"})
        threading.Thread(target=worker,daemon=True).start()
        self.send_response(200); self.send_header("Content-Type","text/event-stream; charset=utf-8")
        self.send_header("Cache-Control","no-cache"); self.send_header("Connection","close"); self.end_headers()
        while True:
            e=q.get()
            if e.get("type")=="_done": break
            self.wfile.write(("data: "+json.dumps(e,ensure_ascii=False)+"\n\n").encode("utf-8")); self.wfile.flush()

def start_server(port=8765):
    try: httpd=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    except OSError: httpd=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    threading.Thread(target=httpd.serve_forever,daemon=True).start()
    return httpd.server_address[1],httpd

if __name__=="__main__":
    port,httpd=start_server(); print(f"http://127.0.0.1:{port}",flush=True); threading.Event().wait()
