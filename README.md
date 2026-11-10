# AtlasDesk Agent v1.2 — 从零开始

这是按《增量作业｜给你的 Cursor 装一套技能》重建的交付版。

## A. 第一次运行（Windows PowerShell）
```powershell
cd desktop-agent
python -m pip install .
python -m app.setup_global_agents
python -m unittest discover -s tests -v
```

## B. 生成技能验收报告
```powershell
python -m app.inspect skills --out skill_report.json
Get-Content .\skill_report.json
```

应重点看到：
- skills = 3
- disclosure_ratio >= 5
- trials = 6
- false_positive = 0

## C. 真实 red -> green 验证
下面命令会在 `workspace/calculator.py` 上真实做一次“改错 → 自动测试红 → 恢复 → 自动测试绿”，并恢复源文件：
```powershell
python -m app.demo_red_green
python -m app.inspect custom --out custom_report.json
Get-Content .\custom_report.json
```
这不是手写 JSON；hooks 的统计持久化在 `workspace/.agent/metrics.json`。

## D. 配置模型并启动桌面
```powershell
$env:OPENAI_API_KEY="你的Key"
$env:OPENAI_MODEL="你的模型名"
python desktop.py
```

第三方 OpenAI-compatible 接口可额外设置：
```powershell
$env:OPENAI_BASE_URL="https://你的地址/v1"
```

## E. 功能开关验收
```powershell
$env:ENABLE_SKILLS="0"
python desktop.py
# 关闭窗口后重新打开
$env:ENABLE_SKILLS="1"

$env:ENABLE_HOOKS="0"
python desktop.py
$env:ENABLE_HOOKS="1"
```

## F. 三个技能
- `run-tests`：纯提示词
- `review-diff`：SKILL.md + `scripts/collect_diff.py`
- `fetch-issue`：SKILL.md + MCP `get_issue`

## G. 三条 hook
- PreToolUse：拒绝 `.env / *.pem / *.key`
- PreToolUse：拒绝 `rm -rf / git push --force / git reset --hard`，并给替代方案
- PostToolUse：`write/edit` 后真实运行 workspace 测试并注入最多 3 行摘要

## H. 打包
```powershell
python -m pip install pyinstaller
python build_release.py
```

## I. Git tag
- `v1.0`：基础桌面智能体
- `v1.1`：技能系统
- `v1.2`：定制层（提交版本）
- `v1.3`：常驻选做，本包未实现
