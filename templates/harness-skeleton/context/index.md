# harness/context

Agent 当前执行上下文，记录项目的阶段状态和活跃目标。

## 主要内容

- `current-phase.md` — 当前项目阶段说明
- `current-task.md` — 当前认领的 `harness/tasks/active/` 任务 ID（供 `stop` hook 归档与提示下一步）

## 关联

- 被 Agent 读取以了解当前工作重心
- 由 `harness/tasks/active/` 中的任务驱动阶段演进
