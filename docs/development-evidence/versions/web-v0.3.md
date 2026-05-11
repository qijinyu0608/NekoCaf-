# web-v0.3 开发证据

版本标签：`web-v0.3`
分支：`nekocafe-web-v1`
远端：`git@github.com:qijinyu0608/NekoCaf-.git`
日期：2026-05-11

## 1. 版本目标

根据 [NekoCafé 平台 PRD](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/product/nekocafe-platform-prd.md)，把原先的单页大组件重构成更接近真实餐饮系统的会话分层前端。

本版本聚焦三件事：

1. 把身份信息、登录状态、业务状态拆开。
2. 把顾客首页和店员后台拆成两个独立入口。
3. 把顾客侧 UI 改成更像真实咖啡预约站的风格，并隐藏具体桌号。

## 2. PRD 追溯

| PRD 编号 | 来源 | 本版本处理 |
| --- | --- | --- |
| `PRD-AUTH-001` | 产品策略 | 顾客与店员分入口 |
| `PRD-AUTH-002` | 产品策略 | 会话态、身份态、业务态分离 |
| `PRD-AUTH-003` | 产品策略 | 顾客只能访问自己的资料与预约 |
| `PRD-AUTH-004` | 产品策略 | 店员只能访问门店后台操作 |
| `PRD-CUS-001` | `FR-001`, `FR-010` | 顾客首页展示会员摘要 |
| `PRD-CUS-002` | `FR-002` | 顾客首页查询可预约时段 |
| `PRD-CUS-003` | `FR-003` | 顾客首页创建预约 |
| `PRD-CUS-004` | `FR-005` | 顾客首页查看我的预约 |
| `PRD-CUS-005` | `FR-004` | 顾客首页取消预约 |
| `PRD-CUS-006` | `FR-006` | 顾客侧隐藏桌号，仅展示主题/区域 |
| `PRD-STAFF-001` | `UC-005` | 店员后台查看今日预约 |
| `PRD-STAFF-002` | `UC-005` | 店员后台确认到店 |

## 3. 实现范围

### 3.1 后端

- 新增 mock session 能力，挂在 `member-service`。
- 新增 `POST /member/v1/session/login`、`GET /member/v1/session/me`、`POST /member/v1/session/logout`。
- 新增前端优先使用的 `me` 接口。
- 预约服务增加顾客/店员 session 权限判断。
- 顾客访问 staff 接口返回 403。

### 3.2 前端

- 拆出 `auth/`、`shell/`、`modules/` 三层结构。
- 引入路由，顾客首页与店员后台分开。
- 顾客首页采用 `Customer First` 入口。
- 店员后台采用独立 `/staff` 工作区。
- 顾客预约列表不展示具体桌号。

### 3.3 视觉与交互

- 使用新版 NekoCafé logo。
- 顾客首页保持工具型但温暖的预约站风格。
- 顾客与店员不再通过同页 tab 混用一个工作区。

## 4. 关键验收路径

### 4.1 顾客首页

1. 打开 `/`
2. 点击“继续预约”
3. 进入顾客会话
4. 查看会员摘要
5. 选择时段并创建预约
6. 在“我的预约”里看到新预约，且不显示桌号

### 4.2 店员后台

1. 打开 `/staff`
2. 点击“进入店员后台”
3. 查看今日预约
4. 点击“确认到店”
5. 看到状态变更为已到店

## 5. 自动化验证

### 5.1 后端测试

命令：

```bash
./.venv/bin/pytest -q
```

结果：

```text
33 passed in 0.63s
```

### 5.2 前端构建

命令：

```bash
npm run build
```

结果：

```text
vite v7.3.3 building client environment for production...
✓ 1722 modules transformed.
dist/assets/index-ljpEfBBM.js           252.25 kB
✓ built in 1.62s
```

## 6. 浏览器验收

工具：Playwright 本地浏览器脚本

访问地址：

```text
http://127.0.0.1:5173/
http://127.0.0.1:5173/staff
```

实际结果：

- 顾客首页可以进入会话并创建预约。
- 顾客预约列表只显示主题/区域，不显示桌号。
- 店员后台可以进入独立会话并看到今日预约。
- 店员后台可以确认到店。
- 会话刷新后可恢复；退出后回到匿名态。

脚本记录摘要：

```json
{
  "customerState": "预约已创建，已同步到我的预约。",
  "customerReservations": 1,
  "customerText": "05/20 18:00Sunset Window2 人 · 已预约\n已预约",
  "staffBefore": "已进入店员后台，可以查看今日预约。",
  "staffAfter": "店员后台已确认顾客到店。",
  "staffReservations": 1,
  "canCheckIn": true
}
```

截图：

- [web-v0.3-customer.png](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/development-evidence/artifacts/web-v0.3-customer.png)
- [web-v0.3-staff.png](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/development-evidence/artifacts/web-v0.3-staff.png)

## 7. Git 交付要求

本版本完成后执行：

```bash
git add -A
git commit -m "feat(web): split session and workspace layers v0.3"
git tag web-v0.3
git push origin nekocafe-web-v1
git push origin web-v0.3
```

## 8. 下一版本入口

下一版本建议：`web-v0.4`

主题：异常处理与后台扩展

建议实现：

- 迟到、爽约、临时改台真实状态流转
- 店员后台异常高亮规则
- 猫咪健康模块数据模型和首个可见视图
- 运营看板最小只读指标面板
