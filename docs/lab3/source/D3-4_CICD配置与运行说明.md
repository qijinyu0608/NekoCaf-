# D3-4 CI/CD 配置与运行说明

## 1. 当前目标

本轮只先补实验三 `Phase D` 的最小 CI 主链，优先把当前已经可运行的双服务 PoC 固化下来，而不是一次性扩展完整 CD、镜像推送和扫描平台。

## 2. 当前文件位置

- CI 工作流：`project/.github/workflows/ci.yml`

## 3. 当前流水线范围

当前 CI 只覆盖两类最基础校验：

1. Python 工程校验
   - 安装 `project/` 依赖
   - 运行 `pytest -q`
   - 校验 `docker compose config`
2. Helm 结构校验
   - 对 `project/infra/helm/` 运行 `helm lint`
   - 对 `dev/staging/prod` 三套 values 分别运行校验

## 4. 为什么先这样做

- 当前工程已经具备本地运行、容器启动和最小业务链路。
- 先补测试与配置校验，可以把“当前可运行状态”固定成可回归基线。
- 这样既符合实验三流水线要求，也不会让实现范围失控。

## 5. 当前未纳入的能力

当前还没有纳入：

- 镜像推送到远端仓库
- 安全扫描
- 自动部署到真实集群
- 发布审批与自动回滚

这些能力保留到实验三后续阶段继续补。

## 6. 当前运行留档

当前最小 CI 主链已经补了本地验证留档，文件位于：

- `docs/lab3/exports/D3-4_local_ci_validation.txt`

当前留档覆盖：

1. `pytest -q`
2. `docker compose config`
3. `helm lint`

当前说明文档和本地留档已经能共同说明：实验三当前 CI 主链虽小，但已经具备可复核、可追踪的基本交付形态。
