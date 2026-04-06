# harness/tasks/active

正在执行的活跃任务存放目录。

## 主要内容

（当前无任务文件时，可将示例任务 `task-example.md` 复制为起点并删除本说明行。）

## 关联

- 由 Agent 主动认领并执行
- 完成后移动到 `completed/` 目录
- 认领时在 `harness/context/current-task.md` 中将 `active_task_id` 设为**不带 `.md` 后缀**的任务 ID（与 `task-<id>.md` 文件名一致）
