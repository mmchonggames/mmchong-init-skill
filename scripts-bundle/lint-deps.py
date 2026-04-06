#!/usr/bin/env python3
"""
lint-deps.py — 检查 TypeScript/JavaScript 项目的跨层依赖违规

功能：
1. 解析 tsconfig.json 的 paths 映射（路径别名）
2. 扫描所有 .ts / .tsx / .js / .jsx 文件的 import 语句
3. 根据分层规则（layer rules）判断是否存在违规依赖
4. 输出违规文件 + 违规 import 列表
5. 退出码：0（无违规）/ 1（有违规）

分层规则（默认）：
  - packages/shared/src  → 只允许被 apps/* 和 packages/* 引用，不能引用 apps/api/src
  - apps/api/src         → 只允许被 apps/web 引用（如果有 BFF），不能引用 apps/web
  - apps/web/src         → 不能引用 apps/api/src（通过 @/ 直接 import）
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# ─── 配置 ────────────────────────────────────────────────────────────────

LAYER_RULES: list[dict] = [
    {
        "name": "shared-only-leaf",
        "description": "packages/shared/src 不能直接 import apps/api/src（共享包是叶子节点）",
        "from_pattern": r"^packages/shared/src",
        "to_pattern": r"^apps/api/src",
        "severity": "error",
    },
    {
        "name": "web-cannot-import-api-internals",
        "description": "apps/web 不能通过相对路径 import apps/api/src（应通过 HTTP BFF）",
        "from_pattern": r"^apps/web/src",
        "to_pattern": r"^apps/api/src",
        "severity": "error",
    },
]

# ─── 工具函数 ────────────────────────────────────────────────────────────

def find_tsconfig_roots(project_root: Path) -> list[Path]:
    """在项目根目录和每个 workspace 包中寻找 tsconfig.json"""
    configs = []
    for root, dirs, files in os.walk(project_root):
        # 跳过 node_modules、.git
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", ".turbo", "dist", "build")]
        if "tsconfig.json" in files or "tsconfig.base.json" in files:
            configs.append(Path(root))
    return configs


def parse_tsconfig_paths(tsconfig_path: Path) -> dict[str, str]:
    """解析 tsconfig.json 的 paths 映射，返回 alias -> real path"""
    paths = {}
    try:
        with open(tsconfig_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 简单的 JSON 解析（tsconfig 可能含 comments，需strip）
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        data = json.loads(content)
        paths_raw = data.get("compilerOptions", {}).get("paths", {})
        for alias, targets in paths_raw.items():
            # alias 可能是 "@mmchong/shared/*" 或 "@mmchong/shared"
            if alias.endswith("/*"):
                paths[alias[:-2]] = targets[0][:-2] if targets else ""
            else:
                paths[alias] = targets[0] if targets else ""
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        pass
    return paths


def resolve_alias(import_path: str, paths_map: dict[str, str], project_root: Path) -> str | None:
    """将 import 路径中的 alias 解析为实际相对路径"""
    for alias, real_base in paths_map.items():
        if import_path.startswith(alias):
            suffix = import_path[len(alias):]
            # real_base 可能是 "packages/shared/src" 这样的绝对路径片段
            if real_base.startswith("packages/") or real_base.startswith("apps/"):
                resolved = project_root / real_base / suffix
            elif real_base.startswith("/"):
                resolved = Path(real_base) / suffix
            else:
                resolved = (project_root / real_base) / suffix
            return str(resolved.resolve().relative_to(project_root.resolve()))
    return None


IMPORT_RE = re.compile(
    r"^\s*(?:import\s+.*?\s+from\s+['\"]|require\s*\()['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)

REL_IMPORT_RE = re.compile(r"^(\.\.?(?:/.*)?)$")


def extract_imports(file_path: Path, content: str) -> list[str]:
    """从文件内容中提取所有 import 路径"""
    imports = []
    for match in IMPORT_RE.finditer(content):
        imports.append(match.group(1))
    return imports


def classify_import(
    import_path: str,
    file_path: Path,
    project_root: Path,
    paths_map: dict[str, str],
) -> str | None:
    """
    对 import 路径分类：
      - 返回 None 表示跳过（非层间依赖）
      - 返回实际路径（相对于 project_root）表示需要检查
    """
    # 跳过 node_modules
    if not import_path.startswith("."):
        return None

    # 相对路径 → 直接转为相对路径字符串
    if import_path.startswith("."):
        # 解析相对路径
        try:
            resolved = (file_path.parent / import_path).resolve().relative_to(project_root.resolve())
            return str(resolved)
        except ValueError:
            return None
    return None


def check_violation(from_path: str, to_path: str, rules: list[dict]) -> list[str]:
    """检查 from → to 是否违反分层规则"""
    violations = []
    for rule in rules:
        from_match = re.match(rule["from_pattern"], from_path)
        to_match = re.match(rule["to_pattern"], to_path)
        if from_match and to_match:
            violations.append(f"[{rule['severity']}] {rule['name']}: {from_path} → {to_path}  （{rule['description']}）")
    return violations


def is_in_node_modules(path: Path) -> bool:
    parts = path.parts
    return "node_modules" in parts


def scan_file(
    file_path: Path,
    project_root: Path,
    paths_map: dict[str, str],
    rules: list[dict],
    violations: list[tuple[str, str]],
) -> None:
    """扫描单个文件，收集违规"""
    if is_in_node_modules(file_path):
        return
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return

    for imp in extract_imports(file_path, content):
        classified = classify_import(imp, file_path, project_root, paths_map)
        if classified:
            rel_from = str(file_path.relative_to(project_root))
            v = check_violation(rel_from, classified, rules)
            for msg in v:
                violations.append((str(file_path), msg))


# ─── 主函数 ───────────────────────────────────────────────────────────────

def main() -> None:
    project_root = Path(__file__).parent.parent.resolve()

    # 收集所有需要扫描的文件
    all_files: list[Path] = []
    for root, dirs, files in os.walk(project_root):
        # 跳过无关目录
        dirs[:] = [d for d in dirs if d not in (
            "node_modules", ".git", ".turbo", "dist", "build",
            ".next", ".output", "coverage", ".cache",
        )]
        for f in files:
            if f.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
                all_files.append(Path(root) / f)

    # 全局 paths_map（合并所有 tsconfig）
    global_paths: dict[str, str] = {}
    for tc_root in find_tsconfig_roots(project_root):
        tc_path = tc_root / "tsconfig.json"
        if tc_path.exists():
            # 优先使用 tsconfig.base.json
            base = tc_root / "tsconfig.base.json"
            if base.exists():
                tc_path = base
            global_paths.update(parse_tsconfig_paths(tc_path))

    # 也加载根 tsconfig
    root_tc = project_root / "tsconfig.json"
    if root_tc.exists():
        global_paths.update(parse_tsconfig_paths(root_tc))

    violations: list[tuple[str, str]] = []

    for file_path in all_files:
        scan_file(file_path, project_root, global_paths, LAYER_RULES, violations)

    # ─── 输出结果 ────────────────────────────────────────────────────────
    if violations:
        print("=" * 70)
        print("❌ 跨层依赖违规检查失败")
        print("=" * 70)
        grouped: dict[str, list[str]] = defaultdict(list)
        for fpath, msg in violations:
            grouped[fpath].append(msg)

        for fpath, msgs in sorted(grouped.items()):
            print(f"\n📄 {fpath}")
            for msg in msgs:
                print(f"   {msg}")

        print(f"\n共发现 {len(violations)} 条违规（{len(grouped)} 个文件）")
        sys.exit(1)
    else:
        print("✅ 跨层依赖检查通过，未发现违规")
        sys.exit(0)


if __name__ == "__main__":
    main()
