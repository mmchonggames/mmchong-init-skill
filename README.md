# mmchong-init

从 **mmchong.ai** 抽取并维护的 **项目治理与脚手架素材库**：文档模板（`AGENTS.md`、层级 `index.md`）、`.cursor` hooks 模板、`harness` 骨架、校验脚本与 Git pre-commit 约定，用于在新仓库中快速对齐同一套规范。

## 目录一览

| 路径 | 说明 |
|------|------|
| [scripts-bundle/](./scripts-bundle/) | 可整体复制到目标仓库 `scripts/` 的校验与 pre-commit |
| [templates/](./templates/) | `cursor/`、`harness-skeleton/`、`AGENTS.example.md`、`ROOT_INDEX.example.md` |
| [install/apply-to-repo.sh](./install/apply-to-repo.sh) | 将上述内容应用到任意目标 git 仓库 |
| [skill/SKILL.md](./skill/SKILL.md) | Cursor Skill **`mmchong-init`**（可复制到 `~/.cursor/skills/mmchong-init/`） |
| [PROJECT_PLAN.md](./PROJECT_PLAN.md) | 里程碑与风险 |

## 本仓库自身（开发 mmchong-init 时）

在仓库根目录执行一次 `npm install`（安装 `emoji-regex` 供 `check-web-no-emoji.mjs` 使用，并通过 `prepare` 安装 Git pre-commit）。治理文件入口：**[AGENTS.md](./AGENTS.md)**、**[index.md](./index.md)**。可将 `skill/SKILL.md` 同步到 `~/.cursor/skills/mmchong-init/`，或使用项目内 **`.cursor/skills/mmchong-init/`**。

## 快速使用（对外分发）

在 **本仓库根目录** 执行：

```bash
./install/apply-to-repo.sh /path/to/target-repo
```

然后按 `templates/README.md` 与 `skill/SKILL.md` 中的说明改写目标仓库的 `AGENTS.md`；若目标为 monorepo，请在 `scripts/hooks/pre-commit` 中追加构建、lint 与测试步骤。

## 仓库

- 默认分支：`main`
- 详细里程碑：见 [PROJECT_PLAN.md](./PROJECT_PLAN.md)

## 源项目

素材与约定来源于同级目录下的 [mmchong.ai](../mmchong.ai) monorepo。
