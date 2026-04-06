# mmchong — 项目规划

本仓库用于维护一套 **可复用的项目骨架与治理工具包**，目标是从 **上游参考仓库** 中抽象出：文档约定、目录索引（`index.md`）、Cursor Hooks、`harness` 工作流、校验脚本与 Git 预提交流程，便于在新仓库中 **复制 / 脚手架化** 落地，并可选地配套 **Cursor Skill** 供 Agent 按规范初始化或校验项目。

---

## 1. 背景与目标

| 维度 | 说明 |
|------|------|
| **问题** | 多项目重复维护 `AGENTS.md`、层级 `index.md`、`.cursor/hooks`、脚本与 pre-commit，易漂移、难一致。 |
| **目标** | 单一来源（本仓库）维护 **模板 + 脚本 + 文档规则**，通过「复制 bundle」或「init 命令」同步到其他项目；Skill 负责 **告知 Agent 放什么、改什么、跑什么命令**。 |
| **非目标** | 不替代各业务仓库的业务代码；不强制统一技术栈细节（仅提供可裁剪的默认项）。 |

---

## 2. 从上游参考仓库可抽取的资产清单

### 2.1 根与 Agent 文档

- **`AGENTS.md`**：项目定位、技术栈、目录树、文档维护规则（`index.md` 递归）、五层架构与 `lint:arch`、构建与质量标准（单文件行数、无 `console.log`、emoji 策略等）。
- **根目录 `index.md`**：与 `AGENTS.md` 互补的「一级目录职责 + 技术栈表 + 快速开始」；新仓库可二选一或合并为单一入口，但需约定 **唯一主入口** 避免重复。

**规划动作**：提供 `templates/AGENTS.md.tpl`、`templates/ROOT_INDEX.md.tpl`，占位符：`{{PROJECT_NAME}}`、`{{ONE_LINE_PITCH}}`、`{{STACK_TABLE}}`。

### 2.2 层级 `index.md` 约定

当前实践中大量目录带有 `index.md`，用于说明该目录用途、核心文件与引用关系（见 `AGENTS.md` 文档维护规则）。

**规划动作**：

- 整理 **最小模板族**：`folder-index-minimal.md`（通用）、可选 `apps-api-src.md`、`apps-web-src.md`、`harness.md` 等。
- Skill / 文档中明确：**改代码则更新本目录及向上父级 `index.md`** 的判定规则（与现有 pre-commit 逻辑对齐）。

### 2.3 `.cursor/`（Hooks 与提示）

现有结构（参考）：

- `.cursor/hooks.json` — `sessionStart` / `preCompact` / `stop` 等。
- `.cursor/hooks/stop_verify.py`、`stop_task_harness.py` — stop 时校验。
- `.cursor/hooks/prompts/*.md` — 会话提示。

**注意**：当前 `hooks.json` 内部分 prompt 仍残留其他项目名（如 *info-scraper*），迁移时应 **参数化仓库名与必读文件路径**（例如统一读 `AGENTS.md` + 根 `index.md`，若项目使用 `INDEX.md` 则二选一并写清）。

**规划动作**：`templates/cursor/hooks.json.tpl` + 脚本清单；可选提供 `apply-cursor-hooks.sh` 将模板写入目标仓库。

### 2.4 `harness/` 结构

职责：Agent 记忆、任务队列（active/backlog/completed）、trace、context（见 `harness/index.md`）。

**规划动作**：

- 提供 **空骨架目录** 与每个子目录的 `index.md` 模板 + 示例 `MEMORY.md` 片段（不含业务内容）。
- 约定与 Cursor/OpenClaw 等工具链的 **可选** 集成说明（本包只保证目录与文档一致）。

### 2.5 校验脚本（可集中到 `bundle/`）

| 资产 | 作用 |
|------|------|
| `scripts/check-web-no-emoji.mjs` | 前端路径 emoji 检查（可与 pre-commit `--staged` 配合） |
| `scripts/lint-deps.py` | 架构跨层依赖检查 |
| `scripts/lint-quality.py` | 代码质量辅助（若 pre-commit 未全量引用，可作为可选） |
| `scripts/validate.sh` / `validate.py` | 聚合验证入口 |
| `scripts/hooks/pre-commit` | 安装到 `.git/hooks/pre-commit`（根 `package.json` 通过 `prepare` 复制） |

**规划动作**：

