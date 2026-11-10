# 作品介绍

AtlasDesk 是一个面向本地代码仓库的桌面智能体，采用 pywebview 提供原生桌面窗口，并严格保留 read、write、edit、bash 四个内置工具。界面同时展示对话和工具轨迹，用户可以看到每次工具调用的参数、结果和错误，并支持中断。

增量 A 实现了三个按需加载技能：run-tests（纯提示词）、review-diff（提示词 + scripts）、fetch-issue（提示词 + MCP）。启动时只加载 name + description，命中触发语后才加载正文。

增量 B 实现了全局 + 项目两层 AGENTS.md、三条代码级 hooks，以及一个只读 reviewer。PreToolUse 会阻止密钥文件和破坏性命令；PostToolUse 在 write/edit 后自动运行测试并注入精简失败摘要；reviewer 只检查 git diff 并只返回最终消息。

项目提供 `python -m app.inspect skills --out skill_report.json` 与 `python -m app.inspect custom --out custom_report.json` 两条独立验收命令，所有数字均由程序生成。
