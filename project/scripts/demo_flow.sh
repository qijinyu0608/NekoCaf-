#!/usr/bin/env bash
set -euo pipefail

TENANT_ID="${TENANT_ID:-tenant-nekocafe}"
MEMBER_BASE_URL="${MEMBER_BASE_URL:-http://127.0.0.1:8002}"
RESERVATION_BASE_URL="${RESERVATION_BASE_URL:-http://127.0.0.1:8001}"

print_step() {
  printf '\n[%s] %s\n' "$1" "$2"
}

print_step "1/6" "查询会员详情"
curl -s \
  -H "X-Tenant-Id: ${TENANT_ID}" \
  "${MEMBER_BASE_URL}/member/v1/members/member-1001"
printf '\n'

print_step "2/6" "查询会员积分账户"
curl -s \
  -H "X-Tenant-Id: ${TENANT_ID}" \
  "${MEMBER_BASE_URL}/member/v1/members/member-1001/points"
printf '\n'

print_step "3/6" "查询门店可预约时段"
curl -s \
  -H "X-Tenant-Id: ${TENANT_ID}" \
  "${RESERVATION_BASE_URL}/reservation/v1/stores/store-shanghai-001/slots?date=2026-05-20&partySize=2"
printf '\n'

print_step "4/6" "创建预约"
create_response="$(
  curl -s \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Tenant-Id: ${TENANT_ID}" \
    "${RESERVATION_BASE_URL}/reservation/v1/reservations" \
    -d '{
      "memberId": "member-1001",
      "storeId": "store-shanghai-001",
      "slotId": "slot-20260520-1800",
      "partySize": 2
    }'
)"
printf '%s\n' "${create_response}"

reservation_id="$(
  printf '%s' "${create_response}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["reservationId"])'
)"

print_step "5/6" "查询预约详情"
curl -s \
  -H "X-Tenant-Id: ${TENANT_ID}" \
  "${RESERVATION_BASE_URL}/reservation/v1/reservations/${reservation_id}"
printf '\n'

print_step "6/6" "查询会员预约列表"
curl -s \
  -H "X-Tenant-Id: ${TENANT_ID}" \
  "${RESERVATION_BASE_URL}/reservation/v1/members/member-1001/reservations"
printf '\n'
