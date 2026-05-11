#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
COOKIE_JAR="$(mktemp)"
trap 'rm -f "${COOKIE_JAR}"' EXIT

print_step() {
  printf '\n[%s] %s\n' "$1" "$2"
}

print_step "1/6" "建立顾客会话"
curl -s \
  -c "${COOKIE_JAR}" \
  -X POST \
  -H "Content-Type: application/json" \
  "${BASE_URL}/api/session/login" \
  -d '{"persona":"customer"}'
printf '\n'

print_step "2/6" "查询门店"
curl -s -b "${COOKIE_JAR}" "${BASE_URL}/api/stores"
printf '\n'

print_step "3/6" "查询可预约时段"
curl -s -b "${COOKIE_JAR}" \
  "${BASE_URL}/api/slots?storeId=store-shanghai-jingan&date=2026-05-20&partySize=2"
printf '\n'

print_step "4/6" "创建预约"
create_response="$(
  curl -s \
    -b "${COOKIE_JAR}" \
    -X POST \
    -H "Content-Type: application/json" \
    "${BASE_URL}/api/reservations" \
    -d '{
      "storeId": "store-shanghai-jingan",
      "slotId": "slot-jingan-20260520-1800",
      "partySize": 2
    }'
)"
printf '%s\n' "${create_response}"

reservation_id="$(
  printf '%s' "${create_response}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["reservationId"])'
)"

print_step "5/6" "查询我的预约"
curl -s -b "${COOKIE_JAR}" "${BASE_URL}/api/reservations/me"
printf '\n'

print_step "6/6" "切换店员会话并查看今日预约"
curl -s \
  -c "${COOKIE_JAR}" \
  -X POST \
  -H "Content-Type: application/json" \
  "${BASE_URL}/api/session/login" \
  -d '{"persona":"staff"}' >/dev/null
curl -s -b "${COOKIE_JAR}" \
  "${BASE_URL}/api/staff/reservations?storeId=store-shanghai-jingan&businessDate=2026-05-20"
printf '\n'
