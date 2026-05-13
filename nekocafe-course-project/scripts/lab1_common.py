from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_DIR = ROOT / "docs" / "foundation"
LAB1_DIR = ROOT / "docs" / "lab1"
SOURCE_DIR = LAB1_DIR / "source"
DIAGRAM_DIR = LAB1_DIR / "diagrams"
EXPORT_DIR = LAB1_DIR / "exports"
SUBMISSION_DIR = LAB1_DIR / "submission"
BUILD_DIR = LAB1_DIR / ".build"

ARTIFACT_NAMES = {
    "D1-1": "RequirementsPlan",
    "D1-2": "RequirementsList",
    "D1-3": "SRS",
    "D1-4": "UMLModels",
    "D1-5": "GlossaryRTM",
    "D1-6": "ValidationReport",
    "D1-7": "AIRecord",
    "D1-8": "DefensePPT",
}

META = {
    "course": "软件工程",
    "header": "《软件工程》实验报告 — NekoCafé 项目",
    "suite_title": "NekoCafé 猫咪主题餐饮预约平台",
    "experiment": "实验一",
    "experiment_title": "智能化需求工程与 UML 建模",
    "class_name": "计算机23-2",
    "student_id": "231002208",
    "student_name": "戚晋瑜",
    "version": "v1.0",
    "date": "2026-05-07",
    "declaration": "本人承诺所提交的实验材料系本人独立完成，对引用的他人成果均已明确标注。AI 生成内容均在附录中说明使用范围与提示词，并由本人完成复核与定稿。",
}

STAKEHOLDERS = [
    {
        "id": "CUS-A",
        "role": "顾客代表 A",
        "layer": "核心用户层",
        "power": "中",
        "interest": "高",
        "focus": "预约流程顺滑、价格透明、与猫咪互动体验稳定",
        "persona": "高频周末到店的城市白领，偏好提前预约和主题桌位。",
    },
    {
        "id": "CUS-B",
        "role": "顾客代表 B",
        "layer": "核心用户层",
        "power": "中",
        "interest": "高",
        "focus": "带朋友聚会的预约可靠性、活动优惠、会员权益可见",
        "persona": "偶发性聚会用户，更关心改期、爽约和优惠券使用。",
    },
    {
        "id": "STA-1",
        "role": "店员代表",
        "layer": "运营执行层",
        "power": "高",
        "interest": "高",
        "focus": "排台效率、异常处理、猫咪健康记录的操作负担",
        "persona": "负责门店开台与现场协调，需要快速查看当日预约。",
    },
    {
        "id": "OPS-1",
        "role": "运营总监",
        "layer": "管理决策层",
        "power": "高",
        "interest": "中高",
        "focus": "跨店数据、活动投放效果、合规审计与门店复制效率",
        "persona": "关注集团层面经营指标，要求平台支撑标准化扩张。",
    },
]

INTERVIEW_QUESTIONS = {
    "顾客": [
        "你通常在什么场景下会使用猫咖预约平台？",
        "你决定是否下单时，最想先看到哪些门店信息？",
        "如果想指定桌位或猫咪互动主题，你期待平台怎么表达？",
        "你对预约成功后的确认方式和提醒频率有什么偏好？",
        "如果预约时段无空位，你希望看到什么替代方案？",
        "你如何看待定金、爽约规则和改期规则？",
        "会员权益怎样呈现，才会让你愿意长期使用？",
        "你在聚会场景下最担心哪些信息不透明？",
        "你是否需要系统给出桌位或菜品推荐？为什么？",
        "你对在线点单与到店核销之间的衔接有什么期待？",
        "你认为评价一次体验时，最关键的三个指标是什么？",
        "如果只能改进一件事，你最希望平台先优化哪一项？",
    ],
    "店员": [
        "门店在高峰期排台时最耗时的动作是什么？",
        "你接待预约顾客时，需要先核对哪些信息？",
        "如果出现爽约、迟到或现场改台，当前处理流程怎样？",
        "哪些异常情况最需要系统主动提醒？",
        "你希望桌位状态和猫咪状态以什么方式同时展现？",
        "记录猫咪健康打卡时，哪些字段必须保留？",
        "多人协作时，最容易出现什么信息冲突？",
        "如果门店当天临时关闭部分区域，系统应该怎么支持？",
        "你是否需要查看历史预约与顾客偏好？",
        "对于短信、电话、站内消息，哪种通知对你最有效？",
        "你最担心什么功能会增加一线门店负担？",
        "如果系统只能优先支持一个后台能力，你会选什么？",
    ],
    "运营总监": [
        "你最关注哪些跨门店经营指标？",
        "平台升级后，你希望总部得到哪些新的分析能力？",
        "会员运营与活动投放最需要追踪哪些数据？",
        "系统如何支撑新门店快速复制是你关心的吗？",
        "哪些合规与审计信息必须被留痕？",
        "你对 AI 推荐的业务目标和可解释性有什么要求？",
        "如果平台预算有限，你会优先建设哪些模块？",
        "对外部第三方系统接入，你最看重稳定性还是速度？",
        "当门店投诉上升时，你希望平台给出什么辅助判断？",
        "你认为预约数据与营收数据之间最关键的联动是什么？",
        "如果需要分阶段上线，你建议第一阶段的边界是什么？",
        "你对后续实验二到实验四的技术衔接有什么期望？",
    ],
}

