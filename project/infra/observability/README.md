# Observability Baseline

当前目录已经补成实验三 `Phase E` 的最小可观测性基线。

当前包含：

- `prometheus.yml`：抓取 `nekocafe-web` 的 `/metrics`
- `alert-rules.yml`：最小服务存活告警规则
- `grafana-dashboard.json`：基础请求速率与 P95 延迟面板定义

当前范围仍然保持克制：

- 先落 `Prometheus + /metrics + traceId + 基础请求日志`
- 暂未接入完整 OpenTelemetry SDK、日志聚合平台和真实 Grafana 容器
