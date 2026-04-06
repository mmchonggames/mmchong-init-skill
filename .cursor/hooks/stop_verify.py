#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stop hook：任务结束时
1) 运行 scripts/verify/large_py_files.py --fail-on-over --lines 500，禁止存在超过 500 行的 .py；
2) 对工作区中已修改的 .py，检查其所在目录是否存在 index.md（与 AGENTS.md 目录文档约定一致）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Set


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "scripts" / "verify" / "large_py_files.py").is_file():
            return parent
    return p.parents[2]


def _git_changed_paths(root: Path) -> Set[str]:
    """已跟踪文件的未提交变更 + 未跟踪文件（相对仓库根的路径）。"""
    out: Set[str] = set()
    for cmd in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            line = line.strip()
            if line:
                out.add(line)
    return out


def _should_check_index(py_rel: str) -> bool:
    parts = py_rel.split("/")
    if parts[0] in (
        ".cursor",
        ".git",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
    ):
        return False
    if py_rel.startswith("harness/memory/"):
        return False
    return py_rel.endswith(".py")


def _index_missing_for_py(root: Path, py_rel: str) -> str | None:
    p = (root / py_rel).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None
    if not p.is_file():
        return None
    parent = p.parent
    idx = parent / "index.md"
    if idx.is_file():
        return None
    return f"{py_rel} -> missing {idx.relative_to(root)}"


def _run_large_py_check(root: Path) -> int:
    script = root / "scripts" / "verify" / "large_py_files.py"
    if not script.is_file():
        print("stop_verify: large_py_files.py not found", file=sys.stderr)
        return 1
    return subprocess.call(
        [
            sys.executable,
            str(script),
            "--fail-on-over",
            "--lines",
            "500",
            "--no-guidance",
        ],
        cwd=root,
    )


def main() -> int:
    root = _repo_root()
    os.chdir(root)

    rc = _run_large_py_check(root)
    if rc == 2:
        print(
            "stop_verify: 存在超过 500 行的 Python 文件，请先拆分或调整阈值策略。",
            file=sys.stderr,
        )
        return 2
    if rc != 0:
        print("stop_verify: large_py_files 执行失败", file=sys.stderr)
        return rc

    changed = _git_changed_paths(root)
    problems: list[str] = []
    for rel in sorted(changed):
        if not _should_check_index(rel):
            continue
        msg = _index_missing_for_py(root, rel)
        if msg:
            problems.append(msg)

    if problems:
        print("stop_verify: 以下已修改 .py 所在目录缺少 index.md：", file=sys.stderr)
        for m in problems:
            print(f"  {m}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