RISKS = [
    ("R-01", "AI 幻觉导致需求细节失真", "中", "对关键事实进行人工复核，并在 SRS 中标注假设来源"),
    ("R-02", "顾客与店员术语不一致", "高", "统一以 Glossary 为准，对“桌位/台位/包间”等术语做别名映射"),
    ("R-03", "高层诉求过宽导致范围膨胀", "中", "通过 MoSCoW 和阶段边界将实验一范围控制在需求基线"),
    ("R-04", "图文表之间编号不一致", "高", "所有产物从同一份结构化数据生成，避免手工复制"),
    ("R-05", "访谈记录过长难以追溯", "低", "在原始对话中加入轮次编号和主题标签"),
]

FUNCTIONAL_REQUIREMENTS = [
    ("FR-001", "会员", "顾客可以注册并维护会员资料", "顾客代表 A", "Must", "P1", "Given 新用户访问注册页 When 提交合法信息 Then 系统创建会员账号", "BC-MEMBER", "member-service", "Baseline", "UC-001", "Member / MemberProfile"),
    ("FR-002", "预约", "顾客可以浏览门店与可预约时段", "顾客代表 A", "Must", "P1", "Given 顾客进入门店页 When 选择日期 Then 返回可预约时段", "BC-RESERVATION", "reservation-service", "Baseline", "UC-002", "Store / BusinessCalendar"),
    ("FR-003", "预约", "顾客可以创建桌位预约订单", "顾客代表 A", "Must", "P1", "Given 顾客已选择门店与时段 When 提交预约 Then 系统生成预约记录", "BC-RESERVATION", "reservation-service", "Baseline", "UC-003", "Reservation / ReservationOrder"),
    ("FR-004", "预约", "顾客可以取消未到店的预约", "顾客代表 B", "Should", "P2", "Given 存在有效预约 When 顾客取消 Then 状态更新为已取消且释放桌位", "BC-ORDER", "order-service", "Draft", "UC-004", "ReservationOrder"),
    ("FR-005", "预约", "顾客可以查看预约历史与当前状态", "顾客代表 B", "Must", "P2", "Given 顾客进入个人中心 When 打开预约记录 Then 系统展示历史状态列表", "BC-ORDER", "order-service", "Draft", "UC-004", "ReservationOrder"),
    ("FR-006", "预约", "顾客可以选择桌位偏好与互动主题", "顾客代表 A", "Should", "P2", "Given 顾客创建预约 When 选择偏好标签 Then 系统在可用桌位中优先匹配", "BC-RESERVATION", "reservation-service", "Draft", "UC-003", "TableSlot"),
    ("FR-007", "推荐", "系统可以推荐合适的桌位与猫咪互动主题", "运营总监", "Could", "P3", "Given 顾客填写偏好 When 提交推荐请求 Then 返回包含原因说明的推荐结果", "BC-RECOMMENDATION", "recommendation-service", "Draft", "UC-007", "RecommendationRule"),
    ("FR-008", "等位", "当目标时段满位时顾客可以加入等位", "顾客代表 B", "Should", "P2", "Given 时段无可用桌位 When 顾客选择等位 Then 系统创建等位记录并告知排序", "BC-RESERVATION", "reservation-service", "Draft", "UC-003", "WaitlistEntry"),
    ("FR-009", "通知", "系统可以向顾客发送预约确认与临近提醒", "顾客代表 A", "Must", "P2", "Given 预约创建成功 When 进入通知阶段 Then 系统发送确认消息与到店提醒", "BC-NOTIFICATION", "notification-service", "Draft", "UC-003", "NotificationTask"),
    ("FR-010", "会员", "会员可查看等级、积分与权益说明", "顾客代表 B", "Should", "P2", "Given 顾客进入会员中心 When 打开权益页 Then 展示等级和可用权益", "BC-MEMBER", "member-service", "Draft", "UC-009", "LoyaltyPointAccount / Coupon"),
    ("FR-011", "会员", "会员消费后可以累计积分", "运营总监", "Should", "P2", "Given 订单核销成功 When 结算完成 Then 系统按规则累积积分", "BC-MEMBER", "member-service", "Draft", "UC-009", "LoyaltyPointAccount"),
    ("FR-012", "会员", "会员可以使用优惠券抵扣符合条件的订单", "顾客代表 B", "Should", "P2", "Given 顾客满足使用条件 When 提交订单 Then 系统校验并抵扣优惠券", "BC-MEMBER", "member-service", "Draft", "UC-009", "Coupon"),
    ("FR-013", "门店运营", "店员可以查看当日预约并安排桌位", "店员代表", "Must", "P1", "Given 店员进入后台 When 查看当日排班 Then 系统展示预约与桌位占用", "BC-STORE-OPS", "store-ops-service", "Baseline", "UC-005", "ShiftSchedule / TableSlot"),
    ("FR-014", "门店运营", "店员可以标记顾客到店、入座和离店", "店员代表", "Must", "P1", "Given 顾客到店 When 店员点击状态按钮 Then 预约订单进入下一状态", "BC-STORE-OPS", "store-ops-service", "Draft", "UC-005", "ReservationOrder"),
    ("FR-015", "门店运营", "店员可以处理迟到、爽约和现场改台", "店员代表", "Must", "P1", "Given 预约出现异常 When 店员选择处置方式 Then 系统记录异常并更新资源占用", "BC-STORE-OPS", "store-ops-service", "Draft", "UC-005", "ReservationOrder / TableSlot"),
    ("FR-016", "猫咪健康", "店员可以记录猫咪健康打卡", "店员代表", "Must", "P2", "Given 店员进入猫咪档案页 When 填写体温与情绪 Then 系统保存打卡记录", "BC-CAT-HEALTH", "cat-health-service", "Draft", "UC-006", "CatProfile / HealthRecord"),
    ("FR-017", "猫咪健康", "店员可以查看猫咪互动限制与休息状态", "店员代表", "Should", "P2", "Given 店员查看猫咪列表 When 选择某只猫咪 Then 系统展示今日互动限制", "BC-CAT-HEALTH", "cat-health-service", "Draft", "UC-006", "CatProfile"),
    ("FR-018", "门店配置", "店长可以维护营业时间与闭店区间", "运营总监", "Should", "P2", "Given 店长进入门店配置 When 更新营业时间 Then 新时段立即参与预约计算", "BC-STORE-OPS", "store-ops-service", "Draft", "UC-008", "BusinessCalendar"),
    ("FR-019", "门店配置", "店长可以配置桌位容量、主题和可预约状态", "店员代表", "Should", "P2", "Given 门店调整桌位资源 When 保存配置 Then 系统刷新可预约资源池", "BC-STORE-OPS", "store-ops-service", "Draft", "UC-008", "TableSlot"),
    ("FR-020", "活动运营", "运营可以发起活动并绑定会员权益", "运营总监", "Could", "P3", "Given 运营创建活动 When 设定规则 Then 系统向目标会员展示活动入口", "BC-OPERATIONS", "ops-insight-service", "Draft", "UC-008", "ActivityCampaign"),
    ("FR-021", "活动运营", "运营可以查看跨门店预约转化数据", "运营总监", "Must", "P2", "Given 运营进入数据看板 When 选择时间范围 Then 系统展示跨门店预约漏斗", "BC-OPERATIONS", "ops-insight-service", "Baseline", "UC-008", "Reservation / ActivityCampaign"),
    ("FR-022", "活动运营", "运营可以查看会员复购与活动复用效果", "运营总监", "Should", "P2", "Given 运营查看经营指标 When 切换维度 Then 系统展示复购与活动拉动效果", "BC-OPERATIONS", "ops-insight-service", "Draft", "UC-008", "Member / ActivityCampaign"),
    ("FR-023", "点单", "顾客可以在预约后提前浏览菜品并提交预点单", "顾客代表 A", "Could", "P3", "Given 顾客拥有有效预约 When 打开菜单 Then 系统允许提交预点单", "BC-ORDER", "order-service", "Draft", "UC-010", "ReservationOrder"),
    ("FR-024", "点单", "顾客可以查看订单处理状态", "顾客代表 B", "Should", "P2", "Given 顾客打开订单中心 When 查看某笔订单 Then 系统展示支付、备餐和核销状态", "BC-ORDER", "order-service", "Draft", "UC-010", "ReservationOrder"),
    ("FR-025", "客服", "客服或店员可以补发预约通知", "店员代表", "Could", "P3", "Given 顾客未收到通知 When 店员点击补发 Then 系统重新触发消息任务", "BC-NOTIFICATION", "notification-service", "Draft", "UC-005", "NotificationTask"),
    ("FR-026", "客服", "系统可以保留预约异常的处理日志", "运营总监", "Must", "P2", "Given 店员处理异常 When 提交处置结果 Then 系统记录操作人、时间与原因", "BC-STORE-OPS", "store-ops-service", "Baseline", "UC-005", "AuditLog"),
    ("FR-027", "集成", "系统可以在短信网关失败时自动重试", "运营总监", "Should", "P2", "Given 发送通知失败 When 满足重试策略 Then 系统自动进入重试队列", "BC-NOTIFICATION", "notification-service", "Draft", "UC-003", "NotificationTask"),
    ("FR-028", "合规", "系统可以记录关键敏感操作审计日志", "运营总监", "Must", "P1", "Given 管理员访问敏感数据 When 执行查询或导出 Then 系统记录审计日志", "BC-OPERATIONS", "ops-insight-service", "Baseline", "UC-008", "AuditLog"),
    ("FR-029", "推荐", "推荐结果需要展示至少一条原因说明", "顾客代表 A", "Should", "P2", "Given 推荐服务返回结果 When 顾客查看详情 Then 系统展示可理解的推荐理由", "BC-RECOMMENDATION", "recommendation-service", "Draft", "UC-007", "RecommendationRule"),
    ("FR-030", "门店运营", "系统可以根据到店状态联动更新桌位占用", "店员代表", "Must", "P1", "Given 预约状态变化 When 顾客入座或离店 Then 桌位资源池同步更新", "BC-STORE-OPS", "store-ops-service", "Baseline", "UC-005", "TableSlot / ReservationOrder"),
]

