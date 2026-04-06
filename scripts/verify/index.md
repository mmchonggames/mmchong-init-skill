# verify

Python 校验与仓库卫生检查脚本。

## 核心文件

- `large_py_files.py` — 扫描仓库内 `.py` 文件行数，可选 `--fail-on-over` 与阈值（与 `AGENTS.md` 单文件行数约定一致）

## 关联

- `.cursor/hooks/stop_verify.py` 调用本目录下的 `large_py_files.py`
