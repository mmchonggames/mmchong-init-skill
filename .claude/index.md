# .claude

Claude 编辑器配置目录：本会话启动、压缩前与 **stop** 钩子的入口。

## 核心文件

- `settings.json` — `SessionStart`、`PreCompact`、`Stop`（调用 `hooks/` 下 Python 脚本）
- `hooks/stop_verify.py` — 校验 Python 行数与已修改 `.py` 旁是否有 `index.md`
- `hooks/stop_task_harness.py` — 与 `harness/context/current-task.md` 中的任务 id 对齐
- `hooks/prompts/` — 与 `settings.json` 内联文案应保持语义一致

## 关联

- 模板单一来源：`templates/cursor/`（更新后若需本仓库生效，可重新执行 `./install/apply-to-repo.sh "$(pwd)"`）
- 对应 Cursor 配置：`.cursor/`