NON_FUNCTIONAL_REQUIREMENTS = [
    ("NFR-001", "性能效率", "高峰期预约接口支持 5000 QPS", "总览文档", "Must", "P1", "峰值 5000 QPS 下错误率低于 1%", "BC-RESERVATION", "k6 压测", "Baseline"),
    ("NFR-002", "可靠性", "核心预约接口 SLA 不低于 99.9%", "总览文档", "Must", "P1", "月度可用性 >= 99.9%", "BC-RESERVATION", "Prometheus + SLO 报告", "Baseline"),
    ("NFR-003", "安全性", "个人信息处理需符合《个人信息保护法》", "运营总监", "Must", "P1", "敏感字段具备权限控制与脱敏规则", "BC-MEMBER", "安全测试 + 合规审查", "Baseline"),
    ("NFR-004", "可维护性", "新增门店上线需要做到零停机", "总览文档", "Should", "P2", "配置变更发布过程不影响已有门店服务", "BC-STORE-OPS", "变更演练", "Draft"),
    ("NFR-005", "易用性", "顾客端关键流程在移动端三步内完成预约", "顾客代表 A", "Should", "P2", "完成预约的主流程不超过 3 个关键操作页面", "BC-RESERVATION", "可用性走查", "Draft"),
    ("NFR-006", "兼容性", "顾客端需兼容微信小程序与主流移动浏览器", "顾客代表 B", "Should", "P2", "覆盖 iOS Safari、Android Chrome、微信小程序", "BC-RESERVATION", "兼容性测试", "Draft"),
    ("NFR-007", "安全性", "关键运营操作需保留不少于 180 天的审计日志", "运营总监", "Must", "P2", "敏感操作日志保留 >= 180 天且支持检索", "BC-OPERATIONS", "日志审计检查", "Draft"),
    ("NFR-008", "可移植性", "核心服务可在容器环境中部署", "总览文档", "Should", "P2", "服务镜像化后可在统一运行环境启动", "BC-RESERVATION", "容器化验证", "Draft"),
    ("NFR-009", "功能适合性", "推荐结果需在 2 秒内返回并说明原因", "运营总监", "Could", "P3", "P95 推荐响应时间 <= 2s 且解释字段非空", "BC-RECOMMENDATION", "接口测试", "Draft"),
    ("NFR-010", "易用性", "店员后台应支持异常状态颜色区分", "店员代表", "Should", "P2", "异常预约在后台列表中 1 秒内可识别", "BC-STORE-OPS", "可用性走查", "Draft"),
]

