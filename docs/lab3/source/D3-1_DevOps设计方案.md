# D3-1 DevOps 设计方案

## 1. 文档目标

本方案用于说明 NekoCafe 课程项目在实验三阶段的工程化落地路径。核心目标不是一次性实现完整生产平台，而是在实验二架构输入的基础上，形成一套可运行、可测试、可容器化、可验证的最小 DevOps 闭环，并为实验四的质量工程打基础。

## 2. 当前建设范围

### 2.1 项目形态

- 仓库形态：Monorepo
- 统一工程目录：`project/`
- 统一实验交付目录：`docs/lab3/`

### 2.2 当前优先服务

本轮只把下面两个上下文落成真实可运行服务：

- `reservation-service`
- `member-service`

### 2.3 当前交付目标

1. 形成最小业务闭环
2. 补齐 Docker 与 Compose
3. 补齐最小 CI 与 Helm 骨架
4. 补齐最小可观测性
5. 形成实验三可验收证据

## 3. 总体设计原则

### 3.1 文档和功能优先

先明确边界、范围和运行方式，再进行编码和工程化补全，避免在功能未稳定时过早扩展外围平台能力。

### 3.2 最小闭环优先

实验三只要求形成“真实可运行 PoC”，因此优先保证一条可请求、可测试、可演示的业务链路，而不是追求全量业务域一次到位。

### 3.3 真实交付优先

所有交付文档应尽量回填自真实运行结果，包括测试输出、Compose 配置、Trivy 扫描、Prometheus target 状态等，避免提前虚写。

## 4. 架构与目录方案

### 4.1 Monorepo 取舍

采用 Monorepo 的原因如下：

1. 课程实验阶段更强调统一目录、统一依赖和统一追溯
2. 双服务共享 `libs/common/` 更方便统一租户头、样例数据、基础命名与观测中间件
3. 文档、工程、测试、部署材料集中在同一仓库内，更适合实验三到实验四连续推进

### 4.2 目录职责

- `project/services/`：双服务入口与接口实现
- `project/libs/common/`：共享样例数据、观测逻辑和基础约定
- `project/tests/`：服务级单元验证
- `project/infra/docker/`：容器化定义
- `project/infra/helm/`：最小 Helm 部署骨架
- `project/infra/observability/`：Prometheus、告警规则与 Dashboard JSON
- `project/docs/`：运行手册、回滚手册与工程说明

## 5. 服务与功能范围

### 5.1 当前保留的最小业务链路

当前已落地的主链路如下：

1. 查询会员详情
2. 查询会员积分账户
3. 查询门店可预约时段
4. 创建预约
5. 查询预约详情
6. 查询会员预约列表

### 5.2 当前不优先展开的范围

以下内容保留在实验二文档与架构表达层，不在实验三本轮扩展为真实实现：

- 推荐域
- 门店运营域
- 猫咪健康域
- 完整灰度发布
- 自动回滚与告警联动
- 完整 Grafana 平台化运行

## 6. 构建与部署方案

### 6.1 本地开发模式

本地采用统一 Python 工程方式：

1. 通过 `python3 -m venv .venv` 创建虚拟环境
2. 通过 `pip install -e '.[dev]'` 安装项目依赖
3. 通过 `make run-member`、`make run-reservation` 启动服务
4. 通过 `pytest -q` 验证当前实现

### 6.2 容器化方案

当前每个服务对应一个最小 Dockerfile：

- `project/infra/docker/member.Dockerfile`
- `project/infra/docker/reservation.Dockerfile`

统一使用 `python:3.12-slim` 作为基础镜像，采用单阶段构建。当前版本优先满足可构建、可运行、可扫描，不提前引入多阶段和非 root 增强项。

### 6.3 本地编排方案

通过 `docker-compose.yml` 编排以下组件：

- `member-service`
- `reservation-service`
- `prometheus`

其中双服务都配置健康检查，Prometheus 通过静态 scrape config 抓取 `/metrics`。

### 6.4 CI 方案

当前最小 CI 主链位于：

- `project/.github/workflows/ci.yml`

当前包含两类检查：

1. Python 检查链：依赖安装、`pytest -q`、`docker compose config`
2. Helm 检查链：基础 `helm lint` 与三套 values 校验

### 6.5 Helm 方案

当前 Helm 目录提供最小部署骨架：

- `Chart.yaml`
- `values.yaml`
- `values-dev.yaml`
- `values-staging.yaml`
- `values-prod.yaml`
- `templates/` 下的 Deployment 与 Service 模板

本轮目标是满足“结构完整、职责清晰、可讲清楚”，而不是直接接入真实 K8s 集群。

## 7. 可观测性方案

### 7.1 服务内观测

双服务统一接入共享观测逻辑，当前能力包括：

- `X-Trace-Id` 透传与自动生成
- 结构化请求日志
- `/metrics` 指标输出

### 7.2 当前关键指标

- `nekocafe_http_requests_total`
- `nekocafe_http_request_duration_seconds`

### 7.3 当前采集链路

Prometheus 通过 `project/infra/observability/prometheus.yml` 抓取两个服务的 `/metrics`，并通过 `alert-rules.yml` 提供基础告警规则。

## 8. 回滚与风险控制

当前阶段不依赖真实发布平台，回滚策略以最小、可控为原则：

1. 优先回退到最近一个通过本地测试的 Git 提交
2. 当 Compose 配置导致运行异常时，优先恢复到最近一个可启动版本
3. 当局部功能回归时，优先通过单服务重建和健康检查确认恢复

## 9. 验收口径

当前实验三完成度以以下条件作为判断依据：

1. 双服务可本地启动
2. 最小业务链路可演示
3. `docker compose up` 可运行
4. CI 配置文件与 Helm 骨架已落地
5. `/metrics` 与 Prometheus target 可验证
6. 文档、脚本和导出证据能反映真实工程状态

## 10. 与实验四的衔接

实验三输出给实验四的关键基础包括：

- 可运行服务
- 最小部署链路
- 观测与日志基础
- 可被测试与审查的真实代码

实验四将在此基础上继续补齐测试体系、缺陷闭环、质量门禁与 AI 辅助代码审查记录。
