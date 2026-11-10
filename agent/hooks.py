
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from .config import ENABLE_HOOKS, WORKSPACE


STATE_DIR = WORKSPACE / ".agent"
STATE_FILE = STATE_DIR / "metrics.json"

DEFAULT = {
    "denied": [],
    "autotest": {
        "runs": 0,
        "red": 0,
        "green": 0,
        "red_to_green": 0,
        "injected_lines": 0,
        "last_was_red": False,
    },
    "reviewer": {
        "runs": 0,
        "issues_found": 0,
        "main_context_delta": 0,
        "subagent_tokens": 0,
    },
}


def _load():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = json.loads(json.dumps(DEFAULT))

    for key, value in DEFAULT.items():
        data.setdefault(key, json.loads(json.dumps(value)))

    return data


def _save(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_metrics():
    _save(json.loads(json.dumps(DEFAULT)))


def get_metrics():
    return _load()


def before_tool(name: str, args: dict) -> tuple[bool, str]:
    if not ENABLE_HOOKS:
        return True, ""

    data = _load()

    # 拦截敏感文件操作
    if name in {"read", "write", "edit"}:
        path = str(args.get("path", "")).lower()

        if (
            path.endswith(".env")
            or path.endswith(".pem")
            or path.endswith(".key")
            or "/.env" in path
            or "\\.env" in path
        ):
            reason = (
                "密钥不入库，用环境变量；"
                "需要示例时只写 .env.example。"
            )

            data["denied"].append(
                {
                    "tool": name,
                    "path": args.get("path", ""),
                    "reason": reason,
                }
            )

            _save(data)
            return False, reason

    # 拦截危险命令
    if name == "bash":
        cmd = str(args.get("command", "")).lower()

        if "rm -rf" in cmd:
            reason = (
                "拒绝 rm -rf；替代方案："
                "先用 git clean -nd 预览，"
                "再用 git restore 或明确删除单个文件。"
            )

            data["denied"].append(
                {
                    "tool": "bash",
                    "command": args.get("command", ""),
                    "reason": reason,
                }
            )

            _save(data)
            return False, reason

        if "git push --force" in cmd or "git push -f" in cmd:
            reason = (
                "拒绝 force push；替代方案："
                "使用普通 push，必要时新建修复提交。"
            )

            data["denied"].append(
                {
                    "tool": "bash",
                    "command": args.get("command", ""),
                    "reason": reason,
                }
            )

            _save(data)
            return False, reason

        if "git reset --hard" in cmd:
            reason = (
                "拒绝 git reset --hard；替代方案："
                "优先 git revert 或 git restore。"
            )

            data["denied"].append(
                {
                    "tool": "bash",
                    "command": args.get("command", ""),
                    "reason": reason,
                }
            )

            _save(data)
            return False, reason

    return True, ""


def _summarize(text: str):
    """
    从 unittest 输出中提取关键测试信息。
    """
    out = []

    for line in text.splitlines():
        if (
            "FAIL:" in line
            or "ERROR:" in line
            or "AssertionError" in line
            or "FAILED (" in line
        ):
            out.append(line.strip())

        if len(out) >= 3:
            break

    if not out:
        for line in reversed(text.splitlines()):
            if "FAILED" in line or line.strip() == "OK":
                out = [line.strip()]
                break

    return out[:3]


def _clear_workspace_pycache():
    """
    清理工作区内的 Python 字节码缓存。

    解决以下场景：
    1. 自动测试运行失败（red）。
    2. Agent 迅速修复源代码。
    3. Python 仍然读取旧的 .pyc 缓存。
    4. 自动测试错误地继续报告 red。

    仅清理 WORKSPACE 内的 __pycache__ 目录，
    不删除 Python 源代码或其他项目文件。
    """
    if not WORKSPACE.exists():
        return

    for cache_dir in WORKSPACE.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)


def run_autotest():
    """
    自动运行 unittest，并记录 red / green 状态。
    """
    if not ENABLE_HOOKS:
        return {
            "ran": False,
            "summary": [],
        }

    data = _load()
    a = data["autotest"]

    a["runs"] += 1

    # 关键修复：每次测试前清理旧字节码缓存
    _clear_workspace_pycache()

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            ".",
            "-p",
            "test*.py",
        ],
        cwd=WORKSPACE,
        text=True,
        capture_output=True,
        timeout=30,
    )

    output = (proc.stdout + "\n" + proc.stderr).strip()
    summary = _summarize(output)

    a["injected_lines"] += len(summary)

    if proc.returncode == 0:
        a["green"] += 1

        # 上一次失败、本次成功，记录一次 red -> green
        if a.get("last_was_red"):
            a["red_to_green"] += 1

        a["last_was_red"] = False
        status = "green"

    else:
        a["red"] += 1
        a["last_was_red"] = True
        status = "red"

    _save(data)

    return {
        "ran": True,
        "status": status,
        "exit_code": proc.returncode,
        "summary": summary,
    }


def after_tool(name: str, args: dict, result):
    """
    write / edit 工具执行后，自动运行测试。
    """
    if not ENABLE_HOOKS or name not in {"write", "edit"}:
        return ""

    auto = run_autotest()

    if not auto["summary"]:
        return (
            f"自动测试：{auto['status']}"
            f"（exit={auto['exit_code']}）"
        )

    return (
        "自动测试："
        + auto["status"]
        + "\n"
        + "\n".join(auto["summary"])
    )


def record_reviewer(
    issues_found: int,
    main_context_delta: int,
    subagent_tokens: int,
):
    """
    记录 Reviewer 子代理的运行统计。
    """
    data = _load()
    r = data["reviewer"]

    r["runs"] += 1
    r["issues_found"] += int(issues_found)
    r["main_context_delta"] = int(main_context_delta)
    r["subagent_tokens"] += int(subagent_tokens)

    _save(data)


def on_user_prompt(prompt: str) -> str:
    """
    为 Agent 注入开发规范提醒。
    """
    if not ENABLE_HOOKS:
        return ""

    return (
        "提醒：先读再改；"
        "小改动用 edit；"
        "完成前必须给出测试证据。"
    )