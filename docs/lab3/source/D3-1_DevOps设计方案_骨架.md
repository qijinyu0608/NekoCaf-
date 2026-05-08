# D3-1 DevOps 设计方案骨架

本文档是实验三 `Phase A` 的设计骨架，目标不是一次写完最终版，而是先固定本轮开发边界，保证后续代码、容器化和交付件围绕同一主线推进。

## 1. 当前范围

- 项目形态：Monorepo
- 本轮优先服务：`reservation-service`、`member-service`
- 本轮目标：先形成最小可运行闭环，再继续补容器化、Compose、CI/CD、Helm、观测

## 2. 本轮不优先展开的内容

- 推荐域、门店运营域、猫咪健康域的真实服务实现
- 完整灰度发布与自动回滚
- 完整 Grafana Dashboard、告警联动和 DORA 报表取数闭环

## 3. 实验三简化开发顺序

1. `Phase A` 先定边界与说明文档
2. `Phase B` 本地功能最小闭环
3. `Phase C` 容器化与本地起栈
4. `Phase D` 最小 CI/CD 与部署骨架
5. `Phase E` 观测与交付证据收尾

## 4. 当前工程取舍

### 4.1 Monorepo 取舍

- 采用 Monorepo，原因是课程实验阶段更强调统一目录、统一依赖、统一文档和统一追溯。
- 两个核心服务共享 `libs/common/`，便于保持命名和基础约定一致。
- 相比 Polyrepo，这种结构更适合当前“文档、功能、测试、容器化逐步收口”的推进方式。

### 4.2 服务范围取舍

- 只把 `reservation-service` 与 `member-service` 做成真实可运行服务。
- 其他上下文继续保留在实验二文档和架构表达层，不在本轮扩展为真实代码服务。

## 5. Phase A 完成标准

- `project/README.md` 明确实验三当前范围和最小完成标准
- `project/docs/runbook.md` 明确本地开发步骤和阶段顺序
- `project/docs/rollback.md` 明确实验三早期的回退策略
- 团队对“先功能、后外围”的节奏达成一致

## 6. 下一阶段输入

Phase B 将基于实验二 OpenAPI，优先落最核心业务接口，形成至少一条可请求、可测试、可演示的业务链路。
