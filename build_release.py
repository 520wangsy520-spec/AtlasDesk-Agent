from __future__ import annotations
import os, subprocess, sys
sep=";" if os.name=="nt" else ":"
args=[sys.executable,"-m","PyInstaller","--noconfirm","--clean","--windowed","--name","AtlasDesk",
      "--add-data",f"ui{sep}ui","--add-data",f"skills{sep}skills","--add-data",f"AGENTS.md{sep}.","--add-data",f"mcp.json{sep}.","desktop.py"]
print(" ".join(args)); subprocess.check_call(args)
