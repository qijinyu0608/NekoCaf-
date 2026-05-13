# NekoCafé v1

NekoCafé 当前实现已经从“React 前端 + 双 FastAPI 服务”收束为一个更容易继续演进的全栈单体：

- `FastAPI`
- `Jinja`
- 少量原生 JavaScript
- `SQLite`

本轮重点是把顾客首页先做成更像真实产品的预约站，同时保留最小店员后台，支撑实验三 `D3-2` 的可运行仓库和实验四后续测试闭环。

## 当前能力

- 顾客首页：立即预约、会员积分、我的猫咪档案、智能推荐
- 门店探索：多城市门店筛选、门店地址/营业时间/电话、可约时段摘要、直达预约
- 预约确认：预约详情、桌位信息、到店须知、取消入口
- 会员中心：积分、权益、下一次到店、预约记录
- 猫咪档案：当前会员关联猫咪资料
- 智能推荐：基于偏好的门店建议
- 店员后台：今日预约、状态筛选、到店确认
- 管理员后台：三类系统入口、权限概览、门店营业/暂停预约控制
- 单体会话：顾客 persona / 店员 persona / 管理员 persona
- 本地持久化：SQLite

## 目录

- `app/`: 单体应用代码、模板、静态资源
- `data/`: SQLite 数据文件
- `tests/`: 单元与页面级测试
- `infra/`: Docker 与观测配置
- `docs/`: runbook / rollback 等工程文档

## 本地开发

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
```

启动应用：

```bash
make run-app
```

默认地址：

- 首页：[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 门店探索：[http://127.0.0.1:8000/stores](http://127.0.0.1:8000/stores)
- 预约确认：`http://127.0.0.1:8000/reservations/{reservation_id}`
- 店员后台：[http://127.0.0.1:8000/staff](http://127.0.0.1:8000/staff)
- 管理员后台：[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- 权限管理：[http://127.0.0.1:8000/permissions](http://127.0.0.1:8000/permissions)
- 健康检查：[http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz)
- 指标：[http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)

## 最小演示链路

```bash
make demo-flow
```

该脚本会完成：

1. 建立顾客会话
2. 查询门店
3. 查询时段
4. 创建预约
5. 查询预约详情 API
6. 检查预约确认页面
7. 查询我的预约
8. 切换店员会话并查看今日预约

## 容器化

```bash
make compose-up
docker compose ps
make compose-down
```

Prometheus 会抓取单体应用的 `/metrics`。
