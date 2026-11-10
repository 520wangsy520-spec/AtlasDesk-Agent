# 项目地图
agent/ 负责智能体循环、四工具、技能、hooks、MCP 与 reviewer
server/ 本地 HTTP + SSE 桥接
ui/ 三栏桌面界面
skills/ 三个按需加载技能
workspace/ 唯一允许 agent 修改的沙箱目录
tests/ 验收用确定性测试

# 构建与测试
python -m unittest discover -s tests -v
python -m app.inspect skills --out skill_report.json
python -m app.inspect custom --out custom_report.json

# 代码风格
- Python 3.11+
- 不新增第五个内置工具
- 工具错误必须可读，并告诉模型下一步怎么做

# 测试说明
- 工具测试不依赖网络
- edit 必须拒绝 0 次或多次匹配
- bash 必须有 timeout 与输出截断

# 安全约束
- 不允许访问 workspace 之外文件
- 不写 .env / *.pem / *.key
- 不运行 rm -rf / git push --force / git reset --hard

# 坑
- pywebview 才是桌面壳，不要把浏览器地址栏当成成品
- 打包后 workspace 位于 ~/Documents/AtlasDesk-workspace
- MCP stdio 的 stdout 只能传 JSON-RPC
