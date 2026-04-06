# mmchong — Agent 导航

## 项目定位

**一句话：** 从 [mmchong 开源组织](https://github.com/mmchong) 相关实践中抽象并维护的 **项目治理与脚手架素材库**（文档约定、层级 `index.md`、Cursor Hooks、`harness`、校验脚本、Git pre-commit），供新仓库复制对齐；本仓库同时 **消费自身产出**（根目录 `scripts/`、`.cursor/`、`harness/` 由 `install/apply-to-repo.sh` 同步），便于在本仓库内迭代模板与门禁。

## 技术栈与工具

| 类别 | 说明 |
|------|------|
| 脚本 | Bash、Python 3.10+、`check-web-no-emoji.mjs`（Node，依赖 `emoji-regex`） |
| 编辑器 | Cursor（`.cursor/hooks.json` + `stop` 校验脚本） |
| 包管理 | 本仓库仅 **`package.json` + npm** 用于安装 `emoji-regex`；**无** pnpm/turbo monorepo |

## 目录结构（一级）

```
mmchong/
├── scripts-bundle/     # 分发给目标仓库的脚本 **单一来源**（复制到消费者 `scripts/`）
├── scripts/            # 与 scripts-bundle 同步的本地副本（运行 hooks、stop_verify 等）
├── templates/          # AGENTS/ROOT_INDEX 示例、BOOTSTRAP、cursor、harness-skeleton
├── BOOTSTRAP.md        # 首次初始化引导（与 templates/BOOTSTRAP.md 同源；面向业务仓库分发，本仓库维护者可删除）
├── install/            # apply-to-repo.sh 等安装脚本
├── skill/              # Cursor Skill 源文件（技能名 mmchong-init；可复制到 ~/.cursor/skills/mmchong-init/）
├── harness/            # Agent 任务/记忆骨架（与 templates/harness-skeleton 同源应用结果）
├── .cursor/            # Cursor Hooks（由 templates/cursor 应用）
├── AGENTS.md           # 本文件
├── index.md            # 根索引（与 AGENTS 互补）
├── README.md
└── PROJECT_PLAN.md     # 里程碑与风险
```

## 维护规则

1. **改 `scripts-bundle/` 后**：若需本仓库内行为与之一致，重新执行 `./install/apply-to-repo.sh "$(pwd)"` 覆盖 `scripts/`、`.cursor/`（注意 `harness/` 若已存在则跳过；仅改脚本时可只同步 `scripts/` 相关文件）。
2. **层级 `index.md`**：修改某目录下代码或脚本后，更新该目录及向上父级的 `index.md`，与 pre-commit 中的索引检查一致。
3. **Cursor prompt**：先改 `templates/cursor/hooks/prompts/*.md`，再将等价正文同步到 `templates/cursor/hooks.json` 与目标 `.cursor/hooks.json`。
4. **消费者仓库**：业务项目应将 `scripts/hooks/pre-commit` 按栈裁剪（本仓库使用 **轻量** pre-commit，无 `pnpm turbo` / 全量测试）。

## 常用命令

```bash
# 将 bundle 应用到本仓库或任意目标 git 仓库
./install/apply-to-repo.sh /path/to/target-repo

# 安装 Node 依赖（emoji 检查脚本）
npm install

# 手动安装 pre-commit（或由 package.json prepare 在安装依赖后执行）
cp scripts/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# 可选校验（按需）
node scripts/check-web-no-emoji.mjs
python3 scripts/verify/large_py_files.py --fail-on-over --lines 500
```

## 关联文档

- [index.md](index.md) — 顶层索引与目录职责
- [PROJECT_PLAN.md](PROJECT_PLAN.md) — 规划与里程碑
- [harness/memory/MEMORY.md](harness/memory/MEMORY.md) — 长期记忆（重大决策时更新）
