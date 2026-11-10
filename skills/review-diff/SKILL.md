---
name: review-diff
description: 审查当前代码改动并输出问题清单。Use this when 用户说“审一下 diff”“代码审查”“看看改了什么”“review diff”。
---

## 什么时候用
用户希望检查当前改动质量，而不是继续实现功能时。

## 步骤
1. 用 bash 执行 `python ../skills/review-diff/scripts/collect_diff.py` 获取 diff。
2. 只检查当前 diff，不扩散到整个仓库。
3. 检查是否修改无关文件。
4. 检查是否新增不必要依赖。
5. 检查 `except: pass`。
6. 检查新分支是否缺少测试。
7. 检查 `print(` / `TODO` 等调试残留。
8. 只报告，不修改。

## 不要做什么
- 不要直接写文件。
- 不要重新实现业务逻辑。

## 怎么算做完了
- 输出问题列表；若没有问题，明确写“未发现问题”。
