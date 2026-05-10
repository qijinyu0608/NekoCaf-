# web-v0.1 开发证据

版本标签：`web-v0.1`
分支：`nekocafe-web-v1`
远端：`git@github.com:qijinyu0608/NekoCaf-.git`
日期：2026-05-10

## 1. 版本目标

根据 `docs/product/nekocafe-platform-prd.md`，完成 NekoCafé 平台首个可运行 Web 版本。

本版本聚焦顾客预约台，形成从会员信息读取、可预约时段查询、创建预约、查看我的预约、取消预约到 SQLite 持久化的最小闭环。

## 2. PRD 追溯

| PRD 编号 | 来源 | 本版本处理 |
| --- | --- | --- |
| `PRD-CUS-001` | `FR-001`, `FR-010` | 展示会员昵称、脱敏手机号、等级、积分 |
| `PRD-CUS-002` | `FR-002`, `UC-002` | 支持按日期和人数查询门店可预约时段 |
| `PRD-CUS-003` | `FR-003`, `UC-003` | 支持选择时段并创建预约 |
| `PRD-CUS-004` | `FR-005`, `UC-004` | 支持查看我的预约列表 |
| `PRD-CUS-005` | `FR-004`, `UC-004` | 支持取消已预约记录 |
| `PRD-CUS-006` | `FR-006`, `UC-003` | 展示时段主题、容量和桌位 |
| `NFR-005` | 顾客端三步内完成预约 | 首屏完成日期/人数、选时段、确认预约 |

## 3. 实现范围

### 3.1 后端

- 新增 SQLite 数据层：`project/libs/common/database.py`
- 新增运行时数据库目录：`project/data/`
- 会员服务改为读取 SQLite。
- 预约服务改为读取 SQLite。
- 预约记录持久化到 `reservations` 表。
- 新增取消预约接口。
- 保留 `X-Tenant-Id` 租户头。
- 保留 `/healthz` 和 `/metrics`。

### 3.2 前端

- 新增 React/Vite/TypeScript 工程：`project/frontend/`
- 使用真实 logo：`project/frontend/src/assets/nekocafe-logo.png`
- 首屏采用平台型工作台布局。
- 已激活顾客预约台。
- 预留店员后台、猫咪健康、运营看板、推荐权益入口。

### 3.3 文档

- 新增产品 PRD：`docs/product/nekocafe-platform-prd.md`
- 新增开发证据目录：`docs/development-evidence/`
- 更新 `project/README.md`，加入 PRD 链接和前端启动说明。

## 4. 关键验收路径

### 4.1 顾客预约路径

1. 打开 `http://127.0.0.1:5173/`
2. 查看会员状态。
3. 选择 `2026-05-20` 和 `2` 人。
4. 选择 `18:00 Sunset Window`。
5. 点击“确认预约”。
6. 我的预约出现 `05/20 18:00`、`store-shanghai-001`、`2 人 · T1`、`已预约`。
7. 点击取消按钮。
8. 状态变为 `已取消`。

### 4.2 后续能力入口

首屏必须可见或可滚动到：

- 店员后台
- 猫咪健康
- 运营看板
- 后续后台能力：店员工作台、猫咪健康台账、推荐与权益

## 5. 自动化验证

### 5.1 后端测试

命令：

```bash
.venv/bin/pytest
```

结果：

```text
collected 28 items
tests/unit/test_lab2_batch1_data.py .....                                [ 17%]
tests/unit/test_lab2_batch2_data.py ......                               [ 39%]
tests/unit/test_lab2_batch3_data.py ...                                  [ 50%]
tests/unit/test_naming_conventions.py ..                                 [ 57%]
tests/unit/test_service_apps.py .......                                  [ 82%]
tests/unit/test_sqlite_reservation_flow.py ..                            [ 89%]
tests/unit/test_word_style_policy.py ...                                 [100%]
28 passed in 0.55s
```

### 5.2 前端构建

命令：

```bash
make build-web
```

结果：

```text
vite v7.3.3 building client environment for production...
✓ 1702 modules transformed.
dist/index.html                           0.41 kB
dist/assets/nekocafe-logo-DdFOyLEz.png  947.47 kB
dist/assets/index-Lmq9ngjA.css            6.21 kB
dist/assets/index-DZN-U607.js           206.02 kB
✓ built in 1.37s
```

## 6. 浏览器验证

工具：Codex in-app browser

访问地址：

```text
http://127.0.0.1:5173/
```

观察结果：

- 页面标题为 `NekoCafé Reservation`。
- 真实 PNG logo 可见，布局没有被图片尺寸撑坏。
- 会员状态、平台模块、顾客预约台、我的预约和后续后台能力区域可见。
- 创建预约后列表显示 `2 人 · T1`。
- 取消预约后状态显示 `已取消`。

## 7. Git 交付要求

本版本完成后执行：

```bash
git add -A
git commit -m "feat(web): add PRD-traced customer reservation platform v0.1"
git tag web-v0.1
git push origin nekocafe-web-v1
git push origin web-v0.1
```

## 8. 后续版本入口

下一版本建议：`web-v0.2`

主题：店员后台骨架

建议实现：

- 今日预约列表
- 预约状态筛选
- 到店确认入口
- 迟到/爽约异常状态展示
- 店员后台 UI 与顾客预约台共用平台导航