- 在本仓库中设 `packages/scripts-bundle/` 或 `dist/scripts/`：**原样 vendor** 或 **轻量 fork**（保留许可证与来源注释）。
- 提供 **`install-git-hooks.sh`**：复制 pre-commit、设置可执行位；可选 `prepare` 片段供目标 `package.json` 粘贴。
- **分层 pre-check**：区分「轻量（仅 staged + 文档）」与「完整（build + lint + test）」两套 profile，避免小项目提交过慢。

### 2.6 Git 与 pre-commit

参考实现采用：**`prepare` 将 `scripts/hooks/pre-commit` 拷入 `.git/hooks/pre-commit`**，而非强制 Husky（仓库内无 `.husky`）。

**规划动作**：

- 文档化：**Husky vs 纯 `prepare`** 两种安装方式。
- `pre-commit` 中与 monorepo 强绑定的步骤（如 `pnpm turbo build --filter=api --filter=web`）改为 **配置驱动**（`mmchong.yaml` 或环境变量）以便小项目裁剪。

---

## 3. 建议的本仓库目录结构（演进中）

```
mmchong/
├── README.md                 # 仓库说明与快速导航
├── PROJECT_PLAN.md           # 本文件
├── templates/
│   ├── AGENTS.md.tpl
│   ├── ROOT_INDEX.md.tpl
│   ├── cursor/
│   └── harness/              # 骨架 + 各 index.md
├── scripts-bundle/           # 从上游参考仓库同步的校验脚本（版本化）
├── install/                  # install-git-hooks.sh、apply-templates 等
├── skill/                    # Cursor Skill（SKILL.md + 可选资源）
└── docs/
    └── CONVENTIONS.md        # 与上游参考仓库对齐的约定摘要
```

---

## 4. Cursor Skill 设计要点（后续迭代）

- **名称（工作标题）**：如「mmchong 项目初始化与治理」。
- **触发场景**：新建仓库、补齐文档索引、安装 hooks、从旧项目迁移治理规则。
- **行为**：
  - 读取目标仓库是否已有 `AGENTS.md` / 根索引；
  - 按模板生成或增量更新层级 `index.md`；
  - 复制 `scripts-bundle` 与 pre-commit，并提示运行 `pnpm validate` 等价命令（若存在）。
- **约束**：Skill 内说明 **与上游参考仓库 / 本仓库 canonical 的同步流程**（本仓库为 canonical，业务仓库为 consumer）。

---

## 5. 分阶段实施（里程碑）

| 阶段 | 内容 | 产出 |
|------|------|------|
| **M0** | 本仓库立项、规划、git 初始化 | `PROJECT_PLAN.md`、`README.md` |
| **M1** | 从上游参考仓库 **快照复制** scripts + hooks + harness 骨架到 `scripts-bundle/`、`templates/` | **已完成**：`scripts-bundle/`、`templates/cursor`（含已修正文案的 `hooks.json`）、`templates/harness-skeleton/`、`templates/*.example.md`、`install/apply-to-repo.sh`、`skill/SKILL.md`（技能名 **`mmchong`**） |
| **M2** | 参数化模板（项目名、路径、pre-commit profile） | `*.tpl` + 一份示例 `mmchong.config.example.yaml` |
| **M3** | 安装脚本与文档（install hooks、校验清单） | `install/*.sh` + `docs/CONVENTIONS.md` |
| **M4** | Cursor `skill/`：`SKILL.md` + 资源路径 | 可在 Cursor 中加载的 Skill |
| **M5** | （可选）CLI：`npx mmchong` 或本地 `pnpm dlx` 发布 | 降低复制成本 |

---

## 6. 风险与决策记录

- **仓库名残留**：迁移任何来自 `.cursor` 的 prompt 时必须全文检索旧项目名。
- **pre-commit 过重**：默认完整校验可能拖慢提交；需提供「仅文档 + emoji + 行数」的轻量 profile。
- **index.md 与 INDEX.md**：本模板默认小写 `index.md`；若其他项目已用 `INDEX.md`，需在 Skill 与模板中 **二选一并全局一致**。

---

## 7. 与源仓库的关系

- **上游参考仓库**：本地路径因环境而异；与 **本仓库** 通常置于同一父目录便于对照与同步。
- **本仓库**（本地路径示例）：`/Users/liusong/Documents/04_self_project/17_mmchong/mmchong-init`
- 更新流程建议：在上游参考仓库中验证规则变更 → 同步到 mmchong → 版本打 tag（如 `v0.1.0-scripts`）。

---

*文档版本：与仓库初始化同步创建，可随里程碑修订。*
