from __future__ import annotations
import sys, time, webbrowser

def main():
    if "--mcp-demo" in sys.argv:
        from mcp_demo_server import main as m
        m(); return
    from server.app import start_server
    port,httpd=start_server(8765)
    url=f"http://127.0.0.1:{port}/"
    try:
        import webview
    except Exception as exc:
        print(f"pywebview unavailable: {exc}")
        webbrowser.open(url)
        try:
            while True: time.sleep(3600)
        except KeyboardInterrupt:
            httpd.shutdown()
        return
    webview.create_window("AtlasDesk Agent",url=url,width=1280,height=820,min_size=(960,640))
    webview.start(); httpd.shutdown()

if __name__=="__main__": main()
