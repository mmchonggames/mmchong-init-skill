# scripts

本目录为 **mmchong** 分发给消费者仓库的自动化脚本包（复制到目标仓库根目录的 **`scripts/`**）。**在 mmchong 仓库自身**中，根目录 **`scripts-bundle/`** 为单一来源，本目录由 `./install/apply-to-repo.sh "$(pwd)"` 同步，便于本地跑 hooks 与校验。

## 主要内容

- `analyze-logs.sh` — 结构化日志分析（依赖 `jq`）
- `validate.sh` — Bash 验证管道
- `validate.py` — Python 统一验证管道（可按目标仓库裁剪）
- `lint-deps.py` — 跨层依赖违规检查（TypeScript/JavaScript）
- `lint-quality.py` — 命名、`console`、行数等质量检查
- `check-web-no-emoji.mjs` — `apps/web` 路径下禁止 emoji（依赖根目录 `emoji-regex`）
- `verify/large_py_files.py` — Python 文件行数门禁
- `hooks/pre-commit` — 默认 **轻量** Git pre-commit；monorepo 请自行追加 turbo / lint / test

## 关联

- `.cursor/hooks/stop_verify.py` 会调用 `scripts/verify/large_py_files.py`；请先保证本目录已就位
- 根目录 `package.json` 的 `prepare` 可将 `scripts/hooks/pre-commit` 安装到 `.git/hooks/pre-commit`
