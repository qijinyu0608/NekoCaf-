from __future__ import annotations

from pathlib import Path

from lab1_common import (
    FUNCTIONAL_REQUIREMENTS,
    GLOSSARY,
    META as LAB1_META,
    NON_FUNCTIONAL_REQUIREMENTS,
)


ROOT = Path(__file__).resolve().parents[1]
LAB2_DIR = ROOT / "docs" / "lab2"
SOURCE_DIR = LAB2_DIR / "source"
DIAGRAM_DIR = LAB2_DIR / "diagrams"
EXPORT_DIR = LAB2_DIR / "exports"
SUBMISSION_DIR = LAB2_DIR / "submission"
BUILD_DIR = LAB2_DIR / ".build"

ARTIFACT_NAMES = {
    "D2-1": "QualityUtilityTree",
    "D2-2": "EventStormingContextMap",
    "D2-3": "ArchitectureATAM",
}

META = {
    **LAB1_META,
    "experiment": "实验二",
    "experiment_title": "软件架构设计与微服务拆分实践",
    "date": "2026-05-07",
}

QUALITY_ATTRIBUTE_SCENARIOS = [
    {
        "id": "QAS-001",
        "source_nfr": "NFR-001",
        "quality": "性能效率",
        "stimulus_source": "高峰期顾客流量",
        "stimulus": "午晚餐高峰同时发起预约请求",
        "artifact": "reservation-service",
        "environment": "节假日高峰期，活动促销同时在线",
        "response": "完成预约时段查询与预占校验，不阻塞其他核心链路",
        "response_measure": "5000 QPS 下 P95 < 800ms，错误率 < 1%",
        "priority": "H",
        "driver": "5000 QPS",
    },
    {
        "id": "QAS-002",
        "source_nfr": "NFR-002",
        "quality": "可靠性",
        "stimulus_source": "业务监控与顾客请求",
        "stimulus": "核心预约服务出现单点异常或瞬时抖动",
        "artifact": "预约主链路",
        "environment": "门店正常营业时段",
        "response": "系统自动隔离故障并维持关键预约能力可用",
        "response_measure": "月度 SLA >= 99.9%，故障恢复时间 < 10 分钟",
        "priority": "H",
        "driver": "核心服务高可用",
    },
    {
        "id": "QAS-003",
        "source_nfr": "NFR-003",
        "quality": "安全性",
        "stimulus_source": "监管要求与运营查询",
        "stimulus": "后台需要访问会员手机号与偏好等敏感信息",
        "artifact": "member-service",
        "environment": "跨店运营与客服排障场景",
        "response": "系统进行鉴权、脱敏与审计留痕",
        "response_measure": "所有敏感查询均具备 RBAC 校验与审计日志",
        "priority": "H",
        "driver": "会员数据合规",
    },
    {
        "id": "QAS-004",
        "source_nfr": "NFR-004",
        "quality": "可维护性",
        "stimulus_source": "总部运维团队",
        "stimulus": "新增门店需要在次日接入统一平台",
        "artifact": "门店配置与部署体系",
        "environment": "不中断既有门店服务的上线窗口",
        "response": "通过配置化与标准化部署快速接入新门店",
        "response_measure": "新增门店接入时间 < 1 天，既有门店零停机",
        "priority": "H",
        "driver": "新增门店零停机",
    },
    {
        "id": "QAS-005",
        "source_nfr": "NFR-005",
        "quality": "易用性",
        "stimulus_source": "顾客",
        "stimulus": "首次使用顾客在移动端完成预约",
        "artifact": "顾客端预约流程",
        "environment": "微信小程序与移动 Web",
        "response": "系统在少量关键页面内完成预约并反馈结果",
        "response_measure": "主流程不超过 3 个关键操作页面",
        "priority": "M",
        "driver": "预约体验稳定",
    },
    {
        "id": "QAS-006",
        "source_nfr": "NFR-006",
        "quality": "兼容性",
        "stimulus_source": "多终端顾客",
        "stimulus": "顾客从不同移动端入口访问平台",
        "artifact": "顾客端界面与接口适配层",
        "environment": "iOS Safari、Android Chrome、微信小程序",
        "response": "系统在三类终端上保持一致的关键能力和文案",
        "response_measure": "关键预约流程在三类终端通过验收",
        "priority": "M",
        "driver": "多终端一致性",
    },
    {
        "id": "QAS-007",
        "source_nfr": "NFR-007",
        "quality": "安全性",
        "stimulus_source": "运营审计",
        "stimulus": "发生敏感运营操作争议或合规复核",
        "artifact": "审计日志体系",
        "environment": "运营后台与客服后台",
        "response": "系统能够检索关键操作人、时间、动作与结果",
        "response_measure": "审计日志保留 >= 180 天，支持按门店/人员检索",
        "priority": "H",
        "driver": "可审计运营",
    },
    {
        "id": "QAS-008",
        "source_nfr": "NFR-008",
        "quality": "可移植性",
        "stimulus_source": "交付与运维团队",
        "stimulus": "需要在统一运行环境中迁移或扩容核心服务",
        "artifact": "核心服务运行环境",
        "environment": "容器化部署场景",
        "response": "服务镜像化并支持标准化启动与扩缩容",
        "response_measure": "核心服务可在 Docker 环境稳定启动",
        "priority": "M",
        "driver": "后续实验三交付",
    },
    {
        "id": "QAS-009",
        "source_nfr": "NFR-009",
        "quality": "功能适合性",
        "stimulus_source": "顾客偏好与运营策略",
        "stimulus": "顾客请求推荐桌位与互动主题",
        "artifact": "recommendation-service",
        "environment": "顾客提交偏好信息后",
        "response": "系统返回可解释的推荐结果",
        "response_measure": "P95 推荐响应 <= 2s，解释字段非空",
        "priority": "M",
        "driver": "AI 推荐可解释",
    },
    {
        "id": "QAS-010",
        "source_nfr": "NFR-010",
        "quality": "易用性",
        "stimulus_source": "店员",
        "stimulus": "高峰期需要快速识别异常预约和资源冲突",
        "artifact": "店员后台",
        "environment": "门店营业高峰",
        "response": "系统用显著状态与颜色提醒异常",
        "response_measure": "异常预约 1 秒内可识别",
        "priority": "M",
        "driver": "店员后台可视化",
    },
]

