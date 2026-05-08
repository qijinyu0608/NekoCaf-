# NekoCafé Monorepo Skeleton

实验二到实验四的统一代码仓库骨架。

## 当前阶段

当前工作区已经进入实验三开发阶段，但本轮开发遵循“文档和功能优先、外围能力后置”的节奏。

本轮优先目标：

- 先把 `reservation-service` 与 `member-service` 做成最小可运行闭环。
- 先保证本地开发、单测和最小运行说明清晰可复现。
- 在功能稳定后，再继续补 Docker、Compose、CI/CD、Helm 与观测配置。

本轮暂不展开：

- `BC-ORDER`
- `BC-STORE-OPS`
- `BC-CAT-HEALTH`
- `BC-RECOMMENDATION`
- 完整灰度发布、自动回滚、全量 Dashboard 和 DORA 报表细节

## 当前范围

- 可运行服务：
  - `services/reservation`
  - `services/member`
- 设计层保留上下文：
  - `BC-ORDER`
  - `BC-STORE-OPS`
  - `BC-CAT-HEALTH`
  - `BC-RECOMMENDATION`

## 目录

- `services/`: 服务入口与各自实现
- `libs/common/`: 跨服务共享常量与约定
- `tests/`: 单元、集成、契约、E2E、性能测试占位
- `infra/`: Docker、Helm、可观测性配置占位
- `docs/`: ADR、运行手册、回滚手册

## 本地开发

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

## 当前最小业务链路

本轮已经先落一条可演示的最小链路：

1. 在 `member-service` 查询会员详情与积分账户
2. 在 `reservation-service` 查询门店可预约时段
3. 在 `reservation-service` 创建预约
4. 在 `reservation-service` 查询预约详情与会员预约列表

推荐本地启动方式：

```bash
make run-member
make run-reservation
```

如果要验证最小容器化基线，可以直接运行：

```bash
make compose-up
```

如果要一次性演示当前最小业务链路，可以直接运行：

```bash
make demo-flow
```

最小演示请求示例：

```bash
curl -H 'X-Tenant-Id: tenant-nekocafe' \
  http://127.0.0.1:8002/member/v1/members/member-1001

curl -H 'X-Tenant-Id: tenant-nekocafe' \
  'http://127.0.0.1:8001/reservation/v1/stores/store-shanghai-001/slots?date=2026-05-20&partySize=2'

curl -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Id: tenant-nekocafe' \
  http://127.0.0.1:8001/reservation/v1/reservations \
  -d '{
    "memberId": "member-1001",
    "storeId": "store-shanghai-001",
    "slotId": "slot-20260520-1800",
    "partySize": 2
  }'
```

## 实验三推荐开发顺序

1. 先阅读 `docs/lab3/README.md` 与 `docs/development-path.md` 中的实验三阶段拆分。
2. 先完成 `project/README.md`、`project/docs/runbook.md`、`project/docs/rollback.md` 的边界收口。
3. 先补双核心服务的最小业务接口，再补容器化与本地起栈。
4. 最后再补 CI/CD、Helm、多环境与观测证据。

## 实验三最小完成标准

- 两个核心服务可以本地启动。
- 至少有一条最小业务链路可请求、可测试、可演示。
- README 能指导同学完成环境安装、测试和最小启动。
- `docker compose up` 和 CI 骨架在后续阶段逐步补齐，而不是一开始全部压上。

## 下一步

1. 完成实验三 `Phase A` 文档边界收口。
2. 进入实验三 `Phase B`，补双核心服务的最小功能闭环。
3. 在实验三 `Phase C/D` 继续补容器化、CI/CD 和部署骨架。
4. 在实验四把测试、质量门禁和 AI 评审挂到同一仓库。
