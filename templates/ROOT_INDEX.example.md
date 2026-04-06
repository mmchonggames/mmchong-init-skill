# mmchong.ai

AI Micro-SaaS 项目的 monorepo 根目录：定位为 **AI 能力基座平台**，以用户注册、订阅、信用点（额度）与商业化支撑（含付费广告等）为核心；多模态生成（如 MiniMax）与各类功能页面是基座之上生长的场景与产品能力。

## 项目概述

一个基于 Fastify + Next.js + Prisma + Supabase 的现代 AI 应用：底层优先承载身份、订阅、额度与 AI 调用履约；上层提供图片/音乐/歌词等多模态能力及各类业务页面，采用 pnpm + turbo 管理多包依赖。

## 技术栈

| 类别 | 技术 |
|------|------|
| 包管理 | pnpm + turbo |
| 前端 | Next.js 16 (App Router) + React 19；图标 [Lucide](https://lucide.dev/packages)（`lucide-react`），`apps/web` 不使用 emoji（`pnpm check:web-no-emoji`） |
| 后端 | Fastify 5 |
| ORM | Prisma |
| AI | MiniMax 多模态模型 |
| 认证 | Supabase Auth |
| 数据库 | Supabase PostgreSQL |
| 共享工具 | @mmchong/shared (pino 日志、Redis 锁、限流器) |

## 目录结构

- `apps/` — 应用层（api 后端、web 前端）
- `packages/shared/` — 跨应用共享包
- `db/` — 额外 SQL 脚本
- `docs/` — 项目文档（开发指南、设计文档、邮件模板等）
- `harness/` — Agent 记忆系统
- `scripts/` — 自动化脚本
- `tests/` — 根目录单元测试索引与覆盖说明（见 `tests/index.md`）

## 快速开始

```bash
# 安装依赖
pnpm install

# 启动开发（会先构建 workspace 依赖如 @mmchong/shared，再启动 api / web）
pnpm dev

# API 单独开发
pnpm --filter api dev

# Web 单独开发
pnpm --filter web dev
```

## 关联

- `apps/api` 依赖 `packages/shared`
- `apps/web` 依赖 `packages/shared` 和 `apps/api`
