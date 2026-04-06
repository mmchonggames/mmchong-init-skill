---
name: mmchong-init
description: >-
  Applies mmchong-style project governance from the mmchong-init bundle: AGENTS.md
  and hierarchical index.md conventions, Cursor hooks under .cursor/, harness/
  task/memory layout, validation scripts under scripts/, and git pre-commit wiring.
  Use when bootstrapping a repo, syncing governance from mmchong-init, installing
  Cursor stop/session hooks, or when the user mentions mmchong-init, harness
  tasks, index.md per-folder docs, or pre-commit validation scripts.
---

# mmchong-init

## When to use

- 用户希望 **按 mmchong 约定** 初始化或补强仓库：根目录 `AGENTS.md`、层级 `index.md`、**harness** 目录、**`.cursor/hooks`**、**`scripts/`** 校验与 **pre-commit**。
- 用户提到从 **mmchong-init** 仓库复制模板、对齐文档与门禁规则，或处理 **`BOOTSTRAP.md` 首次初始化**。

## Canonical source

素材以独立仓库维护（与本技能同名）：路径示例为与 `mmchong.ai` 同级的 **`mmchong-init`**。业务仓库是 **消费者**：以该仓库的 `scripts-bundle/`、`templates/` 为单一来源，按需同步。

## 新 clone 之后（mmchong-init 本仓库）

在 **mmchong-init** 仓库根目录执行 **`npm install`** 一次：

- 安装 **`emoji-regex`**（`scripts/check-web-no-emoji.mjs` 依赖）。
- 触发根目录 **`package.json` 的 `prepare`**，将 `scripts/hooks/pre-commit` 复制到 **`.git/hooks/pre-commit`** 并赋予可执行权限；否则提交前校验与 README 约定不会自动生效。

Agent 在本仓库内操作脚本或协助用户提交前，若发现 `node_modules/` 不存在或 pre-commit 未安装，应提示或代为执行上述命令。

## Steps (agent)

1. **确认目标**：是新仓库脚手架，还是在现有仓库中增量添加 hooks/scripts/harness。
2. **读取** 目标仓库是否已有 `AGENTS.md`、根 `index.md`、`harness/`、`.cursor/`、`scripts/`；避免不经确认覆盖非空目录（尤其 `harness/`、`scripts/hooks/pre-commit`）。
3. **应用文件**（二选一）：
   - 在 **mmchong-init** 仓库中执行：`install/apply-to-repo.sh <目标仓库路径>`，将 `scripts-bundle` 复制为 `<target>/scripts/`，将 `templates/cursor` 复制为 `<target>/.cursor/`，若不存在则复制 `templates/harness-skeleton` 为 `<target>/harness/`，并在目标 **尚无** `BOOTSTRAP.md` 时复制 `templates/BOOTSTRAP.md` 到目标根目录。
   - 或手工复制：`mmchong-init` 内对应目录 → 目标仓库（见下表）。
4. **文档与首次初始化**：若目标为 **新项目** 或根目录存在 **`BOOTSTRAP.md`**，优先按该文件引导用户确认项目内容、技术栈与目录，再据此将 `templates/AGENTS.example.md`、`templates/ROOT_INDEX.example.md` 改写为根目录 **`AGENTS.md`**、**`index.md`**；全部确认后可删除 **`BOOTSTRAP.md`**。根目录保留 **`index.md`（小写）** 与 **`AGENTS.md`** 的约定。
5. **依赖**：**mmchong-init 本仓库** 见上文「新 clone 之后」的 **`npm install`**；其他目标仓库若复制了 `check-web-no-emoji.mjs`，同样需要根目录安装 `emoji-regex`（或等价包管理器）。Python 脚本建议 3.10+；`lint-deps.py` / `validate.py` 面向 **pnpm + turbo** monorepo，小项目需删减或改环境变量跳过项。
6. **Git hooks**：将 `scripts/hooks/pre-commit` 安装到 `.git/hooks/pre-commit`（可参考 mmchong.ai 根目录 `package.json` 的 `prepare` 脚本）；**务必按目标仓库** 调整 turbo filter、测试与构建命令。
7. **Cursor**：`templates/cursor/hooks.json` 中 `sessionStart` / `preCompact` 与 `hooks/prompts/` 下 Markdown 应保持语义同步；修改 prompt 时先改 Markdown，再同步到 `hooks.json`。

## Layout reference

| mmchong-init 内路径 | 目标仓库路径 |
|---------------------|----------------|
| `scripts-bundle/*` | `scripts/` |
| `templates/cursor/hooks.json` | `.cursor/hooks.json` |
| `templates/cursor/hooks/` | `.cursor/hooks/` |
| `templates/harness-skeleton/` | `harness/`（可选） |
| `templates/BOOTSTRAP.md` | `BOOTSTRAP.md`（目标根目录；`apply-to-repo.sh` 仅在目标无此文件时复制） |

## Install this skill (user)

- **个人全局**：将本仓库的 `skill/` 目录复制为 `~/.cursor/skills/mmchong-init/`（内含本 `SKILL.md`）。
- **仅当前项目**：复制为 `<repo>/.cursor/skills/mmchong-init/SKILL.md`（若 Cursor 版本支持项目级 skills）。

## Stop hook 与 index 约定

- `stop_verify.py` 使用各目录的 **`index.md`（小写）** 与 `scripts/verify/large_py_files.py`；业务以 **TypeScript 为主** 时，pre-commit 中的 index 检查以 shell 脚本为准（见 `scripts/hooks/pre-commit`）。
- `stop_task_harness.py` 依赖 `harness/context/current-task.md` 中的 `active_task_id` 与 `harness/tasks/active/task-*.md`。

## 验证

在 **mmchong-init** 本仓库中，若尚未安装 Node 依赖，先执行 **`npm install`**，再运行：

```bash
node scripts/check-web-no-emoji.mjs
python3 scripts/verify/large_py_files.py --fail-on-over --lines 500 --no-guidance
```

在 **其他** 目标仓库中（按实际脚本调整）：

```bash
python3 scripts/lint-deps.py
node scripts/check-web-no-emoji.mjs
```

完整 monorepo 可参考源项目中的 `pnpm validate` 组合。
