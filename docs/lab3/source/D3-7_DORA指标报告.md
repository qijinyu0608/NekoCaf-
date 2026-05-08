# D3-7 DORA 指标报告

## 1. 报告口径

本报告只描述实验三当前阶段的真实工程状态，不把尚未接入的平台能力写成既成事实。

当前系统形态：

- 代码仓库：单仓 Monorepo
- 发布方式：本地 `docker compose up --build -d`
- CI：GitHub Actions 最小检查链路
- CD：Helm Chart 已有骨架，但尚未接入真实集群发布

因此，本报告中的 DORA 指标应理解为“实验三 PoC 阶段基线”，而不是生产环境运营指标。

## 2. 统计样本

本轮实验三相关提交样本：

1. `2026-05-08 13:50:39 +0800` `4477b05` `docs(lab3): define phase-a scope and delivery boundary`
2. `2026-05-08 13:55:53 +0800` `c9d3420` `feat(lab3): add minimal member and reservation flow`
3. `2026-05-08 13:59:41 +0800` `5b1db4e` `feat(lab3): tighten local container baseline`
4. `2026-05-08 14:40:17 +0800` `da10349` `feat(lab3): add minimal ci and helm baseline`

当前阶段部署样本：

1. 本地 `docker compose up --build -d`
2. 本地 `docker compose up --build -d member reservation`
3. 本地 `docker compose up -d prometheus`

## 3. 当前阶段 DORA 基线

| 指标 | 当前阶段口径 | 当前判断 |
| --- | --- | --- |
| Deployment Frequency | 以本地 Compose 部署/重建为准 | 高频，按需触发，可达到同日多次 |
| Lead Time for Changes | 以一次 Lab3 小批提交到本地可验证运行完成为准 | 小于 1 个工作日 |
| Change Failure Rate | 以“变更后需要立即修复或回退”的本地发布次数占比估算 | 当前批次未出现已确认发布失败，基线可记为 0 次 |
| Time to Restore Service | 以本地容器异常后恢复到 `/healthz` 与 `/metrics` 正常为准 | 分钟级，可通过重新构建和重启恢复 |

## 4. 指标解释

### Deployment Frequency

实验三当前以本地 PoC 为主，没有正式共享环境，因此部署频率不采用“每天上线几次”的生产口径，而是采用“是否可以稳定地小步发布和重建”。从当前分支的小批提交和多次本地 Compose 重建看，已经具备同日多次交付验证能力。

### Lead Time for Changes

从 `13:50` 到 `14:40` 的连续提交可以看出，本轮实验三的文档边界、功能闭环、容器化和最小 CI/Helm 骨架都在同一工作时段内完成并被验证，因此当前阶段更适合记录为“小于 1 个工作日”。

### Change Failure Rate

本轮开发过程中出现过 Docker 拉取基础镜像和 Prometheus 镜像的环境问题，但都属于本机网络与基础设施拉取问题，不是项目配置回归。当前没有出现“代码变更导致服务健康检查失败且无法在当轮修复”的已确认案例，因此当前基线暂记为 `0`。

### Time to Restore Service

当前恢复方式主要依赖：

1. 重新构建容器
2. 重启单个服务
3. 用 `/healthz`、`/metrics`、Prometheus target 状态验证恢复

从当前操作过程看，这个恢复时间属于分钟级。

## 5. 当前局限

当前 DORA 数据还不是自动采集，主要局限有：

1. 没有正式 CD 流水线
2. 没有统一发布记录表
3. 没有自动统计失败部署和恢复时间
4. 没有共享测试环境或生产环境数据

## 6. 后续升级建议

1. 将 CI 与后续 CD 事件写入统一发布日志
2. 给部署记录增加时间戳、版本号、执行人和结果状态
3. 给回滚操作增加标准命令和留痕
4. 在实验三最终提交前，将本报告同步整理成任务书模板要求的表格形式

当前判断是：实验三已经可以给出一版真实、可解释的 DORA 基线，但它仍然是课程 PoC 阶段的工程指标，而不是生产环境指标。
