# 首次初始化引导（BOOTSTRAP）

> **若你正在维护 `mmchong-init` 素材库本身**：本文件面向「使用 mmchong-init 应用到**新业务仓库**」的场景；在本仓库内可忽略或删除根目录的 `BOOTSTRAP.md`。

本文件用于在 **首次** 将 mmchong 治理模板应用到仓库后，补齐 **真实项目信息**。全部确认并写入 `AGENTS.md`、`index.md` 等文档后，**删除本文件**，避免与长期文档重复。

---

## 1. 何时需要按本文件操作

在以下情况视为 **需要引导**，应优先完成本节流程再大规模写业务代码：

- 仓库是新项目，或刚从模板复制了 `AGENTS.example.md` / `ROOT_INDEX.example.md` 尚未改写；或
- 根目录仍存在本文件 `BOOTSTRAP.md`，且 `AGENTS.md` / `index.md` 中仍有明显占位符、与实际情况不符。

若项目已成熟、`AGENTS.md` 与 `index.md` 已反映真实栈与目录，可直接删除本文件。

---

## 2. Agent 与维护者协作（建议问题清单）

请 **Agent 或维护者** 先自行判断：若为「新项目 / 未填模板」，再 **向用户提问**（或对照已有资料），收齐后再落笔。建议覆盖：

| 主题 | 说明 |
|------|------|
| 项目定位 | 产品/库名称、一句话目标、主要用户或场景 |
| 技术栈 | 语言与版本、包管理器、前端/后端/移动端框架、数据库与 ORM、测试与构建工具 |
| 仓库布局 | 顶层目录职责（如 `apps/`、`packages/`、`src/` 等），与团队约定是否一致 |
| 质量与门禁 | 是否使用本仓库自带的 `scripts/`、pre-commit、Cursor hooks；是否需要删减或增补命令 |
| 文档约定 | 是否采用层级 `index.md`、长期记忆（如 `harness/memory/MEMORY.md`） |

将答案整理进 **`AGENTS.md`**（由 `templates/AGENTS.example.md` 复制改名或合并）与 **根目录 `index.md`**（由 `templates/ROOT_INDEX.example.md` 复制改写）。

---

## 3. 完成标准与收尾

- [ ] `AGENTS.md` 中项目名、概述、技术栈、目录结构、构建/验证方式已与当前仓库一致，无模板占位语。
- [ ] 根目录 `index.md` 已同步为一级目录与关联关系。
- [ ] 按需补充或删减 `scripts/hooks/pre-commit`、依赖安装方式（如 `npm install` / `pnpm install`）等说明。
- [ ] 上述确认无误后，**删除本文件 `BOOTSTRAP.md`**，并在 `AGENTS.md` 中保留或删除「首次初始化请读 BOOTSTRAP」的提示行（建议删除该提示行，避免指向已不存在的文件）。

---

## 4. 参考路径（按实际仓库调整）

- 模板来源（若在 monorepo 或本地克隆了 mmchong-init）：`templates/AGENTS.example.md`、`templates/ROOT_INDEX.example.md`
- 必读约定：根目录 `AGENTS.md`、`index.md`
