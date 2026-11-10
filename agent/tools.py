from __future__ import annotations
from pathlib import Path
import base64, difflib, mimetypes, os, subprocess, tempfile
from .config import WORKSPACE

MAX_BASH_OUTPUT = 12000
MAX_IMAGE_BYTES = 4_000_000

def _resolve(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    base = WORKSPACE.resolve()
    if p != base and base not in p.parents:
        raise ValueError("拒绝：路径越界。请使用 workspace 内的相对路径。")
    return p

def read(path: str, offset: int = 1, limit: int = 200):
    p = _resolve(path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在：{path}")
    mime, _ = mimetypes.guess_type(p.name)
    if mime and mime.startswith("image/"):
        raw = p.read_bytes()
        if len(raw) > MAX_IMAGE_BYTES:
            raise ValueError("图片过大，请压缩到 4 MB 以内。")
        return {"type":"image","mime_type":mime,"data":base64.b64encode(raw).decode("ascii"),"path":path}
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, int(offset))
    lim = min(max(1, int(limit)), 500)
    chunk = lines[start-1:start-1+lim]
    out = "\n".join(f"{i:>5} | {line}" for i, line in enumerate(chunk, start=start))
    remain = max(0, len(lines) - (start-1+len(chunk)))
    return out + (f"\n--- 还有 {remain} 行 ---" if remain else "\n--- EOF ---")

def write(path: str, content: str):
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    old_lines = len(p.read_text(encoding="utf-8", errors="replace").splitlines()) if p.exists() else 0
    new_lines = len(content.splitlines())
    fd, temp = tempfile.mkstemp(prefix=p.name+".", suffix=".tmp", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, p)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return f"写入完成：{path}；原 {old_lines} 行，现在 {new_lines} 行。"

def edit(path: str, old: str, new: str):
    p = _resolve(path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在：{path}")
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        raise ValueError("编辑失败：old 文本出现 0 次。请先 read 获取精确上下文。")
    if count > 1:
        raise ValueError(f"编辑失败：old 文本出现 {count} 次，不唯一。请扩大 old 上下文。")
    updated = text.replace(old, new, 1)
    diff = "\n".join(difflib.unified_diff(text.splitlines(), updated.splitlines(), fromfile=path, tofile=path, lineterm=""))
    write(path, updated)
    return f"编辑完成：{path}\n{diff[:8000]}"

def bash(command: str, timeout: int = 30):
    timeout = min(max(1, int(timeout)), 120)
    proc = subprocess.run(command, cwd=WORKSPACE, shell=True, text=True, capture_output=True, timeout=timeout)
    stdout = proc.stdout[-MAX_BASH_OUTPUT//2:]
    stderr = proc.stderr[-MAX_BASH_OUTPUT//2:]
    return {"exit_code":proc.returncode,"stdout":stdout,"stderr":stderr,
            "truncated":len(proc.stdout)+len(proc.stderr)>MAX_BASH_OUTPUT}

TOOL_SCHEMAS = [
    {"type":"function","function":{"name":"read","description":"读取 workspace 内文件。需要查看代码、文本或图片时使用；大文件使用 offset/limit 分页。",
     "parameters":{"type":"object","properties":{"path":{"type":"string"},"offset":{"type":"integer","default":1},"limit":{"type":"integer","default":200}},"required":["path"]}}},
    {"type":"function","function":{"name":"write","description":"原子写入 workspace 内文件。创建新文件或明确覆盖整个文件时使用。",
     "parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"edit","description":"精确替换一次字符串。小范围修改优先使用；old 不唯一会拒绝。",
     "parameters":{"type":"object","properties":{"path":{"type":"string"},"old":{"type":"string"},"new":{"type":"string"}},"required":["path","old","new"]}}},
    {"type":"function","function":{"name":"bash","description":"在 workspace 内运行命令，用于搜索、Git、测试和安装。必须设置超时；非零退出码也是正常观察结果。",
     "parameters":{"type":"object","properties":{"command":{"type":"string"},"timeout":{"type":"integer","default":30}},"required":["command"]}}},
]
TOOLS = {"read":read,"write":write,"edit":edit,"bash":bash}
