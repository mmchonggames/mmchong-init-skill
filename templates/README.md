# templates

面向目标仓库的 **可复制模板**，不直接参与 mmchong-init 仓库自身的构建。

| 路径 | 说明 |
|------|------|
| `BOOTSTRAP.md` | **首次初始化引导**：应用到目标仓库根目录后，按此文与用户确认项目信息，填好 `AGENTS.md` / `index.md` 后删除（由 `install/apply-to-repo.sh` 在目标无此文件时复制） |
| `AGENTS.example.md` | 复制为目标仓库根目录 **`AGENTS.md`** 并改写（含「首次读 BOOTSTRAP」提示） |
| `ROOT_INDEX.example.md` | 复制为根目录 **`index.md`** 并改写 |
| `cursor/hooks.json` | Cursor Hooks；与 `cursor/hooks/*.py`、`prompts/*.md` 配套，复制到目标仓库 **`.cursor/`** |
| `cursor/hooks/` | `stop_verify.py`、`stop_task_harness.py` |
| `harness-skeleton/` | 空 **harness** 骨架；复制到目标仓库 **`harness/`**（若已存在请合并或手工挑选） |

维护 `sessionStart` / `preCompact` 文案时：先改 `cursor/hooks/prompts/*.md`，再把等价正文同步进 `hooks.json`（Cursor 要求内联字符串）。
