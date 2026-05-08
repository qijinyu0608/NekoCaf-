# Lab 3 Submission Status

本目录用于跟踪实验三 `D3-1` 到 `D3-9` 的当前完成状态，避免提交前才临时盘点。

## 当前状态

- `D3-1` DevOps 设计方案：
  - 已补正式稿：`docs/lab3/source/D3-1_DevOps设计方案.md`
- `D3-2` 源代码与配置仓库：
  - 已具备 `project/` Monorepo、双服务、Docker Compose、README、Runbook、Rollback
- `D3-3` Dockerfile 与镜像相关材料：
  - 已具备 `member` 与 `reservation` Dockerfile
  - 已补基线报告：`docs/lab3/source/D3-3_Dockerfile与镜像扫描报告.md`
  - 已补扫描留档：`docs/lab3/exports/D3-3_trivy_member.txt`、`docs/lab3/exports/D3-3_trivy_reservation.txt`
- `D3-4` CI/CD 配置与运行说明：
  - 已补 `project/.github/workflows/ci.yml`
  - 已补说明文档：`docs/lab3/source/D3-4_CICD配置与运行说明.md`
  - 已补本地验证留档：`docs/lab3/exports/D3-4_local_ci_validation.txt`
- `D3-5` K8s 部署清单与 Helm Chart：
  - 已补最小 Helm 骨架
  - 已补说明文档：`docs/lab3/source/D3-5_Helm部署骨架说明.md`
- `D3-6` 可观测性配置与 Dashboard：
  - 已补最小可观测性基线
  - 已补说明文档：`docs/lab3/source/D3-6_可观测性配置与Dashboard说明.md`
  - 已补 Prometheus 与 metrics 留档：`docs/lab3/exports/`
- `D3-7` DORA 指标报告：
  - 已补基线报告：`docs/lab3/source/D3-7_DORA指标报告.md`
  - 已补表格版：`docs/lab3/source/D3-7_DORA指标报告.xlsx`
- `D3-8` 演示视频脚本：
  - 已补脚本稿：`docs/lab3/source/D3-8_演示视频脚本.md`
  - 演示输出已留档：`docs/lab3/exports/D3-6_demo_flow.txt`
- `D3-9` 答辩 PPT：
  - 暂未开始

## 当前判断

当前实验三已经完成到“可运行 PoC + 最小 CI + 最小 Helm 骨架 + 最小可观测性基线 + 基线交付文档 + 关键证据留档”的阶段，但还不属于最终提交态。

后续优先级建议：

1. 把 `D3-7` 表格版落成最终文件
2. 补 `D3-8` 的实际视频或录屏材料
3. 最后补 `D3-9` 答辩 PPT
