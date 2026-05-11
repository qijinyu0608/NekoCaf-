# web-v0.2 开发证据

版本标签：`web-v0.2`
分支：`nekocafe-web-v1`
远端：`git@github.com:qijinyu0608/NekoCaf-.git`
日期：2026-05-11

## 1. 版本目标

根据 [NekoCafé 平台 PRD](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/product/nekocafe-platform-prd.md)，完成店员后台第一轮可运行接入。

本版本目标不是做完整门店运营系统，而是在现有顾客预约闭环之上补出一条真实可操作的店员链路：查看今日预约、按状态筛选、确认顾客到店，并继续保持后续复杂能力的扩展边界。

## 2. PRD 追溯

| PRD 编号 | 来源 | 本版本处理 |
| --- | --- | --- |
| `PRD-STAFF-001` | `UC-005` | 提供今日预约列表接口与店员工作台视图 |
| `PRD-STAFF-002` | `UC-005` | 提供到店确认接口和前端操作按钮 |
| `PRD-STAFF-003` | `UC-005` | 先保留迟到、爽约、改台入口说明，不伪装成已完成能力 |
| `PRD-STAFF-004` | `NFR-010` | 在店员列表中复用状态胶囊，区分已预约、已到店、已取消 |

## 3. 实现范围

### 3.1 后端

- 扩展 SQLite 预约数据访问层：支持门店预约列表查询、到店确认。
- 预约服务新增 `POST /reservation/v1/reservations/{reservationId}/check-in`。
- 预约服务新增 `GET /staff/v1/stores/{storeId}/reservations`。
- 继续保留 `X-Tenant-Id` 租户边界。

### 3.2 前端

- 平台导航中的“店员后台”从占位入口升级为真实工作台。
- 新增营业日期和预约状态筛选。
- 新增预约卡片、到店确认按钮与状态展示。
- 修正共享日期状态下的联动刷新，让顾客台和店员台在切换日期时保持一致。

### 3.3 测试与证据

- 新增后端测试：[test_staff_console_flow.py](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/project/tests/unit/test_staff_console_flow.py)
- 保存浏览器验收截图：
  - [web-v0.2-customer.png](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/development-evidence/artifacts/web-v0.2-customer.png)
  - [web-v0.2-staff.png](/Users/qijinyu.0608/Documents/software-engineering-labs-2026-spring/nekocafe-course-project/.worktrees/nekocafe-web-v1/docs/development-evidence/artifacts/web-v0.2-staff.png)

## 4. 关键验收路径

### 4.1 顾客创建预约

1. 打开 `http://127.0.0.1:5173/`
2. 保持 `2026-05-20` 和 `2` 人
3. 选择首个可预约时段
4. 点击“确认预约”
5. 顶部状态出现“预约已创建，已同步到我的预约。”

### 4.2 店员确认到店

1. 点击左侧“店员后台”
2. 查看当日预约列表
3. 点击“确认到店”
4. 顶部状态出现“店员后台已确认顾客到店。”
5. 卡片状态切换为“已到店”

## 5. 自动化验证

### 5.1 后端测试

命令：

```bash
./.venv/bin/pytest
```

结果：

```text
collected 29 items
tests/unit/test_lab2_batch1_data.py .....                                [ 17%]
tests/unit/test_lab2_batch2_data.py ......                               [ 37%]
tests/unit/test_lab2_batch3_data.py ...                                  [ 48%]
tests/unit/test_naming_conventions.py ..                                 [ 55%]
tests/unit/test_service_apps.py .......                                  [ 79%]
tests/unit/test_sqlite_reservation_flow.py ..                            [ 86%]
tests/unit/test_staff_console_flow.py .                                  [ 89%]
tests/unit/test_word_style_policy.py ...                                 [100%]
29 passed in 0.71s
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
dist/assets/index-kn1qoV1S.css            6.61 kB
dist/assets/index-Bm05ftJb.js           210.56 kB
✓ built in 1.30s
```

## 6. 浏览器验收

工具：Playwright 本地浏览器脚本

访问地址：

```text
http://127.0.0.1:5173/
```

实际结果：

- 顾客台成功创建预约，页面状态文案为“预约已创建，已同步到我的预约。”
- 店员后台可见预约列表，并成功执行到店确认。
- 店员后台状态文案为“店员后台已确认顾客到店。”
- 截图已保存到 `docs/development-evidence/artifacts/`。

脚本记录摘要：

```json
{
  "customerMessage": "预约已创建，已同步到我的预约。",
  "reservationCount": 1,
  "staffMessage": "店员后台已确认顾客到店。",
  "staffCount": 1,
  "hasCheckIn": true,
  "bookedCount": 0,
  "checkedInCount": 1
}
```

## 7. Git 交付要求

本版本完成后执行：

```bash
git add -A
git commit -m "feat(web): add PRD-traced staff console v0.2"
git tag web-v0.2
git push origin nekocafe-web-v1
git push origin web-v0.2
```

## 8. 下一版本入口

下一版本建议：`web-v0.3`

主题：异常处理和后台扩展

建议实现：

- 迟到、爽约、临时改台真实状态流转
- 店员后台异常高亮规则
- 猫咪健康模块数据模型和首个可见视图
- 运营看板最小只读指标面板