GLOSSARY = [
    ("会员", "Member", "在平台中拥有注册资料与消费权益的顾客", "用户", "游客", "实验一需求获取"),
    ("预约", "Reservation", "顾客针对门店、时段和桌位发起的占位请求", "订位", "临时到店", "实验一需求获取"),
    ("预约订单", "Reservation Order", "系统持久化后的预约记录实体", "预约记录", "草稿请求", "实验一 SRS"),
    ("桌位", "Table Slot", "门店内可被预约的最小服务单元", "台位", "不可预约资源", "实验一需求获取"),
    ("营业日历", "Business Calendar", "描述门店营业时间、闭店区间和节假日策略的数据实体", "营业时间表", "临时口头通知", "实验一需求分析"),
    ("猫咪档案", "Cat Profile", "记录门店猫咪基础信息、互动偏好与限制的数据对象", "猫咪资料", "匿名猫咪", "实验一需求分析"),
    ("健康打卡", "Health Record", "门店对猫咪健康状态进行的周期性记录", "健康巡检", "无记录状态", "实验一需求分析"),
    ("限界上下文", "Bounded Context", "DDD 中用于界定模型边界的上下文范围", "上下文", "共享大模型", "实验二设计"),
    ("服务", "Service", "在 monorepo 中可独立部署的业务单元", "微服务", "单体模块", "实验三设计"),
    ("推荐规则", "Recommendation Rule", "用于生成桌位与互动推荐的业务规则集合", "推荐策略", "随机推荐", "实验一扩展需求"),
    ("审计日志", "Audit Log", "记录关键业务操作人、动作、时间和结果的追踪数据", "操作日志", "匿名行为", "实验一合规需求"),
    ("测试用例", "Test Case", "用于验证需求与质量目标的执行步骤集合", "TC", "随机检查", "实验四测试计划"),
]

