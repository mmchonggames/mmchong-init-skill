# mmchong.ai - AI Micro-SaaS 项目

## 项目概述

**一句话定位：** AI Micro-SaaS，作为 **AI 能力基座平台** 对外提供服务；上层业务（含多模态生成等）均建立在该基座之上。

### 整体定位

mmchong.ai 是一个 **AI 微服务型产品**：底层是统一的能力与商业化支撑，而不是「单一功能页面即产品本身」。平台负责把 **AI 能力** 以可计量、可订阅的方式交付；各类 **功能页面** 是在基座上 **生长出来的增值能力**，用于承载具体场景与体验，但不改变「先平台、后场景」的层次关系。

### 核心工作目的

平台的 **首要目标** 是支撑后续 **用户订阅 AI 能力与信用点（额度）消费** 的闭环——即身份、计费、额度、履约与可追溯使用的 **核心支撑系统**。研发与架构决策应优先服务于：用户能稳定注册与鉴权、能购买/续订服务、能按规则消耗与补充信用点，并能支撑运营侧需要的商业化能力（含 **付费推广 / 广告** 等增长与变现相关能力）。

### 主要功能范畴（基座侧）

- **用户与身份：** 注册、登录、会话与权限（与 Supabase Auth 等体系衔接）。
- **订阅与商业化：** 套餐、订阅生命周期、支付与账单相关能力。
- **信用点与 AI 能力交付：** 将上游模型能力（如 MiniMax 多模态）封装为可调用、可计量的服务，并与额度扣减、风控策略对齐。
- **增长与变现支持：** 付费广告等 **非核心创作流程** 但属于平台商业闭环的能力，在基座层预留或实现统一接入。

### 与「功能页面」的关系

**连续像素瓦片生成** 等具体能力，是基座之上的一种 **典型应用场景**（通过多模态模型与产品化页面交付），而非平台的唯一定义。新增页面或垂直功能时，应复用同一套账户、订阅与信用点体系，避免在业务层重复造「商业化与身份」轮子。

## 技术栈

