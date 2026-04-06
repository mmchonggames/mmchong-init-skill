# install

将 **mmchong-init** 中的脚本包、Cursor 模板与 harness 骨架安装到目标 git 仓库的脚本目录。

## 核心文件

- `apply-to-repo.sh` — 将 `scripts-bundle/` 复制为 `<target>/scripts/`，`templates/cursor/` 复制为 `<target>/.cursor/`，若不存在则复制 `templates/harness-skeleton` 为 `<target>/harness/`。

## 关联

- 仓库根 [README.md](../README.md) 中的「快速使用」
- [AGENTS.md](../AGENTS.md) 中的维护与同步说明