USE_CASES = [
    {
        "id": "UC-001",
        "name": "注册与维护会员资料",
        "actor": "顾客",
        "preconditions": ["顾客具备手机号或第三方登录能力"],
        "main_flow": ["顾客进入注册页", "填写手机号、昵称与偏好", "系统校验并创建会员账号", "顾客可补充生日、忌口、猫咪偏好"],
        "alt_flow": ["若手机号已存在，则引导顾客找回账号"],
        "exceptions": ["注册验证码校验失败时提示重试"],
        "postconditions": ["会员账号创建成功并可进入个人中心"],
        "related_requirements": ["FR-001", "FR-010"],
    },
    {
        "id": "UC-002",
        "name": "浏览门店与可预约时段",
        "actor": "顾客",
        "preconditions": ["门店营业日历已配置"],
        "main_flow": ["顾客筛选城市与门店", "系统展示门店标签与可预约时段", "顾客查看桌位主题与互动规则"],
        "alt_flow": ["若无对应门店，则提示附近可选门店"],
        "exceptions": ["门店临时闭店时不展示可预约时段"],
        "postconditions": ["顾客完成下单前的门店筛选"],
        "related_requirements": ["FR-002", "FR-006"],
    },
    {
        "id": "UC-003",
        "name": "创建桌位预约",
        "actor": "顾客",
        "preconditions": ["顾客已选择门店、日期和人数"],
        "main_flow": ["系统校验空余桌位", "顾客选择时段与偏好", "系统创建预约订单", "系统触发通知任务"],
        "alt_flow": ["若无空位则引导进入等位或推荐附近门店"],
        "exceptions": ["消息网关失败时进入重试队列"],
        "postconditions": ["生成预约记录并通知顾客"],
        "related_requirements": ["FR-003", "FR-008", "FR-009", "FR-027"],
    },
    {
        "id": "UC-004",
        "name": "管理预约历史与取消",
        "actor": "顾客",
        "preconditions": ["顾客已有有效预约记录"],
        "main_flow": ["顾客打开预约列表", "选择某笔预约查看详情", "在规则允许时发起取消"],
        "alt_flow": ["若顾客仅查看历史，则保留原状态"],
        "exceptions": ["超过可取消时限时提示人工联系门店"],
        "postconditions": ["预约记录状态被更新并保留历史轨迹"],
        "related_requirements": ["FR-004", "FR-005"],
    },
    {
        "id": "UC-005",
        "name": "店员排台与异常处理",
        "actor": "店员",
        "preconditions": ["门店已进入营业日且预约列表可见"],
        "main_flow": ["店员查看今日预约", "按到店情况分配桌位", "标记到店、入座、离店", "处理迟到或爽约异常"],
        "alt_flow": ["若顾客临时改台，则重新匹配桌位并通知后厨"],
        "exceptions": ["资源冲突时给出高优先级预约提示"],
        "postconditions": ["桌位状态与预约状态保持同步"],
        "related_requirements": ["FR-013", "FR-014", "FR-015", "FR-025", "FR-026", "FR-030"],
    },
    {
        "id": "UC-006",
        "name": "猫咪健康打卡",
        "actor": "店员",
        "preconditions": ["猫咪档案已建立"],
        "main_flow": ["店员选择猫咪档案", "录入体温、食量、情绪与互动限制", "系统保存健康打卡"],
        "alt_flow": ["若出现异常指标，则提醒减少互动时段"],
        "exceptions": ["缺失关键字段时阻止提交"],
        "postconditions": ["猫咪健康档案得到更新"],
        "related_requirements": ["FR-016", "FR-017"],
    },
    {
        "id": "UC-007",
        "name": "AI 推荐桌位与主题",
        "actor": "顾客",
        "preconditions": ["顾客已填写人数、偏好或历史数据可用"],
        "main_flow": ["顾客请求推荐", "系统匹配桌位与猫咪主题", "返回带原因说明的推荐结果"],
        "alt_flow": ["若数据不足，则退化为热门组合推荐"],
        "exceptions": ["推荐服务超时时返回规则兜底结果"],
        "postconditions": ["顾客获得可解释的推荐方案"],
        "related_requirements": ["FR-007", "FR-029"],
    },
    {
        "id": "UC-008",
        "name": "运营分析与门店配置",
        "actor": "运营总监 / 店长",
        "preconditions": ["跨门店业务数据已汇总"],
        "main_flow": ["运营查看预约漏斗、复购与活动效果", "店长维护营业时间与桌位配置", "系统保存变更并生成审计记录"],
        "alt_flow": ["若仅查看报表，则不触发配置变更流程"],
        "exceptions": ["敏感操作未授权时拒绝访问并记审计日志"],
        "postconditions": ["经营分析与配置结果可追溯"],
        "related_requirements": ["FR-018", "FR-019", "FR-020", "FR-021", "FR-022", "FR-028"],
    },
    {
        "id": "UC-009",
        "name": "会员积分与优惠券",
        "actor": "顾客",
        "preconditions": ["顾客已成为会员"],
        "main_flow": ["顾客查看积分与优惠券", "订单完成后累计积分", "符合条件时核销优惠券"],
        "alt_flow": ["若优惠券过期，则提示不可使用原因"],
        "exceptions": ["积分规则异常时转人工核查"],
        "postconditions": ["会员权益状态与订单结果保持一致"],
        "related_requirements": ["FR-011", "FR-012"],
    },
    {
        "id": "UC-010",
        "name": "预约关联预点单与订单追踪",
        "actor": "顾客",
        "preconditions": ["顾客已有有效预约"],
        "main_flow": ["顾客浏览菜单并提交预点单", "系统保存订单", "顾客查看支付、备餐和核销状态"],
        "alt_flow": ["若顾客未点单，则保留预约主流程"],
        "exceptions": ["库存不足时阻止提交并提示替代菜品"],
        "postconditions": ["预约与订单状态链路打通"],
        "related_requirements": ["FR-023", "FR-024"],
    },
]

