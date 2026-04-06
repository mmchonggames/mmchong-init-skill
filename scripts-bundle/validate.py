#!/usr/bin/env python3
"""
validate.py — mmchong.ai 统一验证管道

整合以下检查，按顺序执行，任意一步失败则整体失败：
  1. TypeScript 编译检查（pnpm build:api --filter=api）
  2. 跨层依赖检查（scripts/lint-deps.py）
  3. 代码质量检查（scripts/lint-quality.py）
  4. 单元测试（pnpm --filter api test）

使用方式：
  python scripts/validate.py

环境变量：
  SKIP_TSC   — 若设置，跳过 TypeScript 编译检查
  SKIP_DEPS  — 若设置，跳过跨层依赖检查
  SKIP_QUAL  — 若设置，跳过代码质量检查
  SKIP_TEST  — 若设置，跳过单元测试

退出码：
  0 — 所有检查通过
  1 — 任意检查失败
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# ─── 颜色定义 ─────────────────────────────────────────────────────────────

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


def color(text: str, c: str) -> str:
    return f"{c}{text}{NC}"


# ─── 执行工具 ─────────────────────────────────────────────────────────────

def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    env: dict | None = None,
    capture: bool = True,
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    """运行 shell 命令，包装 subprocess.run"""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        capture_output=capture,
        text=True,
        timeout=timeout,
    )
    return result


def step(n: int, total: int, name: str, cmd: str) -> None:
    """打印步骤标题"""
    print()
    print(color(f"─{'─' * 68}─", CYAN))
    print(color(f"  [{n}/{total}] {name}", BOLD))
    print(color(f"  命令: {' '.join(cmd)}", CYAN))
    print(color(f"─{'─' * 68}─", CYAN))


def report(passed: bool, msg: str) -> None:
    """打印检查结果"""
    if passed:
        print(f"  {color('✅', GREEN)} {msg}")
    else:
        print(f"  {color('❌', RED)} {msg}")


# ─── 检查函数 ─────────────────────────────────────────────────────────────

def check_typescript(project_root: Path) -> tuple[bool, str]:
    """运行 TypeScript 编译检查"""
    cmd = ["pnpm", "build:api", "--filter=api"]
    result = run_command(cmd, cwd=project_root, timeout=300)
    if result.returncode == 0:
        return True, "TypeScript 编译检查通过"
    else:
        # 截取关键错误信息
        stderr = result.stderr[-2000:] if result.stderr else ""
        stdout = result.stdout[-1000:] if result.stdout else ""
        detail = stderr or stdout
        return False, f"TypeScript 编译失败\n{detail[-500:]}"


def check_deps(project_root: Path) -> tuple[bool, str]:
    """运行跨层依赖检查"""
    script = project_root / "scripts" / "lint-deps.py"
    result = run_command(["python3", str(script)], cwd=project_root, timeout=120)
    if result.returncode == 0:
        return True, "跨层依赖检查通过"
    else:
        return False, f"跨层依赖违规\n{result.stdout[-1000:]}"


def check_quality(project_root: Path) -> tuple[bool, str]:
    """运行代码质量检查"""
    script = project_root / "scripts" / "lint-quality.py"
    result = run_command(["python3", str(script)], cwd=project_root, timeout=120)
    if result.returncode == 0:
        return True, "代码质量检查通过"
    else:
        return False, f"代码质量违规\n{result.stdout[-1000:]}"


def check_tests(project_root: Path) -> tuple[bool, str]:
    """运行单元测试"""
    cmd = ["pnpm", "--filter", "api", "test"]
    result = run_command(cmd, cwd=project_root, timeout=300)
    if result.returncode == 0:
        return True, "单元测试通过"
    else:
        stdout = result.stdout[-2000:] if result.stdout else ""
        stderr = result.stderr[-1000:] if result.stderr else ""
        detail = stdout or stderr
        return False, f"单元测试失败\n{detail[-800:]}"


# ─── 主函数 ───────────────────────────────────────────────────────────────

def main() -> None:
    project_root = Path(__file__).parent.parent.resolve()
    start_time = time.time()

    checks = [
        ("TypeScript 编译", check_typescript, bool(os.environ.get("SKIP_TSC"))),
        ("跨层依赖检查", check_deps, bool(os.environ.get("SKIP_DEPS"))),
        ("代码质量检查", check_quality, bool(os.environ.get("SKIP_QUAL"))),
        ("单元测试", check_tests, bool(os.environ.get("SKIP_TEST"))),
    ]

    total = len(checks)
    active = [c for c in checks if not c[2]]  # 排除跳过的
    active_total = len(active)

    # 过滤掉跳过的
    checks_to_run = [(name, fn, skipped) for name, fn, skipped in checks]

    print(color("╔══════════════════════════════════════════════════════════╗", BOLD))
    print(color("║         mmchong.ai 统一验证管道                           ║", BOLD))
    print(color("╚══════════════════════════════════════════════════════════╝", BOLD))
    print(f"  项目根目录：{project_root}")
    print(f"  检查项：{active_total}/{total}（跳过 {total - active_total} 项）")

    results: list[tuple[str, bool, str]] = []

    for i, (name, fn, skipped) in enumerate(checks_to_run, 1):
        step(i, total, f"{name} {'[已跳过]' if skipped else ''}", [])

        if skipped:
            print(f"  {color('⏭ ', YELLOW)} 跳过（SKIP_XXX 环境变量）")
            results.append((name, True, "跳过"))
            continue

        passed, msg = fn(project_root)
        results.append((name, passed, msg))
        report(passed, msg)

        if not passed:
            print(f"\n  {color('🔍 详情：', YELLOW)}{msg[:300]}")

    # ─── 汇总 ──────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    passed_count = sum(1 for _, p, _ in results if p)
    failed_count = len(results) - passed_count

    print()
    print(color("═" * 70, BOLD))
    print(f"  耗时：{elapsed:.1f}s")
    print(f"  结果：{passed_count}/{len(results)} 通过", end="")

    if failed_count > 0:
        print(color(f"  ❌ {failed_count} 项失败", RED))
        print()
        print(color("失败项：", RED))
        for name, passed, msg in results:
            if not passed:
                print(f"  • {name}")
        print()
        print(color("═" * 70, RED))
        print(color("❌ 验证管道失败 — 请修复上述问题后重试", RED))
        sys.exit(1)
    else:
        print(color("  ✅ 全部通过", GREEN))
        print()
        print(color("═" * 70, GREEN))
        print(color("✅ 验证管道完成 — 所有检查通过", GREEN))
        sys.exit(0)


if __name__ == "__main__":
    main()
