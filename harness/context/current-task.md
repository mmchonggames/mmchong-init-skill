# 当前认领任务

Agent 从 `harness/tasks/active/` 认领任务时，将下方 `active_task_id` 设为**不带 `.md` 后缀**的任务 ID（与 `task-<id>.md` 文件名一致）。`stop` hook 会据此判断是否与 active 中某一文件对应，并提示下一步或自动归档。

---

active_task_id: none