UTILITY_TREE = [
    ("业务目标", "高峰期稳定预约", "QAS-001 / QAS-002", "H"),
    ("业务目标", "合规会员运营", "QAS-003 / QAS-007", "H"),
    ("业务目标", "新增门店快速复制", "QAS-004 / QAS-008", "H"),
    ("业务目标", "顾客体验稳定", "QAS-005 / QAS-006", "M"),
    ("业务目标", "推荐能力可解释", "QAS-009", "M"),
    ("业务目标", "门店操作高效", "QAS-010", "M"),
]

ARCHITECTURE_DRIVERS = [
    "预约主链路需支撑 5000 QPS 且保持高可用",
    "新增门店上线必须尽量通过配置完成，避免停机",
    "会员与运营敏感数据要满足合规、脱敏和审计要求",
    "实验三只优先落地 member-service 与 reservation-service",
]

DOMAIN_EVENTS = [
    ("顾客注册已提交", "会员"),
    ("会员账号已创建", "会员"),
    ("会员资料已更新", "会员"),
    ("会员偏好已更新", "会员"),
    ("会员积分已累计", "会员"),
    ("优惠券已发放", "会员"),
    ("优惠券已核销", "会员"),
    ("门店已筛选", "预约"),
    ("营业日历已读取", "预约"),
    ("预约时段已查询", "预约"),
    ("桌位偏好已填写", "预约"),
    ("预约请求已提交", "预约"),
    ("预约资源已预占", "预约"),
    ("预约创建已成功", "预约"),
    ("预约创建已失败", "预约"),
    ("等位请求已创建", "预约"),
    ("预约取消已发起", "预约"),
    ("预约取消已成功", "预约"),
    ("到店提醒已发送", "通知"),
    ("补发通知已触发", "通知"),
    ("通知任务已重试", "通知"),
    ("顾客已到店", "门店运营"),
    ("顾客已入座", "门店运营"),
    ("顾客已离店", "门店运营"),
    ("迟到预约已标记", "门店运营"),
    ("爽约预约已标记", "门店运营"),
    ("现场改台已完成", "门店运营"),
    ("桌位状态已同步", "门店运营"),
    ("门店营业时间已更新", "门店运营"),
    ("桌位配置已变更", "门店运营"),
    ("猫咪健康打卡已提交", "猫咪健康"),
    ("猫咪互动限制已更新", "猫咪健康"),
    ("猫咪异常已预警", "猫咪健康"),
    ("推荐请求已接收", "推荐"),
    ("推荐结果已生成", "推荐"),
    ("推荐解释已返回", "推荐"),
    ("活动已创建", "运营"),
    ("活动触达已发送", "运营"),
    ("跨店预约报表已生成", "运营"),
    ("审计日志已落库", "运营"),
]

