from __future__ import annotations
from .config import ENABLE_REVIEWER
from .model import chat
from .tools import bash
from .hooks import record_reviewer

PROMPT="""你是只读 reviewer。你不能修改文件，也没有工具权限。
只检查传入的 git diff：
1) 是否改到不该改的文件；
2) 是否新增不必要依赖；
3) 是否出现 except: pass；
4) 新分支是否缺少测试；
5) 是否有 print( / TODO 调试残留。
只返回最终问题列表，不回传中间过程。控制在 400 中文字以内。"""

def _tok(s:str)->int:
    return max(1,(len(s)+3)//4)

def review_current_diff():
    if not ENABLE_REVIEWER:
        return "Reviewer disabled."
    obs=bash("git diff -- .", timeout=10)
    diff=obs["stdout"] or "(no diff)"
    msg=chat([{"role":"system","content":PROMPT},{"role":"user","content":diff[:12000]}],tools=None)
    text=msg.get("content","")
    issues=sum(1 for line in text.splitlines() if line.strip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")))
    record_reviewer(issues, _tok(text), _tok(PROMPT+diff[:12000]))
    return text
