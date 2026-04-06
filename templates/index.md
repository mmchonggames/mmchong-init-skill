# templates

面向目标仓库的 **可复制模板**（不单独构建）。维护 Cursor hooks 时请先改 `cursor/hooks/prompts/*.md`，再同步到 `cursor/hooks.json`。

## 子路径

| 路径 | 说明 |
|------|------|
| `BOOTSTRAP.md` | 首次初始化引导（随 `apply-to-repo.sh` 写入目标仓库根目录，若不存在） |
| `cursor/` | `hooks.json`、`hooks/`（stop 脚本与 prompts） |
| `harness-skeleton/` | 空 harness 目录树 |
| `AGENTS.example.md` / `ROOT_INDEX.example.md` | 复制为根目录 `AGENTS.md`、`index.md` 后改写（无特定业务项目文案） |

## 关联

- 详细表格见同目录 [README.md](README.md)