VALIDATION_CHECKLIST = [
    "每条功能需求均具备唯一 ID、来源、验收准则和状态。",
    "SRS 中的术语均在 Glossary 中出现并保持一致。",
    "关键 UML 图均能追溯到至少一条需求条目。",
    "所有 Must 类需求都进入了基线并具备验证方式。",
    "对 AI 生成内容均给出人工复核和修订说明。",
]

DEFECTS = [
    ("D-001", "二义性", "FR-006", "桌位偏好的候选值未限定，前端和后台可能理解不一致", "M", "补充偏好枚举和示例", "已修复"),
    ("D-002", "冲突", "FR-004 ↔ FR-015", "顾客取消规则与门店爽约处理规则初稿存在时限冲突", "H", "以门店营业前 2 小时为统一阈值", "已修复"),
    ("D-003", "缺失", "FR-009", "提醒消息缺少失败重试策略", "M", "新增 FR-027 作为补充需求", "已修复"),
    ("D-004", "二义性", "NFR-005", "“三步内完成预约”未说明是否包含登录步骤", "L", "将指标定义为关键业务页面数，不含登录授权", "已修复"),
    ("D-005", "缺失", "UC-006", "猫咪异常健康指标没有对应异常分流", "M", "在活动图和用例异常流中增加人工复核", "已修复"),
    ("D-006", "冲突", "FR-020 ↔ NFR-003", "活动触达策略与个保法授权边界表达不足", "H", "补充仅对授权会员推送活动的限制", "待后续评审"),
]

AI_PROMPTS = [
    {
        "title": "访谈剧本生成",
        "version": "v1",
        "purpose": "为顾客、店员和运营总监生成半结构化访谈大纲",
        "prompt": "请你扮演软件工程课程中的需求分析助手，围绕 NekoCafé 猫咪主题餐饮预约平台，分别为顾客、店员、运营总监生成不少于 12 个访谈问题。要求问题覆盖目标、痛点、异常场景、合规诉求和对 AI 推荐的看法。",
    },
    {
        "title": "需求归并与 MoSCoW 分级",
        "version": "v2",
        "purpose": "将访谈原始描述整理为 FR/NFR 主表",
        "prompt": "请将以下访谈纪要整理成功能需求和非功能需求，并给出来源、MoSCoW、优先级以及 Given-When-Then 验收准则。保持 FR/NFR 编号格式统一，并标注是否适合作为实验一基线。",
    },
    {
        "title": "SRS 文字润色",
        "version": "v1",
        "purpose": "统一 SRS 正文的书面风格",
        "prompt": "请在不改变需求含义的前提下，将以下软件需求规格说明书片段润色为更符合 IEEE 830 风格的中文技术文档，保持术语、编号和约束不变。",
    },
    {
        "title": "AI 反向质询",
        "version": "v1",
        "purpose": "发现需求缺陷和冲突",
        "prompt": "请扮演一名挑剔的软件产品经理，针对以下 NekoCafé SRS 至少指出 5 处潜在二义性、冲突或缺失，并说明为什么这些问题会影响后续设计、开发或测试。",
    },
]

