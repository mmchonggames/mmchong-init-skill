#!/usr/bin/env sh
# 将 mmchong-init 中的脚本包、Cursor hooks、harness 骨架应用到目标仓库。
# 用法：./install/apply-to-repo.sh /absolute/or/relative/path/to/target-repo
# 要求：在 mmchong-init 仓库根目录执行，或设置 MMCHONG_INIT_ROOT。

set -eu

TARGET=${1:-}
if [ -z "$TARGET" ]; then
  echo "Usage: $0 <path-to-target-repo>" >&2
  exit 1
fi

if [ -n "${MMCHONG_INIT_ROOT:-}" ]; then
  ROOT="$MMCHONG_INIT_ROOT"
else
  ROOT=$(cd "$(dirname "$0")/.." && pwd)
fi

TARGET=$(cd "$TARGET" && pwd)

if [ ! -d "$TARGET/.git" ] && [ ! -f "$TARGET/.git" ]; then
  echo "Warning: $TARGET does not look like a git repo root (no .git). Continue? (y/N)" >&2
  read -r _confirm || true
fi

echo "=== mmchong-init apply ==="
echo "Source: $ROOT"
echo "Target: $TARGET"

mkdir -p "$TARGET/scripts"
echo "[1/3] Copying scripts-bundle -> target/scripts ..."
cp -R "$ROOT/scripts-bundle/"* "$TARGET/scripts/"

mkdir -p "$TARGET/.cursor"
echo "[2/3] Copying templates/cursor -> target/.cursor ..."
cp "$ROOT/templates/cursor/hooks.json" "$TARGET/.cursor/hooks.json"
rm -rf "$TARGET/.cursor/hooks"
cp -R "$ROOT/templates/cursor/hooks" "$TARGET/.cursor/hooks"

if [ -d "$TARGET/harness" ]; then
  echo "[3/3] Target already has harness/ — skipping harness-skeleton (merge manually if needed)."
else
  echo "[3/3] Copying templates/harness-skeleton -> target/harness ..."
  cp -R "$ROOT/templates/harness-skeleton" "$TARGET/harness"
fi

echo "Done."
echo "Next: customize scripts/hooks/pre-commit, add package.json prepare hook if desired, install personal skill from skill/SKILL.md instructions."
