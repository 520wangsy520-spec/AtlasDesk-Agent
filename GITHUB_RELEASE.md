# GitHub 发布

```powershell
git init
git add .
git commit -m "baseline: desktop agent v1.0"
git tag v1.0

# 完成技能系统后
git add .
git commit -m "feat: add skill system"
git tag v1.1

# 完成定制层后
git add .
git commit -m "feat: add agents hooks reviewer"
git tag v1.2
```

创建 GitHub Public 仓库后：
```powershell
git remote add origin https://github.com/你的用户名/AtlasDesk-Agent.git
git branch -M main
git push -u origin main
git push origin --tags
```

Release 选择 `v1.2`，上传 `dist/AtlasDesk` 对应的 Windows 构建产物。
