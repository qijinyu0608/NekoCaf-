# Lab 3 Workspace

本目录承接实验三《DevOps 流水线与容器化部署》。

在整体开发路径中，`lab3` 预留给实验二定稿后的工程落地。这里后续应优先承接 `reservation-service` 与 `member-service` 的最小可运行实现，并补齐容器化、流水线、部署和观测证据。

当前建议按更可控的五阶段推进，原则是“文档和功能优先，外围能力后置”：

1. `Phase A` 先定边界与说明文档
2. `Phase B` 本地功能最小闭环
3. `Phase C` 容器化与本地起栈
4. `Phase D` 最小 CI/CD 与部署骨架
5. `Phase E` 观测与交付证据收尾

详细拆分说明统一维护在 [development-path.md](../development-path.md) 的 `Lab 3` 部分，后续开发默认按那份模块顺序执行。

- `source/`: Word、Excel、PPT 可编辑源文件
- `diagrams/`: 流水线图、拓扑图、Dashboard 设计稿
- `exports/`: 截图、扫描报告、导出 PDF
- `submission/`: 最终打包前的整理副本

## 当前已落地内容

- `D3-1`：已有 DevOps 设计骨架
- `D3-2`：`project/` 已形成双服务最小可运行 PoC
- `D3-3`：已补双服务 Dockerfile，并已验证 `docker compose up`
- `D3-4`：已补最小 `ci.yml`
- `D3-5`：已补最小 Helm Chart 骨架

当前最主要未完成项仍然是：

- `D3-3` 的扫描报告类证据
- `D3-6` 可观测性
- `D3-7` 到 `D3-9` 的最终交付材料
