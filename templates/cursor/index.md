# cursor（模板）

复制到目标仓库 **`.cursor/`** 的 Cursor 配置：本会话启动、压缩前与 **stop** 钩子的来源模板。

## 核心文件

- `hooks.json` — `sessionStart`、`preCompact`、`stop`
- `hooks/` — `stop_verify.py`、`stop_task_harness.py`、`prompts/`

## 关联

- 应用脚本：[../install/apply-to-repo.sh](../install/apply-to-repo.sh)