COMMAND_AGGREGATE_VIEW = [
    {
        "command": "创建会员账号",
        "aggregate": "Member",
        "policy": "手机号唯一且需完成基础校验",
        "read_model": "会员中心概览",
    },
    {
        "command": "创建预约",
        "aggregate": "Reservation",
        "policy": "只有可用桌位才能预占成功",
        "read_model": "门店时段可预约视图",
    },
    {
        "command": "取消预约",
        "aggregate": "ReservationOrder",
        "policy": "营业前 2 小时内受限，需保留历史轨迹",
        "read_model": "顾客预约历史",
    },
    {
        "command": "标记到店/入座/离店",
        "aggregate": "StoreShiftBoard",
        "policy": "桌位状态与预约状态必须同步更新",
        "read_model": "门店排台看板",
    },
    {
        "command": "记录猫咪健康打卡",
        "aggregate": "CatProfile",
        "policy": "体温、食量、情绪字段缺一不可",
        "read_model": "猫咪健康看板",
    },
    {
        "command": "生成推荐结果",
        "aggregate": "RecommendationSession",
        "policy": "必须返回至少一条原因说明",
        "read_model": "顾客推荐结果页",
    },
]

BOUNDED_CONTEXTS = [
    {
        "id": "BC-MEMBER",
        "name": "会员域",
        "service": "member-service",
        "goal": "管理会员资料、积分、优惠券与会员权益",
        "requirements": ["FR-001", "FR-010", "FR-011", "FR-012", "NFR-003"],
        "aggregates": ["Member", "LoyaltyPointAccount", "Coupon"],
        "invariants": ["手机号在会员域内唯一", "优惠券核销必须与会员权益状态一致"],
    },
    {
        "id": "BC-RESERVATION",
        "name": "预约域",
        "service": "reservation-service",
        "goal": "管理预约查询、资源预占、等位与预约生命周期入口",
        "requirements": ["FR-002", "FR-003", "FR-006", "FR-008", "NFR-001", "NFR-002"],
        "aggregates": ["Reservation", "WaitlistEntry", "BusinessCalendar"],
        "invariants": ["同一桌位同一时段不可被重复预占", "无空位时只能创建等位而非直接预约"],
    },
    {
        "id": "BC-ORDER",
        "name": "订单域",
        "service": "order-service",
        "goal": "管理预约订单状态、取消规则与预点单信息",
        "requirements": ["FR-004", "FR-005", "FR-023", "FR-024"],
        "aggregates": ["ReservationOrder", "PreorderDraft"],
        "invariants": ["预约订单状态迁移必须保留历史轨迹", "超时取消必须走受限规则"],
    },
    {
        "id": "BC-STORE-OPS",
        "name": "门店运营域",
        "service": "store-ops-service",
        "goal": "支撑排台、异常处理、营业时间与桌位资源配置",
        "requirements": ["FR-013", "FR-014", "FR-015", "FR-018", "FR-019", "FR-026", "FR-030", "NFR-004", "NFR-010"],
        "aggregates": ["StoreShiftBoard", "TableSlot", "ShiftSchedule"],
        "invariants": ["桌位状态与预约状态必须同步", "异常处置必须写入操作日志"],
    },
    {
        "id": "BC-CAT-HEALTH",
        "name": "猫咪健康域",
        "service": "cat-health-service",
        "goal": "维护猫咪档案、健康打卡与互动限制",
        "requirements": ["FR-016", "FR-017", "NFR-010"],
        "aggregates": ["CatProfile", "HealthRecord"],
        "invariants": ["健康打卡必须包含关键指标", "异常猫咪必须更新互动限制"],
    },
    {
        "id": "BC-RECOMMENDATION",
        "name": "推荐域",
        "service": "recommendation-service",
        "goal": "根据偏好与规则生成可解释推荐",
        "requirements": ["FR-007", "FR-029", "NFR-009"],
        "aggregates": ["RecommendationSession", "RecommendationRule"],
        "invariants": ["每次推荐都必须带解释字段", "推荐结果必须在 2 秒内返回"],
    },
]

CONTEXT_RELATIONS = [
    ("BC-MEMBER", "BC-RESERVATION", "Customer-Supplier", "会员身份与偏好为预约域提供顾客画像"),
    ("BC-RESERVATION", "BC-ORDER", "Customer-Supplier", "预约创建后生成订单与取消轨迹"),
    ("BC-RESERVATION", "BC-STORE-OPS", "Customer-Supplier", "预约结果驱动排台与桌位资源占用"),
    ("BC-STORE-OPS", "BC-CAT-HEALTH", "Conformist", "门店排台需遵守猫咪互动限制"),
    ("BC-RESERVATION", "BC-RECOMMENDATION", "Partnership", "预约域与推荐域共同完成偏好匹配"),
    ("BC-MEMBER", "BC-RECOMMENDATION", "Shared Kernel", "会员偏好与推荐画像复用部分核心字段"),
]

