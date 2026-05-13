# NekoCafé 预约与推荐修复记录

## 本轮修复范围

1. 预约接口允许负数或 0 人数提交
2. 智能推荐评分没有跟随当前日期和人数筛选
3. 自定义下拉丢失 `optgroup` 分组层级
4. 预约创建存在并发超卖和顺序型 `reservation_id` 风险

## 问题根因

### 1. 非法预约人数
- 请求模型只校验了 `int`，没有限制必须大于 0
- 数据层 `create_reservation(...)` 也没有第二道防线

### 2. 推荐评分不一致
- 推荐逻辑固定用 `DEFAULT_DATE + 2人` 计算可约时段
- 页面切换日期、人数后，推荐理由没有同步变化

### 3. 城市分组丢失
- 模板里虽然用了 `optgroup`
- 但前端自定义下拉只平铺 `select.options`，没有渲染组标题

### 4. 并发预约风险
- 旧实现先查余位、再插入预约，不是原子操作
- `reservation_id` 使用 `COUNT(*) + 1`，在并发下可能撞号

## 修复方式

### 1. 预约人数双层校验
- `CreateReservationRequest.partySize` 改为正整数校验
- `create_reservation(...)` 增加 `party_size <= 0` 兜底校验
- 非法人数统一返回可读错误，不写入数据库

### 2. 推荐评分接入当前上下文
- `list_member_recommendations(...)` 新增：
  - `business_date`
  - `party_size`
  - `city_name`
  - `store_id`
- 首页、推荐页、`/api/recommendations/me` 统一使用当前筛选参数
- 推荐理由中的“可约时段”改为基于当前日期和人数实时生成

### 3. 自定义下拉保留分组
- `bindCustomSelects()` 改为遍历 `select.children`
- 对 `optgroup` 渲染 `custom-select-group-label`
- 组选项仍保留键盘上下切换与点击选择能力

### 4. 并发预约原子化
- `create_reservation(...)` 使用 `BEGIN IMMEDIATE`
- 在同一事务内完成：
  - 校验门店状态
  - 校验时段归属
  - 计算剩余容量
  - 判断是否可预约
  - 生成唯一 `reservation_id`
  - 插入预约
- `reservation_id` 改为 `res-<随机唯一串>`，不再依赖全局顺序号

## 修复前后关键行为摘要

### 修复前
- `partySize = -2` 会返回 `201`
- 推荐理由可能始终显示固定条件下的“可约时段 X 个”
- 城市分组在自定义下拉中不可见
- 两个并发预约请求可能同时成功

### 修复后
- `partySize <= 0` 返回 `422`
- 推荐页、首页、推荐 API 按当前 `date / partySize` 一致评分
- 分组标题在自定义下拉里可见
- 容量边界下并发预约只允许一个成功，另一个返回容量冲突

## 验证命令

```bash
./.venv/bin/pytest -q
bash scripts/demo_flow.sh
```

## 关键验证点

- 非法人数不落库
- 推荐结果会随日期、人数变化
- 分组城市下拉可见组标题
- 并发预约不会超卖，`reservation_id` 不再连续编号
