from pathlib import Path
from agent.config import GLOBAL_AGENTS

CONTENT="""# 全局规则
- 修改之前先 read
- 小范围修改优先 edit
- 完成前必须运行测试并引用证据
- 密钥只使用环境变量，不写入仓库
"""

def main():
    GLOBAL_AGENTS.parent.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_AGENTS.exists():
        GLOBAL_AGENTS.write_text(CONTENT, encoding="utf-8")
        print(f"created: {GLOBAL_AGENTS}")
    else:
        print(f"exists: {GLOBAL_AGENTS}")

if __name__=="__main__":
    main()
