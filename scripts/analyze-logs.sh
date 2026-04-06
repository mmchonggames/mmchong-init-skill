#!/bin/bash
# ============================================================
# analyze-logs.sh — mmchong 结构化日志分析脚本
# 分析 JSON 日志文件，输出耗时统计和错误分布
# ============================================================

set -e

# ── 参数解析 ────────────────────────────────────────────
LOG_FILE="${1:-}"
MODE="${2:-summary}"

if [ -z "$LOG_FILE" ] || [ ! -f "$LOG_FILE" ]; then
  echo "用法: $0 <日志文件路径> [summary|errors|duration|all]"
  echo ""
  echo "示例:"
  echo "  $0 /var/log/mmchong/api/app.log all"
  echo "  $0 ./logs/api.log errors"
  exit 1
fi

# ── 颜色定义 ────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== 日志分析: $(basename "$LOG_FILE") ===${NC}"
echo ""

# ── 检查 jq 是否安装 ────────────────────────────────────
if ! command -v jq &> /dev/null; then
  echo -e "${RED}错误: 需要安装 jq (JSON 处理器)${NC}"
  echo "  macOS: brew install jq"
  echo "  Ubuntu/Debian: apt install jq"
  exit 1
fi

# ── 1. 摘要统计 ─────────────────────────────────────────
show_summary() {
  echo -e "${YELLOW}【摘要统计】${NC}"
  local total=$(wc -l < "$LOG_FILE")
  local errors=$(grep -c '"level":"ERROR"' "$LOG_FILE" 2>/dev/null || echo "0")
  local warns=$(grep -c '"level":"WARN"' "$LOG_FILE" 2>/dev/null || echo "0")
  local infos=$(grep -c '"level":"INFO"' "$LOG_FILE" 2>/dev/null || echo "0")

  echo "  总日志条数: $total"
  echo "  ERROR: $errors"
  echo "  WARN:  $warns"
  echo "  INFO:  $infos"
  echo ""
}

# ── 2. 错误分布 ─────────────────────────────────────────
show_errors() {
  echo -e "${RED}【错误分布】${NC}"

  if ! grep -q '"level":"ERROR"' "$LOG_FILE"; then
    echo "  (无 ERROR 日志)"
    echo ""
    return
  fi

  # 按 error.name 分布
  echo "  按错误类型:"
  grep '"level":"ERROR"' "$LOG_FILE" | \
    jq -r 'select(.error != null) | .error.name // "Unknown"' | \
    sort | uniq -c | sort -rn | while read count name; do
      printf "    %-6s %s\n" "[$count]" "$name"
    done

  echo ""

  # 按 service 分布
  echo "  按服务分布:"
  grep '"level":"ERROR"' "$LOG_FILE" | \
    jq -r '.service // "unknown"' | \
    sort | uniq -c | sort -rn | while read count svc; do
      printf "    %-6s %s\n" "[$count]" "$svc"
    done

  echo ""

  # 最新 5 条错误（摘要）
  echo "  最新 5 条错误:"
  grep '"level":"ERROR"' "$LOG_FILE" | \
    jq -r '[.timestamp, .service, .error.name, .error.message] | @tsv' | \
    tail -5 | while read ts svc name msg; do
      echo -e "    ${RED}$ts${NC} [$svc] $name: ${msg:0:60}..."
    done

  echo ""
}

# ── 3. 耗时统计 ─────────────────────────────────────────
show_duration() {
  echo -e "${GREEN}【耗时统计】${NC}"

  if ! grep -q '"duration"' "$LOG_FILE"; then
    echo "  (日志中无 duration 字段)"
    echo ""
    return
  fi

  echo "  平均耗时 (ms):"
  grep -v '^$' "$LOG_FILE" | \
    jq -r 'select(.duration != null) | .duration' | \
    awk '{ sum+=$1; n++ } END { if(n>0) printf "    %.2f ms\n", sum/n; else print "    (无数据)"; }'

  echo "  最大耗时 TOP 5:"
  grep -v '^$' "$LOG_FILE" | \
    jq -r 'select(.duration != null) | [.timestamp, .duration, .message] | @tsv' | \
    sort -t$'\t' -k2 -rn | head -5 | \
    while IFS=$'\t' read -r ts dur msg; do
      echo -e "    ${BLUE}${dur}ms${NC} $ts — $msg"
    done

  echo ""

  # 按 endpoint 统计耗时
  echo "  按路径平均耗时 (ms):"
  grep -v '^$' "$LOG_FILE" | \
    jq -r 'select(.duration != null and .context != null) | [.context.path // "unknown", .duration] | @tsv' | \
    awk -F'\t' '{ paths[$1]++; sums[$1]+=$2 } END {
      for (p in sums) printf "    %-30s %.2f ms (n=%d)\n", p, sums[p]/paths[p], paths[p]
    }' | sort -t' ' -k2 -rn

  echo ""
}

# ── 4. 输出全部 ─────────────────────────────────────────
show_all() {
  show_summary
  show_errors
  show_duration
}

# ── 执行 ────────────────────────────────────────────────
case "$MODE" in
  summary)
    show_summary
    ;;
  errors)
    show_errors
    ;;
  duration)
    show_duration
    ;;
  all)
    show_all
    ;;
  *)
    echo -e "${RED}未知模式: $MODE${NC}"
    echo "可用模式: summary | errors | duration | all"
    exit 1
    ;;
esac

echo -e "${BLUE}=== 分析完成 ===${NC}"
