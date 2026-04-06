# harness/tasks

Agent 任务管理目录，采用三层任务队列结构管理任务生命周期。

## 主要内容

- `active/` — 活跃任务（正在执行）
- `backlog/` — 待办任务池（计划中）
- `completed/` — 已完成任务存档

## 任务文件格式

任务文件建议命名为 `task-<slug>.md`，包含：任务 ID、状态、描述与实施步骤（可选用 checklist）。

## 关联

- `active/` 中的任务由 Agent 主动认领执行
- 完成后移动到 `completed/` 并更新各层 `index.md`

## stop hook

在 `harness/context/current-task.md` 中设置 `active_task_id` 后，会话结束时的 `stop` hook 可检查任务是否完成并提示归档（实现见 `.cursor/hooks/stop_task_harness.py`）。
