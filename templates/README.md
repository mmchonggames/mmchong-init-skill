# templates

面向目标仓库的 **可复制模板**，不直接参与 mmchong-init 仓库自身的构建。

| 路径 | 说明 |
|------|------|
| `cursor/hooks.json` | Cursor Hooks 配置；与 `cursor/hooks/*.py`、`prompts/*.md` 配套，复制到目标仓库 **`.cursor/`** |
| `cursor/hooks/` | `stop_verify.py`（已对齐 `index.md` 约定）、`stop_task_harness.py` |
| `harness-skeleton/` | 空 **harness** 骨架；复制到目标仓库 **`harness/`**（若已存在请合并或手工挑选） |
| `AGENTS.example.md` | 从 mmchong.ai 快照的 `AGENTS.md` 示例，需按项目改写 |
| `ROOT_INDEX.example.md` | 根目录 `index.md` 示例 |

维护 `sessionStart` / `preCompact` 文案时：先改 `cursor/hooks/prompts/*.md`，再把等价正文同步进 `hooks.json`（Cursor 要求内联字符串）。
