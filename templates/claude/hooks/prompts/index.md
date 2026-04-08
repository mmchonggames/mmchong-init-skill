# hooks/prompts

Claude **SessionStart** 与 **PreCompact** 钩子提示词 Markdown。

## 核心文件

- `session_start.md` — 会话启动时读取 AGENTS.md / index.md / BOOTSTRAP.md 的提示词
- `precompact_memory.md` — 上下文压缩前的记忆编辑提示词

## 关联

- [../settings.json](../settings.json) — 钩子配置，prompt 内容应与此目录保持同步
