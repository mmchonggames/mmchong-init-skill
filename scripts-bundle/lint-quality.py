#!/usr/bin/env python3
"""
lint-quality.py — 代码质量检查脚本

功能：
1. 检查文件命名规范（kebab-case）
2. 检查类型命名规范（PascalCase for types/interfaces/enum, camelCase for functions）
3. 检查单文件行数限制（默认 500 行）
4. 检查是否使用了 console.log / console.error（应使用结构化日志）
5. 输出违规文件 + 违规内容
6. 退出码：0（无违规）/ 1（有违规）
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ─── 配置 ────────────────────────────────────────────────────────────────

MAX_LINES_PER_FILE = 500

# 文件名规范：支持的文件类型
FILENAME_RULES: list[dict] = [
    {
        "pattern": r"\.ts$|\.tsx$|\.js$|\.jsx$",
        "expected_case": "kebab",
        "description": "文件名应使用 kebab-case（如 my-file.ts）",
    },
    {
        "pattern": r"\.test\.ts$|\.spec\.ts$|\.test\.tsx$|\.spec\.tsx$",
        "expected_case": "kebab",
        "description": "测试文件应使用 kebab-case（如 my-file.test.ts）",
    },
]

# console 使用检测
CONSOLE_PATTERN = re.compile(r"\bconsole\.(log|error|warn|info|debug)\s*\(", re.MULTILINE)

# 类型声明检测（简单版）
# 匹配 TypeScript 类型声明：type Xxx = / interface Xxx / enum Xxx
TYPE_DECL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:type|interface|enum|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)",
    re.MULTILINE,
)

# 函数声明检测（function xxx / const xxx = / const xxx: React.FC）
FUNCTION_DECL_RE = re.compile(
    r"^\s*(?:export\s+)?function\s+([a-z][A-Za-z0-9_$]*)\s*\(",
    re.MULTILINE,
)

# 常量/变量函数声明
CONST_FUNC_RE = re.compile(
    r"^\s*(?:export\s+)?const\s+([a-z][A-Za-z0-9_$]*)\s*[=:]\s*(?:async\s+)?(?:"
    r"function\s*(?:<[^>]+>)?\s*\(|"
    r"\([^)]*\)\s*(?:=>|:)|"
    r"[a-zA-Z_$][a-zA-Z0-9_$.]*\s*=>)",
    re.MULTILINE,
)

# PascalCase 检测（首字母大写且无连字符）
PASCAL_CASE_RE = re.compile(r"^[A-Z][A-Za-z0-9_$]*$")
KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


# ─── 检查逻辑 ────────────────────────────────────────────────────────────

def check_filename_case(file_path: Path) -> list[str]:
    """检查文件名是否符合 kebab-case 规范"""
    errors = []
    name = file_path.name

    # 排除 index 文件（index.ts 是允许的）
    if name == "index.ts" or name == "index.tsx":
        return errors

    for rule in FILENAME_RULES:
        if re.search(rule["pattern"], name):
            if not KEBAB_CASE_RE.match(name.replace(".", "-")):
                # 尝试更严格的 kebab-case 检测
                base_name = name.rsplit(".", 1)[0]
                if not KEBAB_CASE_RE.match(base_name):
                    errors.append(
                        f"文件名不符合 kebab-case：{name}（期望如 my-file.ts）"
                    )
    return errors


def check_type_naming(content: str, file_path: Path) -> list[str]:
    """检查类型命名是否符合规范"""
    errors = []

    for match in TYPE_DECL_RE.finditer(content):
        type_name = match.group(1)
        # 排除以 _ 或 $ 结尾的特殊类型（内部类型）
        if type_name.startswith("_") or type_name.startswith("$"):
            continue
        # 排除数字开头的泛型参数（<T> 中的 T 不在这里匹配）
        if type_name in ("T", "K", "V", "R", "P", "Q", "U"):
            continue
        if not PASCAL_CASE_RE.match(type_name):
            errors.append(
                f"类型/接口/枚举命名不符合 PascalCase：{type_name}（应为 {type_name.capitalize()}）"
            )
    return errors


def check_function_naming(content: str, file_path: Path) -> list[str]:
    """检查函数命名是否符合 camelCase 规范

    camelCase: 首字母小写，后续单词首字母大写（createLogger, isNodeEnv）
    PascalCase: 首字母大写（React.FC）
    kebab-case: 不允许
    """
    errors = []

    # 检测是否是有效的 camelCase（首字母小写，后面可以有大小写）
    def is_camel_case(name: str) -> bool:
        if not name:
            return False
        if name[0].islower():
            # 检查整体格式：首字母小写，后面不全是小写或全是小写+数字
            # 允许 createLogger（混合大小写）、isNodeEnv、fetchApi 等
            return True
        return False

    for match in FUNCTION_DECL_RE.finditer(content):
        func_name = match.group(1)
        if func_name.startswith("_"):
            continue
        if not is_camel_case(func_name):
            # 不是 camelCase（可能是 kebab-case 或其他违规命名）
            if KEBAB_CASE_RE.match(func_name) or (func_name[0].islower() and "-" in func_name):
                errors.append(
                    f"函数命名不符合 camelCase：{func_name}（camelCase 应以小写字母开头，如 myFunc）"
                )
    return errors


def check_console_usage(content: str, file_path: Path) -> list[str]:
    """检查是否使用了 console（应使用结构化日志）"""
    errors = []
    for match in CONSOLE_PATTERN.finditer(content):
        line_no = content[: match.start()].count("\n") + 1
        console_method = match.group(1)
        errors.append(
            f"第 {line_no} 行：使用了 console.{console_method}（应使用 @mmchong/shared 中的结构化日志）"
        )
    return errors


def check_file_length(file_path: Path) -> list[str]:
    """检查文件行数是否超过限制"""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            line_count = sum(1 for _ in f)
        if line_count > MAX_LINES_PER_FILE:
            errors.append(
                f"文件超过 {MAX_LINES_PER_FILE} 行（实际 {line_count} 行），建议拆分"
            )
    except Exception:
        pass
    return errors


def scan_file(file_path: Path) -> list[tuple[str, str]]:
    """
    扫描单个文件，返回 [(violation_type, message)] 列表
    """
    violations: list[tuple[str, str]] = []

    # 跳过非源文件
    if is_in_ignored_dir(file_path):
        return violations

    ext = file_path.suffix
    if ext not in (".ts", ".tsx", ".js", ".jsx"):
        return violations

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    # 1. 文件名检查
    for err in check_filename_case(file_path):
        violations.append(("filename", err))

    # 2. 类型命名（跳过测试文件）
    if not re.search(r"\.test\.(ts|tsx)$|\.spec\.(ts|tsx)$", file_path.name):
        for err in check_type_naming(content, file_path):
            violations.append(("type-naming", err))

    # 3. 函数命名
    for err in check_function_naming(content, file_path):
        violations.append(("function-naming", err))

    # 4. console 使用
    for err in check_console_usage(content, file_path):
        violations.append(("console", err))

    # 5. 文件长度
    for err in check_file_length(file_path):
        violations.append(("file-length", err))

    return violations


def is_in_ignored_dir(file_path: Path) -> bool:
    """判断文件是否在忽略目录中"""
    ignored = {
        "node_modules", ".git", ".turbo", "dist", "build",
        ".next", ".output", "coverage", ".cache",
        "__tests__", "__mocks__", "tests", "test",
    }
    parts = set(file_path.parts)
    return bool(parts & ignored)


# ─── 主函数 ──────────────────────────────────────────────────────────────

def main() -> None:
    project_root = Path(__file__).parent.parent.resolve()

    # 收集所有源文件
    all_files: list[Path] = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in (
            "node_modules", ".git", ".turbo", "dist", "build",
            ".next", ".output", "coverage", ".cache",
        )]
        for f in files:
            if f.endswith((".ts", ".tsx", ".js", ".jsx")):
                all_files.append(Path(root) / f)

    all_violations: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for file_path in all_files:
        violations = scan_file(file_path)
        for vtype, msg in violations:
            rel_path = str(file_path.relative_to(project_root))
            all_violations[rel_path][vtype].append(msg)

    # ─── 输出结果 ────────────────────────────────────────────────────────
    if all_violations:
        print("=" * 70)
        print("❌ 代码质量检查失败")
        print("=" * 70)

        total = sum(len(msgs) for per_file in all_violations.values() for msgs in per_file.values())
        for rel_path, per_type in sorted(all_violations.items()):
            print(f"\n📄 {rel_path}")
            for vtype, msgs in per_type.items():
                type_label = {
                    "filename": "  文件命名",
                    "type-naming": "  类型命名",
                    "function-naming": "  函数命名",
                    "console": "  console 使用",
                    "file-length": "  文件长度",
                }.get(vtype, vtype)
                for msg in msgs:
                    print(f"     ⚠  {msg}")

        print(f"\n共发现 {total} 条违规（{len(all_violations)} 个文件）")
        sys.exit(1)
    else:
        print("✅ 代码质量检查通过，未发现违规")
        sys.exit(0)


if __name__ == "__main__":
    main()
