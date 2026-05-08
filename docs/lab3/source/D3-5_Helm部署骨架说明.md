# D3-5 Helm 部署骨架说明

## 1. 当前目标

本轮先把实验三要求的 Helm 目录从占位态补成可说明、可校验、可继续扩展的最小骨架。

## 2. 当前目录

- `project/infra/helm/Chart.yaml`
- `project/infra/helm/values.yaml`
- `project/infra/helm/values-dev.yaml`
- `project/infra/helm/values-staging.yaml`
- `project/infra/helm/values-prod.yaml`
- `project/infra/helm/templates/member-deployment.yaml`
- `project/infra/helm/templates/member-service.yaml`
- `project/infra/helm/templates/reservation-deployment.yaml`
- `project/infra/helm/templates/reservation-service.yaml`

## 3. 当前覆盖范围

当前 Chart 只覆盖两个实验三核心服务：

- `member-service`
- `reservation-service`

每个服务当前都具备：

- `Deployment`
- `Service`
- 环境级副本数与镜像标签覆盖入口

## 4. 多环境表达方式

- `values-dev.yaml`：单副本，适合本地或最小联调环境
- `values-staging.yaml`：双副本，表达预发布环境
- `values-prod.yaml`：三副本，表达正式环境的更高可用性假设

## 5. 当前限制

当前 Helm 骨架仍然保持克制，暂未补：

- `Ingress`
- `HPA`
- `ConfigMap`
- `Secret`
- `ServiceMonitor`
- `PodDisruptionBudget`

这样处理的原因是实验三当前主目标仍是“先把运行、容器和 CI 固定住”，再逐步向部署细节扩展。
