# D3-3 Dockerfile 与镜像扫描报告

## 1. 当前范围

本轮实验三仅对两个核心服务提供容器化基线：

- `project/infra/docker/member.Dockerfile`
- `project/infra/docker/reservation.Dockerfile`

对应镜像名称：

- `project-member:latest`
- `project-reservation:latest`

## 2. Dockerfile 当前设计

当前 Dockerfile 保持最小化，目标是优先支撑本地 PoC 可构建、可启动、可演示：

1. 基础镜像统一使用 `python:3.12-slim`
2. 只复制 `pyproject.toml`、`libs/`、`services/`
3. 通过 `pip install .` 安装项目依赖
4. 分别以 `uvicorn` 启动 `member-service` 与 `reservation-service`

当前版本没有提前引入多阶段构建、非 root 用户、镜像签名等增强能力，原因是实验三当前阶段优先级仍然是“功能闭环与工程可复现优先”。

## 3. 本地构建与启动结果

本地已验证：

- `docker compose config` 通过
- `docker compose up --build -d` 可成功启动
- `member-service` 与 `reservation-service` 容器状态均为 `healthy`

本地访问验证：

- `http://127.0.0.1:8001/healthz`
- `http://127.0.0.1:8002/healthz`

## 4. 镜像扫描方式

当前采用 Trivy 容器方式进行扫描，避免要求宿主机额外安装扫描工具。由于目标是扫描本地已构建镜像，因此需要显式挂载 Docker socket。

参考命令：

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.cache/trivy:/root/.cache/trivy \
  aquasec/trivy:0.64.1 \
  image --scanners vuln --skip-version-check --severity HIGH,CRITICAL --ignore-unfixed project-member:latest

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.cache/trivy:/root/.cache/trivy \
  aquasec/trivy:0.64.1 \
  image --scanners vuln --skip-version-check --severity HIGH,CRITICAL --ignore-unfixed project-reservation:latest
```

## 5. 当前扫描结论

截至本报告编写时：

1. 扫描工具镜像已拉取成功。
2. 已定位并修正“扫描容器无法读取本地 Docker 镜像”的问题，修正方式是挂载 `/var/run/docker.sock`。
3. 当前网络环境下，Trivy 漏洞数据库首次下载速度较慢，完整漏洞结果仍以本机实际完成扫描时的终端输出为准。
4. 因此，本轮先将扫描方法、目标镜像和复核口径固定下来，作为实验三 `D3-3` 的基线版本。

## 6. 当前风险与后续优化

当前容器化基线仍有几个明确改进点：

1. 增加非 root 运行用户
2. 评估是否引入多阶段构建
3. 固化扫描结果留档
4. 将扫描接入 CI 或发布前检查流程

当前判断是：`D3-3` 已具备真实 Dockerfile 和可执行扫描方案，但最终提交前仍建议补充一次完整扫描结果截图或文本留档。
