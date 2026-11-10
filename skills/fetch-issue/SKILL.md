---
name: fetch-issue
description: 通过 MCP 获取外部 issue 信息。Use this when 用户说“查 issue”“看任务单”“获取 issue”“fetch issue”。
---

## 什么时候用
用户要求读取仓库外部的 issue / 任务信息时。

## 步骤
1. 确认 MCP server 可用。
2. 使用 MCP 的 issue 工具，而不是新增第五个内置工具。
3. 获取 issue 的标题、状态和正文摘要。
4. 把 MCP 返回值作为真实 Observation 回灌。
5. MCP 不可用时明确报告，不偷偷换成浏览器或桌面自动点击。

## 不要做什么
- 不要伪造 issue 数据。
- 不要把 MCP 失败当成功。

## 怎么算做完了
- 日志能看到 `mcp:<server>/<tool>`。
- 最终回答引用了 MCP 的真实返回结果。
