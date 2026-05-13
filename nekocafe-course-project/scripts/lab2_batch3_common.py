from __future__ import annotations

from pathlib import Path

from lab2_common import META, ROOT, SOURCE_DIR, artifact_filename, artifact_stem


ADR_RECORDS = [
    {
        "id": "0001",
        "topic": "ADR 制度",
        "title": "记录架构决策并保持编号连续",
        "status": "Accepted",
        "context": "实验二之后项目会连续进入实验三和实验四，需要保留可回溯的架构决策链条，避免后续实现阶段重新解释为什么这样设计。",
        "decision": "采用 MADR 风格记录 ADR，编号从 0001 开始递增，不重排历史编号，后续若被替代则使用 Superseded 标记。",
        "consequences": [
            "正面：后续服务实现、测试和答辩都有统一决策依据。",
            "负面：需要额外维护 ADR 文档与编号纪律。",
            "中性：不同实验阶段仍可继续补充新 ADR，而不影响既有编号。",
        ],
        "alternatives": [
            "只在报告里写结论：不利于持续演进，也无法在 Git 中单独跟踪变更。",
            "把所有决策挤进一份总说明：粒度过粗，后续难以替换单条决策。",
        ],
    },
    {
        "id": "0002",
        "topic": "服务拆分粒度",
        "title": "采用微服务主线并先实现双核心服务",
        "status": "Accepted",
        "context": "实验二要求完成完整架构表达，但实验三实现资源有限，不能一次性落地所有服务。",
        "decision": "按限界上下文拆分为 6 个服务边界，在实现层优先落地 member-service 与 reservation-service，其余服务维持契约与架构表达。",
        "consequences": [
            "正面：兼顾课程要求的完整性与实验三实现复杂度控制。",
            "负面：部分跨域流程在实验三阶段只能以接口或事件契约形式存在。",
            "中性：后续可按业务压力和教学安排再逐步实现其他服务。",
        ],
        "alternatives": [
            "全部做成模块化单体：不利于 5000 QPS 和后续演进表达。",
            "一次性实现全量微服务：超出实验三可控范围。",
        ],
    },
    {
        "id": "0003",
        "topic": "数据库选型",
        "title": "事务域采用 MySQL，缓存采用 Redis",
        "status": "Accepted",
        "context": "预约、会员、订单等核心事务域需要强一致事务与相对直观的关系建模，同时高峰期时段查询需要热点缓存。",
        "decision": "核心事务数据统一使用 MySQL，热点查询与会话状态使用 Redis，后续分析型需求再通过事件流扩展到离线分析存储。",
        "consequences": [
            "正面：事务语义清晰，便于实验三快速落地。",
            "负面：若推荐和分析需求迅速增长，单纯 MySQL 需要后续补分析侧扩展。",
            "中性：Redis 作为性能补充，而非主数据源。",
        ],
        "alternatives": [
            "全部使用 NoSQL：事务和复杂约束表达不如关系库直接。",
            "立即引入多种专用数据库：当前教学场景维护成本过高。",
        ],
    },
    {
        "id": "0004",
        "topic": "消息中间件",
        "title": "采用事件总线解耦通知、推荐与审计",
        "status": "Accepted",
        "context": "预约主链路不应被通知、推荐解释、运营分析等扩展能力拖慢。",
        "decision": "引入事件总线作为异步解耦基础设施，预约与会员服务只负责发布领域事件，由通知、推荐、审计等消费者异步处理。",
        "consequences": [
            "正面：降低主链路同步耦合，便于后续扩展分析与推荐。",
            "负面：增加消息幂等、重试和监控的复杂度。",
            "中性：实验三可先用轻量实现模拟总线，再逐步增强。",
        ],
        "alternatives": [
            "全部同步 HTTP 调用：主链路容易被扩展服务拖慢。",
            "完全不引入异步：难以体现架构演进空间。",
        ],
    },
    {
        "id": "0005",
        "topic": "API 风格",
        "title": "对外接口采用 REST + OpenAPI 3.0",
        "status": "Accepted",
        "context": "实验二明确要求桌位预约服务与会员服务输出 OpenAPI 3.0 文档，实验三也需要较低门槛的接口联调方式。",
        "decision": "对外同步接口统一采用 REST 风格，并以 OpenAPI 3.0 管理版本、鉴权、限流和错误码契约。",
        "consequences": [
            "正面：契约清晰，适合课程交付与服务联调。",
            "负面：对复杂聚合查询可能不如 GraphQL 灵活。",
            "中性：未来若运营后台需要更灵活聚合查询，可单独评估 GraphQL BFF。",
        ],
        "alternatives": [
            "直接使用 GraphQL：当前收益不足，且增加联调门槛。",
            "只写接口说明不做契约：不满足实验要求，也不利于后续实现。",
        ],
    },
    {
        "id": "0006",
        "topic": "鉴权方案",
        "title": "采用 JWT + RBAC + Tenant Header 的组合鉴权",
        "status": "Accepted",
        "context": "会员敏感数据、跨店运营数据和多租户场景都要求有明确的身份、角色和租户边界。",
        "decision": "API Gateway 验证 JWT，服务内部基于角色做 RBAC 校验，并通过 X-Tenant-Id 强制注入租户上下文。",
        "consequences": [
            "正面：权限、租户和审计链条清晰，便于实验四继续做安全与审查。",
            "负面：比最简单的会话鉴权需要更多网关和中间件配置。",
            "中性：对顾客端和后台端的角色模型需要继续细化。",
        ],
        "alternatives": [
            "仅依赖后端会话：不利于多端接入和服务拆分。",
            "只做身份认证不做角色控制：无法满足敏感运营权限要求。",
        ],
    },
    {
        "id": "0007",
        "topic": "跨境数据同步策略",
        "title": "敏感字段最小化同步并为高合规租户预留 Schema 隔离",
        "status": "Accepted",
        "context": "CTO 关心会员跨境同步合规问题，而推荐与运营分析又需要一定范围的数据共享。",
        "decision": "默认采用行级租户隔离；对带 [GDPR] 标记的敏感字段执行最小化、脱敏或授权后同步；为高合规租户预留 Schema 隔离升级路径。",
        "consequences": [
            "正面：在不显著抬高当前实现成本的前提下保留合规扩展路径。",
            "负面：跨境同步链路需要更严格的字段治理和审计。",
            "中性：短期不会立即引入独立跨境数据平台，但会在路线图中预留。",
        ],
        "alternatives": [
            "完全不做跨境同步：不能回答任务书场景中的 CTO 追问。",
            "立即做完全独立数据库隔离：当前教学场景成本过高。",
        ],
    },
]


