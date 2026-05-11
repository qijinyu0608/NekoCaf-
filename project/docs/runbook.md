# Runbook

## 当前运行形态

NekoCafé 当前已收束为单体 Web 应用：

- 单一 FastAPI 进程
- Jinja 页面
- 原生 JavaScript 交互
- SQLite 本地持久化

## 本地启动

1. 进入 `project/`
2. 创建虚拟环境：`python3.12 -m venv .venv`
3. 安装依赖：`.venv/bin/pip install -e '.[dev]'`
4. 运行测试：`.venv/bin/pytest -q`
5. 启动应用：`make run-app`

访问地址：

- 首页：`http://127.0.0.1:8000/`
- 店员后台：`http://127.0.0.1:8000/staff`
- 指标：`http://127.0.0.1:8000/metrics`

## 最小验收链路

1. 打开首页，确认看到：
   - 立即预约
   - 会员积分
   - 我的猫咪档案
   - 智能推荐
2. 点击体验会员或直接提交预约
3. 在会员中心查看积分和预约记录
4. 进入 `/staff`，点击进入后台
5. 查看今日预约并完成到店确认

## 容器化验证

```bash
make compose-up
docker compose ps
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:9090/-/healthy
make compose-down
```

## 可观测性检查

- 应用指标：`curl http://127.0.0.1:8000/metrics`
- Prometheus：`curl http://127.0.0.1:9090/api/v1/targets`