CANDIDATE_ARCHITECTURES = [
    {
        "id": "ARCH-A",
        "name": "模块化单体",
        "summary": "以单体应用承载会员、预约、门店运营等核心模块，通过模块边界控制耦合。",
        "strengths": [
            "本地开发和部署复杂度低，适合快速交付原型",
            "跨模块事务一致性较容易保证",
            "实验三初期实现成本更低",
        ],
        "tradeoffs": [
            "高峰期热点链路难以独立扩容",
            "新增门店与跨团队协作时模块边界容易被突破",
            "推荐、通知、运营分析等扩展模块会放大单体复杂度",
        ],
        "qas_fit": ["QAS-005", "QAS-006", "QAS-010"],
    },
    {
        "id": "ARCH-B",
        "name": "微服务 + 事件驱动",
        "summary": "按限界上下文拆分服务，通过 API 网关与异步事件解耦预约、门店运营、推荐和通知。",
        "strengths": [
            "预约主链路可独立扩容，更适合 5000 QPS 场景",
            "新增门店与新能力接入更容易配置化演进",
            "审计、通知、推荐等能力可独立部署和治理",
        ],
        "tradeoffs": [
            "分布式一致性、监控和运维复杂度更高",
            "事件建模与接口治理要求更强",
            "实验三需要控制落地范围，避免一次实现过多服务",
        ],
        "qas_fit": ["QAS-001", "QAS-002", "QAS-003", "QAS-004", "QAS-007", "QAS-008", "QAS-009"],
    },
]

ATAM_ANALYSIS = {
    "business_goals": [
        "保证预约核心链路在高峰期稳定可用",
        "支撑新门店快速复制与标准化接入",
        "满足会员敏感数据的合规与审计要求",
        "为实验三和实验四保留可落地、可测试的核心服务边界",
    ],
    "sensitivity_points": [
        "预约资源预占与时段查询的扩容方式直接影响 5000 QPS 能力",
        "敏感数据集中存储还是分域治理直接影响合规与审计成本",
        "同步调用链过长会放大通知、推荐等扩展能力对主链路的干扰",
    ],
    "tradeoff_points": [
        "单体方案降低短期开发复杂度，但牺牲独立扩容与长期演进",
        "微服务方案提升演进性与隔离性，但增加实验三实现和观测成本",
        "推荐域是否独立服务影响解释性扩展与初期落地复杂度",
    ],
    "risks": [
        "若一次性落地全部微服务，实验三实现范围会失控",
        "若审计与合规仅作为单体内功能模块表达，后续跨团队治理成本会升高",
        "若推荐与通知全部走同步调用，会放大预约主链路延迟风险",
    ],
    "non_risks": [
        "核心双服务先落地可以在不牺牲架构表达完整性的前提下降低实验三风险",
        "上下文边界已经能回链实验一需求，后续扩展不会重新命名业务域",
    ],
    "recommendation": "采用“微服务主线 + 核心双服务先落地”的折中方案：实验二保持完整的微服务边界表达，实验三只优先实现 member-service 与 reservation-service，其余上下文维持架构与契约层设计。",
}

REFERENCES = [
    "[1] Bass L., Clements P., Kazman R. Software Architecture in Practice (4th Ed.). Addison-Wesley, 2021.",
    "[2] Evans E. Domain-Driven Design. Addison-Wesley, 2003.",
    "[3] Vernon V. Implementing Domain-Driven Design. Addison-Wesley, 2013.",
    "[4] Brown S. The C4 Model for Visualising Software Architecture. https://c4model.com",
    "[5] Nygard M. Documenting Architecture Decisions. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions",
]


def artifact_filename(artifact_code: str, extension: str) -> str:
    short_name = ARTIFACT_NAMES[artifact_code]
    return f"{META['class_name']}_{META['student_id']}_{META['student_name']}_{META['experiment']}_{short_name}_{META['version']}.{extension}"


def artifact_stem(artifact_code: str) -> str:
    short_name = ARTIFACT_NAMES[artifact_code]
    return f"{META['class_name']}_{META['student_id']}_{META['student_name']}_{META['experiment']}_{short_name}_{META['version']}"


def ensure_dirs() -> None:
    for path in [SOURCE_DIR, DIAGRAM_DIR, EXPORT_DIR, SUBMISSION_DIR, BUILD_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def nfr_lookup(req_id: str) -> dict:
    for row in NON_FUNCTIONAL_REQUIREMENTS:
        if row[0] == req_id:
            return {
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
    raise KeyError(req_id)


def requirement_brief(req_id: str) -> str:
    for row in FUNCTIONAL_REQUIREMENTS:
        if row[0] == req_id:
            return row[2]
    for row in NON_FUNCTIONAL_REQUIREMENTS:
        if row[0] == req_id:
            return row[2]
    raise KeyError(req_id)


def glossary_term(term: str) -> str:
    for row in GLOSSARY:
        if row[0] == term:
            return row[2]
    raise KeyError(term)