ROADMAP = {
    "current_state": [
        "实验二已完成 QAS、DDD、ATAM、C4、OpenAPI 和 ER 的架构表达。",
        "可运行代码骨架当前仅覆盖 member-service 与 reservation-service 的最小应用入口。",
        "实验三与实验四仍需继续补 DevOps、部署、测试与审查闭环。",
    ],
    "target_state": [
        "12 个月内形成支持高峰预约、可观测、可回滚、具备多租户扩展能力的 NekoCafé 平台架构。",
        "核心双服务稳定上线，扩展服务通过事件总线逐步接入，跨境与合规策略具备可执行方案。",
    ],
    "milestones": [
        {
            "code": "M1",
            "months": "第 1-3 月",
            "title": "核心服务上线",
            "focus": "完成 member-service 与 reservation-service 的容器化、CI/CD 与基础观测能力。",
            "deliverables": [
                "双核心服务容器镜像与 compose 部署",
                "基础监控、日志和接口联调脚本",
                "预约主链路的基本单测与集成验证",
            ],
            "definition_of_success": "预约主链路在测试环境可稳定运行，核心接口通过自动化校验，故障可通过日志和监控快速定位。",
        },
        {
            "code": "M2",
            "months": "第 4-6 月",
            "title": "AI 推荐接入",
            "focus": "引入 recommendation-service、通知异步链路和推荐解释能力。",
            "deliverables": [
                "推荐域事件消费者与解释字段输出",
                "通知 worker 与消息重试策略",
                "推荐结果与预约流程的联动验证",
            ],
            "definition_of_success": "顾客可在预约流程中看到可解释推荐，推荐与通知不阻塞预约主链路。",
        },
        {
            "code": "M3",
            "months": "第 7-12 月",
            "title": "跨境与多租户",
            "focus": "完成合规字段治理、多租户隔离增强和跨境同步策略试运行。",
            "deliverables": [
                "高合规租户 Schema 隔离试点",
                "跨境字段最小化同步清单与审计追踪",
                "门店扩张和多租户接入手册",
            ],
            "definition_of_success": "新租户可按标准流程接入，跨境字段同步可审计，高合规租户具备隔离升级路径。",
        },
    ],
    "risk_register": [
        ("服务边界过度设计", "实验三实现范围失控", "坚持双核心服务先落地，并用 ADR 固定边界"),
        ("消息链路缺乏幂等", "通知与推荐重复消费", "在 M2 前补事件幂等键与重试策略"),
        ("合规字段治理不足", "跨境同步存在数据暴露风险", "以 [GDPR] 字段清单驱动最小化同步和审计"),
    ],
    "rollback": [
        "M1 若核心服务不稳定，可回退到单机测试环境并关闭异步消费者。",
        "M2 若推荐链路影响预约响应，可暂时关闭 recommendation-service，只保留基础预约流程。",
        "M3 若高合规租户隔离方案带来迁移风险，可先停留在行级隔离并仅上线字段最小化同步。",
    ],
}


def adr_package_dir() -> Path:
    return SOURCE_DIR / artifact_stem("D2-7")


def adr_markdown_dir() -> Path:
    return ROOT / "docs" / "adr" / "lab2"


def roadmap_docx_path() -> Path:
    return SOURCE_DIR / artifact_filename("D2-8", "docx")