- **包管理：** pnpm + turbo
- **前端：** Next.js 16
- **图标：** [Lucide](https://lucide.dev/packages)（`lucide-react`）— UI 与 `apps/web` 内文案/描述 **禁止使用 emoji**，请用 Lucide 图标组件表达；提交前由 `scripts/check-web-no-emoji.mjs`（pre-commit）校验暂存文件
- **后端：** Fastify 5
- **ORM：** Prisma
- **AI 接入：** MiniMax Facade
- **认证：** Supabase Auth

## 目录结构

```
mmchong.ai/
├── apps/
│   ├── api/          # Fastify 后端 API 服务
│   └── web/          # Next.js 前端应用
├── packages/
│   └── shared/       # 共享类型、工具、SDK
├── harness/          # Agent 记忆与任务系统
│   ├── memory/       # 长期记忆与每日日志
│   ├── tasks/        # 任务管理（active/backlog/completed）
│   ├── trace/        # 执行追踪记录
│   └── context/      # 当前上下文状态
└── docs/             # 项目文档（开发指南、设计文档、邮件模板等）
```

## 快速开始

```bash
pnpm install && pnpm dev
```

## 当前阶段

**Phase 1：** 身份与基座打通 — Supabase Auth + MiniMax 多模态接入 + 可扩展的 API / Web 骨架

当前阶段重点任务：
1. 集成 Supabase Auth，使用户注册、登录与鉴权成为后续 **订阅与信用点** 的基础。
2. 接入 MiniMax 多模态 API（文本、图像等），作为 **可计量 AI 能力** 的一条主干实现路径。
3. 搭建基础 API 路由与 Web 前端框架，使 **功能页面** 能作为基座上的模块持续迭代，而不与「账户 / 订阅 / 额度」核心链路耦合。

## 活跃任务

当前活跃任务请查看：[harness/tasks/active/](harness/tasks/active/)

## 相关链接

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构文档
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - 开发指南
- [harness/memory/](harness/memory/) - 项目记忆

## 文档维护规则

**核心原则：代码与文档必须保持一致。**

当修改代码后，必须对应维护该文件夹内的 `index.md` 文档描述。具体规则如下：

### 规则 1：同步更新
修改代码后，立即检查并更新对应文件夹的 `index.md`，确保以下内容与代码实际相符：
- 该文件夹的用途描述
- 核心文件和子文件夹的说明
- 关键的引用关系

### 规则 2：递归向上维护
如果修改后的代码与 `index.md` 内容有冲突，必须依次递归向上维护所有涉及的父级 `index.md` 文件：
1. 先更新当前文件夹的 `index.md`
2. 再检查并更新父级文件夹的 `index.md`（如 `apps/index.md`、`apps/api/index.md` 等）
3. 递归直到根目录的 `index.md`

### 规则 3：一致性检查
完成代码修改后，确认以下层级保持逻辑一致：
- 当前文件夹 `index.md` — 描述最新状态
- 所有父级 `index.md` — 层层向上同步
- `harness/memory/MEMORY.md` — 如有重大架构变更，同步更新长期记忆

### 示例流程
1. 在 `apps/api/src/models/minimax/` 中新增 `image.ts`
2. 更新 `apps/api/src/models/minimax/index.md`，补充新文件说明
3. 检查 `apps/api/src/models/index.md`，确认新增内容已反映
4. 检查 `apps/api/src/index.md`，确认 models 模块描述一致
5. 递归向上，确认 `apps/api/index.md`、`apps/index.md` 同步

## 架构分层规则

**核心原则：低层级文件不能引用高层级文件，依赖顺序从低层向高层发展。**

本项目采用五层架构，每层只能引用自身及更低层级的模块：

### 分层定义

| 层级 | 名称 | 说明 | 依赖范围 |
|------|------|------|---------|
| **Layer 0** | types/ | 纯类型定义，无内部依赖 | 仅自身 |
| **Layer 1** | utils/ | 工具函数，仅依赖 Layer 0 | Layer 0 |
| **Layer 2** | config/ | 配置层，依赖 Layer 0-1 | Layer 0-1 |
| **Layer 3** | core/services/ | 业务逻辑层，依赖 Layer 0-2 | Layer 0-2 |
| **Layer 4** | api/ cli/ ui/ | 接口层，依赖 Layer 0-3，**彼此不互相引用** | Layer 0-3 |

### 依赖方向

```
Layer 4 (api/ cli/ ui/)  ──引用──▶  Layer 3 (core/services/)
                                                      │
                                              Layer 2 (config/)
                                                      │
                                              Layer 1 (utils/)
                                                      │
                                              Layer 0 (types/)
```

### 规则说明

- **Layer 0**：`packages/shared/src/types/` — 纯 TypeScript 类型定义，不引用任何其他层
- **Layer 1**：`packages/shared/src/utils/` — 工具函数，仅依赖 Layer 0 的类型
- **Layer 2**：`packages/shared/src/config/` — 配置模块，依赖 Layer 0-1
- **Layer 3**：`apps/api/src/core/`、`apps/api/src/services/` — 业务逻辑，依赖 Layer 0-2
- **Layer 4**：`apps/api/`、`apps/web/` — 接口层（Fastify API、Next.js UI），依赖 Layer 0-3，**api 与 web 互不引用**

### 强制检查

使用 `pnpm lint:arch` 或 `scripts/lint_deps.py` 进行静态检查，禁止跨层引用：
- utils/ 不得 import handlers/、scrapers/、threads/
- packages/shared/ 不得 import apps/api/、apps/web/
- apps/api/src/ 不得 import apps/web/src/

## 构建与质量标准

### 构建命令

```bash
pnpm install          # 安装依赖
pnpm check:web-no-emoji  # 扫描 apps/web，禁止 emoji（与 pre-commit 一致）
pnpm build            # 构建所有包
pnpm dev              # 开发模式
pnpm test             # 运行测试
pnpm lint             # 运行 lint
pnpm lint:arch        # 运行架构 lint（跨层依赖检查）
pnpm validate         # 统一验证（tsc → lint → test）
```

### 质量标准

| 标准 | 规则 |
|------|------|
| **日志** | 结构化日志（pino），禁止 `console.log` / `console.error` |
| **单文件行数** | 不超过 500 行 |
| **命名规范** | PascalCase（类型）、camelCase（函数/变量）、kebab-case（文件名） |
| **提交规范** | feat/fix/docs/refactor/chore 前缀，参考 [Conventional Commits](https://www.conventionalcommits.org/) |
| **前端图标与符号** | 使用 `lucide-react`（[Lucide 图标库](https://lucide.dev/packages)）；`apps/web` 源码与前端相关文案 **禁止 emoji**（`pnpm check:web-no-emoji` / pre-commit） |

### 架构检查

```bash
# 跨层依赖检查（ESLint import/no-restricted-paths）
pnpm lint:arch

# 完整验证管道
pnpm validate
```
