# D3-6 可观测性配置与 Dashboard 说明

## 1. 当前目标

本轮先补实验三可观测性的最小闭环，重点不是完整平台化，而是保证当前 PoC 已经具备“可采集、可关联、可解释”的基础能力。

## 2. 当前实现内容

### 2.1 服务侧

`member-service` 与 `reservation-service` 当前都已经补入：

- `X-Trace-Id` 透传与自动生成
- 基础请求日志
- `/metrics` 指标暴露

当前关键指标包括：

- `nekocafe_http_requests_total`
- `nekocafe_http_request_duration_seconds`

## 3. 当前配置文件

- `project/libs/common/observability.py`
- `project/infra/observability/prometheus.yml`
- `project/infra/observability/alert-rules.yml`
- `project/infra/observability/grafana-dashboard.json`

## 4. 本地运行方式

当前通过 `docker compose up -d` 可以同时启动：

- `member-service`
- `reservation-service`
- `prometheus`

本地查看入口：

- 服务指标：
  - `http://127.0.0.1:8001/metrics`
  - `http://127.0.0.1:8002/metrics`
- Prometheus：
  - `http://127.0.0.1:9090`
  - `http://127.0.0.1:9090/targets`

## 4.1 当前本地验证结果

本地已验证：

- `Prometheus Server is Healthy`
- `member-service` target 状态为 `up`
- `reservation-service` target 状态为 `up`
- 两个服务的 `/metrics` 都已输出 `nekocafe_http_requests_total`

## 5. 当前能说明什么

当前这套最小基线已经可以说明：

- 请求级别具备基本链路标识
- 双服务具备可抓取指标
- 本地具备基础监控采集入口，并且 Prometheus 已能抓取两个服务
- Dashboard 已有 JSON 定义，可作为后续截图和答辩演示输入

## 6. 当前未覆盖部分

当前尚未覆盖：

- 完整 OpenTelemetry Trace 上报
- 日志聚合与检索平台
- 真正运行中的 Grafana 容器与截图
- 告警通知联动

这些内容保留为实验三后续增强项。