REFERENCES = [
    "ISO/IEC/IEEE 29148:2018 Systems and software engineering — Life cycle processes — Requirements engineering.",
    "IEEE Std 830-1998 Recommended Practice for Software Requirements Specifications.",
    "Sommerville I. Software Engineering (10th Edition). Pearson, 2015.",
    "张海藩, 吕云翔. 软件工程（第 4 版）. 人民邮电出版社, 2021.",
    "PlantUML 官方文档. https://plantuml.com/zh/",
    "Conventional Commits. https://www.conventionalcommits.org/zh-hans/",
]

TBD_ITEMS = [
    ("TBD-01", "推荐规则是否需要引入实时天气因子", "运营总监", "实验二架构设计前"),
    ("TBD-02", "预点单是否纳入实验三 PoC 范围", "本人", "实验三任务拆解时"),
    ("TBD-03", "跨店会员画像是否需要脱敏下发", "课程组", "实验四质量评审前"),
]

SLIDES = [
    ("封面", ["实验一：智能化需求工程与 UML 建模", "NekoCafé 猫咪主题餐饮预约平台", "计算机23-2 231002208 戚晋瑜"]),
    ("个人分工", ["需求获取与整合", "UML 建模与 RTM 维护", "SRS、验证报告、AI 记录整理"]),
    ("案例与干系人地图", ["NekoCafé 统一案例背景", "顾客 / 店员 / 运营总监关注点"]),
    ("需求获取过程", ["AI 访谈脚本设计", "4 类模拟访谈", "MoSCoW 归并与人工复核"]),
    ("需求清单概览", ["30 条功能需求", "10 条非功能需求", "统一编号和 Given-When-Then"]),
    ("主用例图", ["顾客、店员、运营三类角色", "预约、会员、运营分析主链路"]),
    ("活动与顺序图", ["桌位预约活动流", "跨服务调用顺序流"]),
    ("类图与状态图", ["12+ 核心实体", "订单生命周期状态机"]),
    ("非功能需求与合规", ["SLA / QPS / 兼容性 / 合规", "个保法与审计日志要求"]),
    ("需求验证发现", ["二义性、冲突、缺失缺陷样例", "v1.0 是否可冻结"]),
    ("后续实验输入", ["实验二继续沿用 FR/NFR/UC/BC", "实验三聚焦 member + reservation"]),
    ("Q&A", ["欢迎提问", "可继续展开需求、图稿或 RTM 细节"]),
]


