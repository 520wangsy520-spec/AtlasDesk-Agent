from pathlib import Path
from agent.config import WORKSPACE
from agent.tools import edit
from agent.hooks import after_tool, reset_metrics

def main():
    target=WORKSPACE/"calculator.py"
    original=target.read_text(encoding="utf-8")
    if "return a + b" not in original:
        raise SystemExit("calculator.py is not in expected baseline state.")
    reset_metrics()
    print("1) baseline reset")
    r1=edit("calculator.py","return a + b","return a * b")
    print(after_tool("edit",{"path":"calculator.py"},r1))
    r2=edit("calculator.py","return a * b","return a + b")
    print(after_tool("edit",{"path":"calculator.py"},r2))
    print("2) restored calculator.py")
    print("Now run: python -m app.inspect custom --out custom_report.json")

if __name__=="__main__":
    main()
