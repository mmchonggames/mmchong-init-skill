# scripts

本目录为 **mmchong-init** 分发的自动化脚本包。合并到目标仓库时，请将 **`scripts-bundle/` 下全部内容** 复制到目标仓库根目录的 **`scripts/`**（保持子目录 `verify/`、`hooks/`）。

## 主要内容

- `analyze-logs.sh` — 结构化日志分析（依赖 `jq`）
- `validate.sh` — Bash 验证管道
- `validate.py` — Python 统一验证管道（可按目标仓库裁剪）
- `lint-deps.py` — 跨层依赖违规检查（TypeScript/JavaScript）
- `lint-quality.py` — 命名、`console`、行数等质量检查
- `check-web-no-emoji.mjs` — `apps/web` 路径下禁止 emoji（依赖根目录 `emoji-regex`）
- `verify/large_py_files.py` — Python 文件行数门禁
- `hooks/pre-commit` — Git pre-commit 示例（**需按目标仓库调整** turbo filter、测试命令等）

## 关联

- `.cursor/hooks/stop_verify.py` 会调用 `scripts/verify/large_py_files.py`；请先保证本目录已就位
- 根目录 `package.json` 可添加 `prepare` 将 `scripts/hooks/pre-commit` 安装到 `.git/hooks/pre-commit`（参见 mmchong.ai 根 `package.json`）
