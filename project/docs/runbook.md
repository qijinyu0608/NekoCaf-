# Runbook

## 当前状态

本仓库目前已经进入实验三开发阶段，但仍处于第一轮工程化落地早期。

当前默认口径：

- 只优先开发 `member-service` 和 `reservation-service`
- 先保证本地功能闭环
- 先以本地运行和本地测试为主
- Docker、Compose、CI/CD、Helm、观测按阶段逐步补齐

## Phase A 运行约定

1. 所有实现先以 `project/` 为唯一工程事实源。
2. 服务边界以实验二 OpenAPI 契约和 ADR 为准，不在实验三随意改业务边界。
3. 功能开发优先顺序为：
   - 先文档
   - 再最小功能
   - 再容器化
   - 最后流水线与观测

## 当前本地开发步骤

1. 进入 `project/`
2. 创建虚拟环境：`python3 -m venv .venv`
3. 安装依赖：`.venv/bin/pip install -e '.[dev]'`
4. 运行测试：`.venv/bin/pytest`
5. 单服务启动：
   - `make run-member`
   - `make run-reservation`

## 后续接管建议

1. 先根据实验一需求基线补齐接口说明。
2. 在实验二确认上下文边界后，再决定服务内部模块划分。
3. 在实验三 Phase B 跑通功能后，再继续补 Dockerfile、Compose 与 Helm。
4. 在实验三 Phase D 之后再整理 CI/CD、扫描截图和部署证据。
