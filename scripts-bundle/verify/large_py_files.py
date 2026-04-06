#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
large_py_files.py — 扫描仓库内 Python 源文件行数，标记超过阈值的文件。

本脚本只读文件系统。默认阈值 500 行（与 AGENTS.md 质量标准一致），可用 --lines 调整。

设计背景（mmchong）
---------------------
- 主业务在 `apps/api`（Fastify）、`apps/web`（Next.js）与 `packages/shared`（TypeScript）。
- Python 集中在 `scripts/` 与 `.cursor/hooks/`，用于验证、lint 编排与健康检查。
- 本工具用于盘点「优先拆分候选」，可与 `harness/tasks` 或技术债记录对照。

用法示例
--------
  python scripts/verify/large_py_files.py
  python scripts/verify/large_py_files.py --lines 400 --exclude-tests
  python scripts/verify/large_py_files.py --json
  python scripts/verify/large_py_files.py --fail-on-over; echo $?

退出码
------
  0 — 无超出阈值，或未加 --fail-on-over
  2 — 存在超出阈值且指定了 --fail-on-over
  1 — 参数错误或其它错误
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

# 默认排除：常见非业务或生成物目录名（小写比较）
DEFAULT_EXCLUDE_DIR_NAMES: Tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".turbo",
    "coverage",
)

# 与本仓库相关的拆分提示（键为 posix 相对路径；仅供参考）
SPLIT_GUIDANCE: Dict[str, str] = {
    "scripts/validate.py": """
编排脚本过长时：
- 将各 step 抽到 scripts/validate/ 下按步骤分模块，validate.py 仅保留调度与退出码。
- 环境变量开关与打印格式可集中到 validate_output.py 之类的小模块。
""",
    "scripts/lint-deps.py": """
可将「解析配置」「遍历 import」「报告格式」拆成子模块，主文件保留 CLI。
""",
    "scripts/lint-quality.py": """
可将单类检查（如 compileall、ruff）拆成独立函数文件，主入口只做列表驱动。
""",
    "scripts/verify/health-check.py": """
HTTP 探活、超时与 JSON 解析可分层；多环境 URL 列表可独立配置模块。
""",
    ".cursor/hooks/stop_verify.py": """
可将 INDEX.md 检查与 large_py 调用拆成两个函数文件，由主入口顺序调用。
""",
    ".cursor/hooks/stop_task_harness.py": """
任务解析、index 重写、归档移动可拆模块；主流程保持线性易读。
""",
}

SHORT_APPENDIX = """
--------------------------------------------------------------------------------
与本仓库文档 / 命令的对应关系
--------------------------------------------------------------------------------
- 质量标准：仓库根目录 AGENTS.md（单文件行数建议）。
- 架构分层：docs/ARCHITECTURE.md；跨层依赖：pnpm lint:arch 或 scripts/lint-deps.py。
- 统一验证：pnpm validate 或 python scripts/validate.py。
- 目录索引：业务目录维护 index.md（本仓库 Python 脚本目录见 scripts/verify/index.md）。
--------------------------------------------------------------------------------
"""


def _parse_exclude_patterns(raw: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = list(DEFAULT_EXCLUDE_DIR_NAMES)
    if raw:
        out.extend(raw)
    return out


def _should_skip_dir(name: str, extra_exclude: Sequence[str]) -> bool:
    n = name.lower()
    for pat in extra_exclude:
        if pat.startswith("*") and pat.endswith("*"):
            core = pat.strip("*")
            if core and core in n:
                return True
        elif n == pat.lower().rstrip("/"):
            return True
    return False


def iter_py_files(
    root: Path,
    *,
    extra_exclude: Sequence[str],
    exclude_tests: bool,
) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        kept: List[str] = []
        for d in sorted(dirnames):
            if _should_skip_dir(d, extra_exclude):
                continue
            if exclude_tests and d.lower() == "tests":
                continue
            kept.append(d)
        dirnames[:] = kept

        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            yield Path(dirpath) / fn


@dataclass
class FileStat:
    path: str
    lines: int
    over: bool


def count_lines(path: Path) -> int:
    data = path.read_bytes()
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def collect_stats(
    root: Path,
    *,
    threshold: int,
    extra_exclude: Sequence[str],
    exclude_tests: bool,
) -> List[FileStat]:
    stats: List[FileStat] = []
    for py in sorted(iter_py_files(root, extra_exclude=extra_exclude, exclude_tests=exclude_tests)):
        try:
            n = count_lines(py)
        except OSError as e:
            print(f"warn: skip {py}: {e}", file=sys.stderr)
            continue
        rel = py.relative_to(root).as_posix()
        stats.append(FileStat(path=rel, lines=n, over=n > threshold))
    return stats


def print_text_report(stats: Sequence[FileStat], threshold: int, show_guidance: bool) -> List[FileStat]:
    over = [s for s in stats if s.over]
    over.sort(key=lambda x: -x.lines)
    print(f"Root: {os.getcwd()}")
    print(f"Threshold: {threshold} lines (physical line count)")
    print(f"Scanned .py files: {len(stats)}")
    print()
    if not over:
        print("No files exceed the threshold.")
        return []
    print(f"Files OVER threshold ({len(over)}):")
    print("-" * 72)
    for s in over:
        print(f"  {s.lines:5d}  {s.path}")
    print("-" * 72)
    if show_guidance:
        print()
        print("Split guidance (see SPLIT_GUIDANCE in script; informational only):")
        for s in over:
            key = s.path
            if key in SPLIT_GUIDANCE:
                print()
                print(f"--- {key} ---")
                print(SPLIT_GUIDANCE[key].strip())
    return list(over)


def print_json_report(stats: Sequence[FileStat], threshold: int) -> None:
    payload = {
        "threshold": threshold,
        "files": [asdict(s) for s in stats],
        "over_threshold": [asdict(s) for s in stats if s.over],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="List Python files whose physical line count exceeds a threshold.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  %(prog)s\n  %(prog)s --lines 400 --exclude-tests\n  %(prog)s --json",
    )
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/verify, i.e. project root)",
    )
    p.add_argument("--lines", type=int, default=500, metavar="N", help="Line threshold (default: 500)")
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="DIR",
        help="Additional directory name to exclude (repeatable). Applied to any path component.",
    )
    p.add_argument(
        "--exclude-tests",
        action="store_true",
        help="Skip any directory named 'tests' entirely",
    )
    p.add_argument("--json", action="store_true", help="Print JSON instead of text")
    p.add_argument(
        "--no-guidance",
        action="store_true",
        help="Do not print SPLIT_GUIDANCE blocks for known paths",
    )
    p.add_argument(
        "--fail-on-over",
        action="store_true",
        help="Exit with code 2 if any file exceeds threshold",
    )
    p.add_argument(
        "--print-appendix",
        action="store_true",
        help="Print short maintenance appendix and exit (no scan)",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    if args.print_appendix:
        print(SHORT_APPENDIX.strip())
        return 0

    root = args.root
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = root.resolve()
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 1

    os.chdir(root)
    extra = _parse_exclude_patterns(args.exclude)

    stats = collect_stats(
        root,
        threshold=args.lines,
        extra_exclude=extra,
        exclude_tests=args.exclude_tests,
    )

    if args.json:
        print_json_report(stats, args.lines)
        over = [s for s in stats if s.over]
    else:
        over = print_text_report(stats, args.lines, show_guidance=not args.no_guidance)

    if args.fail_on_over and over:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
