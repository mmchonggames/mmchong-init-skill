# hooks

Claude **stop** 钩子可执行脚本与会话提示 Markdown。

## 核心文件

- `stop_verify.py` — 调用 `scripts/verify/large_py_files.py`；检查已变更 `.py` 所在目录是否有 `index.md`
- `stop_task_harness.py` — 读取 `harness/context/current-task.md` 中的 `active_task_id` 与 `harness/tasks/active/task-*.md` 一致性
- `prompts/session_start.md`、`prompts/precompact_memory.md` — 与 `settings.json` 中 prompt 同步维护

## 关联

- [../index.md](../index.md)
