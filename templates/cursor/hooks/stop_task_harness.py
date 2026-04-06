#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stop hook（第二阶段）：根据 harness/context/current-task.md 判断是否对应
harness/tasks/active/ 中的任务；未完成则提示下一步，已完成则归档到 completed/ 并更新 index.md。
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path


ACTIVE_DIR = Path("harness/tasks/active")
COMPLETED_DIR = Path("harness/tasks/completed")
CONTEXT_TASK = Path("harness/context/current-task.md")
ACTIVE_INDEX = Path("harness/tasks/active/index.md")
COMPLETED_INDEX = Path("harness/tasks/completed/index.md")


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "harness" / "tasks").is_dir():
            return parent
    return p.parents[2]


def _parse_active_task_id(root: Path) -> str | None:
    p = root / CONTEXT_TASK
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^active_task_id:\s*(.+)$", s, re.I)
        if m:
            val = m.group(1).strip().strip("`")
            if val.lower() in ("none", "-", "null", "无"):
                return None
            return val
    return None


def _task_filename(task_id: str) -> str:
    tid = task_id.strip()
    if not tid.endswith(".md"):
        return f"{tid}.md"
    return tid


def _read_task_body(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_marked_done(content: str) -> bool:
    if re.search(r"✅\s*已完成", content):
        return True
    m = re.search(r"##\s*状态\s*\n+([^\n#]+)", content)
    if m and "已完成" in m.group(1):
        return True
    return False


def _unchecked_items(content: str) -> list[str]:
    items: list[str] = []
    for line in content.splitlines():
        if re.match(r"^-\s+\[\s\]\s+", line):
            items.append(line.strip())
    return items


def _title_from_task(content: str) -> str:
    m = re.search(r"^#\s+(.+)$", content, re.M)
    if m:
        return m.group(1).strip()
    return "任务"


def _list_active_task_files(root: Path) -> list[Path]:
    d = root / ACTIVE_DIR
    if not d.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(d.glob("task-*.md")):
        if p.name != "index.md":
            out.append(p)
    return out


def _regenerate_active_index(root: Path) -> None:
    path = root / ACTIVE_INDEX
    if not path.is_file():
        return
    files = _list_active_task_files(root)
    header = "# harness/tasks/active\n\n正在执行的活跃任务存放目录。\n\n## 主要内容\n\n"
    if not files:
        body = (
            "（当前目录下无 `task-*.md` 任务文件；请将任务放入本目录并在 "
            "`harness/context/current-task.md` 中设置 `active_task_id`。）\n"
        )
    else:
        lines: list[str] = []
        for f in files:
            c = _read_task_body(f)
            title = _title_from_task(c)
            lines.append(f"- `{f.name}` — {title}")
        body = "\n".join(lines) + "\n"
    footer = (
        "\n## 关联\n\n"
        "- 由 Agent 主动认领并执行\n"
        "- 完成后移动到 `completed/` 目录\n"
    )
    path.write_text(header + body + footer, encoding="utf-8")


def _ensure_completed_index_entry(root: Path, filename: str, title: str) -> None:
    path = root / COMPLETED_INDEX
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if filename in text:
        return
    bullet = f"- `{filename}` — {title}"
    if "## 主要内容" in text:
        text = text.replace("## 主要内容\n", f"## 主要内容\n\n{bullet}\n", 1)
    else:
        text = text.rstrip() + f"\n\n## 主要内容\n\n{bullet}\n"
    path.write_text(text, encoding="utf-8")


def _reset_current_task_file(root: Path) -> None:
    tpl = """# 当前认领任务

Agent 从 `harness/tasks/active/` 认领任务时，将下方 `active_task_id` 设为**不带 `.md` 后缀**的任务 ID（与 `task-<id>.md` 文件名一致）。`stop` hook 会据此判断是否与 active 中某一文件对应，并提示下一步或自动归档。

---

active_task_id: none
"""
    (root / CONTEXT_TASK).write_text(tpl, encoding="utf-8")


def _archive_task(root: Path, active_file: Path) -> None:
    dest = root / COMPLETED_DIR / active_file.name
    shutil.move(str(active_file), str(dest))
    content = _read_task_body(dest)
    title = _title_from_task(content)
    _reset_current_task_file(root)
    _regenerate_active_index(root)
    _ensure_completed_index_entry(root, active_file.name, title)


def main() -> int:
    root = _repo_root()
    os.chdir(root)

    task_id = _parse_active_task_id(root)
    if not task_id:
        print(
            "[harness/task] 未设置 active_task_id（见 harness/context/current-task.md），跳过任务检查。",
            file=sys.stderr,
        )
        return 0

    fname = _task_filename(task_id)
    active_file = root / ACTIVE_DIR / fname
    if not active_file.is_file():
        print(
            f"[harness/task] active_task_id={task_id!r} 在 {ACTIVE_DIR}/ 中无对应文件 {fname}。",
            file=sys.stderr,
        )
        return 0

    content = _read_task_body(active_file)
    unchecked = _unchecked_items(content)
    marked_done = _is_marked_done(content)
    # 必须：状态标明已完成，且实施步骤中无未勾选项（若有 checklist）
    complete = marked_done and len(unchecked) == 0

    if not complete:
        print(
            "\n[harness/task] 当前会话认领任务 "
            f"`{task_id}` 仍有未完成项（需「## 状态」标明已完成，且不存在 `- [ ]` 未勾选项）。\n",
            file=sys.stderr,
        )
        if unchecked:
            print("**建议下一步执行：**\n", file=sys.stderr)
            for u in unchecked[:8]:
                print(f"  {u}", file=sys.stderr)
            if len(unchecked) > 8:
                print(f"  … 另有 {len(unchecked) - 8} 项", file=sys.stderr)
        else:
            print(
                "  请将「## 状态」更新为包含「已完成」，并确保实施步骤均为 `- [x]`。",
                file=sys.stderr,
            )
        print(
            "\n请在下一会话继续完成上述项；全部完成后再停止会话以便自动归档。\n",
            file=sys.stderr,
        )
        return 0

    try:
        _archive_task(root, active_file)
    except OSError as e:
        print(f"[harness/task] 归档失败: {e}", file=sys.stderr)
        return 1

    print(
        f"\n[harness/task] 已将 `{fname}` 归档至 harness/tasks/completed/，并更新了相关 index.md。\n",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
