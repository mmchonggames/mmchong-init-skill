# templates/claude

Claude 编辑器配置模板：`.claude/` 目录结构，应用于目标仓库。

## 包含内容

- `settings.json` — SessionStart / PreCompact / Stop 钩子配置
- `hooks/` — Python 脚本与提示词

## 使用

由 `install/apply-to-repo.sh` 自动复制到目标仓库的 `.claude/`。
