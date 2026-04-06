# mmchong-init

可复用的 **治理与脚手架** 仓库：维护 `AGENTS.md` / 层级 `index.md` 约定、Cursor Hooks、`harness` 骨架、`scripts-bundle` 与 Git pre-commit 模板；通过 `install/apply-to-repo.sh` 将同一套文件应用到任意目标仓库，**本仓库已对自身执行该流程** 以便本地验证与迭代。

## 技术栈

| 类别 | 说明 |
|------|------|
| 脚本 | Python、Bash、Node（`check-web-no-emoji.mjs`） |
| 依赖 | 根目录 `npm install` 安装 `emoji-regex`；无前端应用目录时 emoji 检查对全仓库扫描为空集即通过 |
| 版本控制 | Git；`prepare` 脚本将 `scripts/hooks/pre-commit` 安装到 `.git/hooks/` |

## 一级目录职责

- **`scripts-bundle/`** — 复制到消费者仓库 `scripts/` 的权威内容；本仓库的 `scripts/` 为其应用副本。
- **`templates/`** — `cursor/`、`harness-skeleton/`、`AGENTS.example.md`、`ROOT_INDEX.example.md`、`BOOTSTRAP.md` 等模板。
- **`install/`** — 将 bundle 应用到目标路径的 shell 脚本。
- **`skill/`** — Cursor Skill `mmchong-init` 的源；可同步到 `~/.cursor/skills/mmchong-init/` 或本仓库 `.cursor/skills/mmchong-init/`。
- **`harness/`** — Agent 记忆、任务队列、trace、context 的空骨架。
- **`.cursor/`** — `hooks.json` 与 `hooks/`（sessionStart、preCompact、stop 校验）。

## 快速开始

```bash
git clone <本仓库 URL>
cd mmchong-init
npm install                    # 安装 emoji-regex；触发 prepare 安装 pre-commit
./install/apply-to-repo.sh /path/to/other-repo   # 对外分发时使用
```

## 关联

- 源项目约定对齐：`mmchong.ai` monorepo（路径见 [PROJECT_PLAN.md](PROJECT_PLAN.md)）。
- Agent 必读： [AGENTS.md](AGENTS.md)。
