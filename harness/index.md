# harness

Agent 记忆和工作流目录，为 AI Agent 提供上下文管理、任务追踪和执行日志能力。

## 主要内容

- `memory/` — 长期记忆文件（MEMORY.md + 每日日志）
- `tasks/` — 任务管理（active/backlog/completed 三层队列）
- `trace/` — 执行追踪日志（按月分目录）
- `context/` — 当前阶段上下文

## 关联

- `memory/MEMORY.md` 是项目长期记忆中枢，记录技术决策和架构演进
- `tasks/` 目录支持 Agent 任务委派和状态流转
