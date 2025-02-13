# 版本发布流程

## 发布流程

- 从 `develop` 新建 `release/x.y.z` 分支，并修改 `package.json` 中的版本号，推送分支至远程仓库，并提交一个合入`develop`的 Pull Request 到仓库
- 仓库的 Github Action 会自动整理上个版本至今 commit 对应的 CHANGELOG，并将 CHANGELOG 的 draft 作为一个评论推送到该 Pull Request 上
- 发布人检查 CHANGELOG，并优化内容逻辑结构，确认无误后删除对于评论首行提示，Github Action 会将优化后的内容写入 CHANGELOG.md 内
- 确认无误后，合并分支入`develop`

合入 `develop` 后，仓库会触发 Github Action 合入 `main` 分支，并将版本号作为 `tag` 打在仓库上
