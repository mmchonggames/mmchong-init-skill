#!/bin/bash
# ============================================================
# validate.sh — mmchong 统一验证脚本
# 运行：lint + typecheck + test
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Validating mmchong ==="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ── 1/3: TypeScript 类型检查 ──────────────────────────
echo -e "${YELLOW}[1/3]${NC} TypeScript check..."
if pnpm build:api --filter=api 2>&1 | tee /tmp/tscheck.log > /dev/null; then
  echo -e "${GREEN}  ✓ TypeScript check passed${NC}"
else
  echo -e "${RED}  ✗ TypeScript check failed${NC}"
  cat /tmp/tscheck.log
  exit 1
fi

# ── 2/3: Lint ──────────────────────────────────────────
echo -e "${YELLOW}[2/3]${NC} Lint..."
if pnpm lint 2>&1 | tee /tmp/lint.log > /dev/null; then
  echo -e "${GREEN}  ✓ Lint passed${NC}"
else
  echo -e "${RED}  ✗ Lint failed${NC}"
  cat /tmp/lint.log
  exit 1
fi

# ── 3/3: Tests ─────────────────────────────────────────
echo -e "${YELLOW}[3/3]${NC} Tests..."
if pnpm --filter api test 2>&1 | tee /tmp/test-api.log > /dev/null; then
  echo -e "${GREEN}  ✓ API tests passed${NC}"
else
  echo -e "${RED}  ✗ API tests failed${NC}"
  cat /tmp/test-api.log
  exit 1
fi

echo ""
echo "=== Done — All checks passed ✓ ==="