def ensure_dirs() -> None:
    for path in [SOURCE_DIR, DIAGRAM_DIR, EXPORT_DIR, SUBMISSION_DIR, BUILD_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def artifact_filename(code: str, extension: str) -> str:
    short = ARTIFACT_NAMES[code]
    return f"{META['class_name']}_{META['student_id']}_{META['student_name']}_{META['experiment']}_{short}_{META['version']}.{extension}"


def artifact_stem(code: str) -> str:
    short = ARTIFACT_NAMES[code]
    return f"{META['class_name']}_{META['student_id']}_{META['student_name']}_{META['experiment']}_{short}_{META['version']}"


def build_data() -> dict:
    return {
        "meta": META,
        "artifact_names": ARTIFACT_NAMES,
        "stakeholders": STAKEHOLDERS,
        "interview_questions": INTERVIEW_QUESTIONS,
        "risks": RISKS,
        "functional_requirements": [
            {
                "id": row[0],
                "category": row[1],
                "description": row[2],
                "source": row[3],
                "moscow": row[4],
                "priority": row[5],
                "acceptance": row[6],
                "context": row[7],
                "service": row[8],
                "status": row[9],
                "use_case": row[10],
                "entity": row[11],
            }
            for row in FUNCTIONAL_REQUIREMENTS
        ],
        "non_functional_requirements": [
            {
                "id": row[0],
                "iso": row[1],
                "description": row[2],
                "source": row[3],
                "moscow": row[4],
                "priority": row[5],
                "metric": row[6],
                "context": row[7],
                "verification": row[8],
                "status": row[9],
            }
            for row in NON_FUNCTIONAL_REQUIREMENTS
        ],
        "glossary": [
            {
                "term": row[0],
                "english": row[1],
                "definition": row[2],
                "synonym": row[3],
                "antonym": row[4],
                "source": row[5],
            }
            for row in GLOSSARY
        ],
        "use_cases": USE_CASES,
        "validation_checklist": VALIDATION_CHECKLIST,
        "defects": [
            {
                "id": row[0],
                "type": row[1],
                "requirement": row[2],
                "description": row[3],
                "severity": row[4],
                "action": row[5],
                "status": row[6],
            }
            for row in DEFECTS
        ],
        "ai_prompts": AI_PROMPTS,
        "references": REFERENCES,
        "tbd_items": TBD_ITEMS,
        "slides": SLIDES,
    }


def export_json(path: Path | None = None) -> Path:
    ensure_dirs()
    target = path or (BUILD_DIR / "lab1_data.json")
    target.write_text(json.dumps(build_data(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def customer_personas() -> list[dict]:
    return [item for item in STAKEHOLDERS if item["role"].startswith("顾客")]


def build_transcript(persona_name: str, role_type: str) -> list[tuple[str, str]]:
    if role_type == "顾客":
        themes = [
            ("使用场景", "我通常会在周末聚会或约会前 2 到 3 天打开平台，先确认门店氛围和空位。"),
            ("门店信息", "门店距离、是否有安静区域、猫咪互动规则和人均价格，是我最先看的信息。"),
            ("主题偏好", "如果能提前看到桌位主题和猫咪性格标签，我会更愿意下单。"),
            ("提醒方式", "我希望预约后先收到确认消息，出发前 2 小时再有一次提醒。"),
            ("无空位处理", "如果没有空位，我希望系统给出等位、附近门店和改期建议。"),
            ("改期规则", "定金和改期规则必须在下单页写清楚，不然用户会没有安全感。"),
            ("会员权益", "如果会员等级、积分和优惠券展示清楚，我会更愿意持续使用。"),
            ("聚会顾虑", "多人到店时我最怕现场桌位和线上预约不一致，或者互动规则说不清。"),
            ("AI 推荐", "推荐可以有，但一定要说明为什么给我这个结果，不然很像盲盒。"),
            ("体验改进", "如果只能改一件事，我希望先把预约成功后的信息透明度做好。"),
        ]
    elif role_type == "店员":
        themes = [
            ("高峰动作", "高峰时最耗时的是确认预约状态、现场来客和桌位清洁状态三件事。"),
            ("核对信息", "顾客到店后我需要核对预约姓名、手机号、人数和是否有特殊互动限制。"),
            ("异常处理", "迟到、爽约和临时改台是最常见的异常，目前最怕信息不同步。"),
            ("主动提醒", "我希望系统自动标红即将超时未到店的预约。"),
            ("桌位与猫咪", "桌位状态和猫咪健康状态必须同屏展示，不然很容易调度冲突。"),
            ("健康打卡", "体温、食量、情绪和今日互动限制是必须保留的核心字段。"),
            ("协作冲突", "多人交接班时最怕一个人改了桌位，另一个人还在看旧状态。"),
            ("临时闭区", "如果某区域临时关闭，系统要能马上把相关桌位下架。"),
            ("历史偏好", "能看到顾客历史偏好会很有帮助，尤其是生日、忌口和互动禁忌。"),
            ("后台优先项", "如果后台只能优先做一个能力，我会先选排台和异常联动。"),
        ]
    else:
        themes = [
            ("经营指标", "我最关注预约转化、翻台率、会员复购和活动拉新效果。"),
            ("总部能力", "平台升级后，我希望总部能统一看跨店数据，而不是各店各报。"),
            ("会员运营", "活动投放必须能看到触达、到店和复购的完整漏斗。"),
            ("门店复制", "新门店上线时，营业时间和桌位模板最好能快速复用。"),
            ("合规留痕", "所有敏感数据访问和关键配置变更都要可审计。"),
            ("推荐要求", "AI 推荐可以试，但必须服务业务目标，还要给出解释字段。"),
            ("阶段边界", "如果分阶段上线，我建议先做会员、预约和门店运营三条主线。"),
            ("数据联动", "我需要看到预约数据如何影响营收、复购和活动效果。"),
            ("异常感知", "当某门店投诉突然上升时，平台要能帮助我快速定位原因。"),
            ("后续实验", "我希望实验二到实验四继续沿用实验一的编号体系和术语表。"),
        ]

    transcript: list[tuple[str, str]] = []
    for topic, answer in themes:
        transcript.append((f"请你结合 {topic} 描述最真实的业务需求。", answer))
        transcript.append((f"如果 {topic} 处理不好，会给你带来什么直接影响？", f"{persona_name} 表示，如果 {topic} 缺乏清晰规则，就会造成体验波动、现场协调压力或经营判断偏差。"))
        transcript.append((f"针对 {topic}，你最希望平台补上的一个细节是什么？", f"{persona_name} 希望平台在 {topic} 上提供更明确的状态、解释和异常兜底，减少人工二次确认。"))
    return transcript


if __name__ == "__main__":
    export_json()
