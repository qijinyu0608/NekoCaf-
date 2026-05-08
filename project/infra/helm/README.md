# Helm Baseline

当前目录已经补成实验三 `Phase D` 的最小 Helm 骨架，目标是先满足“结构完整、环境区分明确、能被 CI 校验”。

当前包含：

- `Chart.yaml`
- `values.yaml`
- `values-dev.yaml`
- `values-staging.yaml`
- `values-prod.yaml`
- `templates/member-*.yaml`
- `templates/reservation-*.yaml`

当前约束：

- 仅覆盖 `member-service` 与 `reservation-service`
- 先表达最小 Deployment + Service
- 暂未补 ConfigMap、Ingress、HPA、Secret 与观测 Sidecar
