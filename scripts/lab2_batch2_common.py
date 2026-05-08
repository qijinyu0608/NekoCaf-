from __future__ import annotations

from lab2_common import (
    EXPORT_DIR,
    META,
    SOURCE_DIR,
    artifact_filename,
    artifact_stem,
)


C4_VIEWS = [
    {
        "id": "L1",
        "file": "L1_System_Context.drawio",
        "png": "L1_System_Context.png",
        "title": "System Context",
        "goal": "表达 NekoCafé 与顾客、店员及支付、地图、短信、AI 模型等外部系统边界。",
    },
    {
        "id": "L2",
        "file": "L2_Container.drawio",
        "png": "L2_Container.png",
        "title": "Container",
        "goal": "表达前端入口、API Gateway、双核心服务、扩展服务、数据库、缓存与消息总线。",
    },
    {
        "id": "L3-MEMBER",
        "file": "L3_Component_Member.drawio",
        "png": "L3_Component_Member.png",
        "title": "Component Member",
        "goal": "深入 member-service 的控制器、应用服务、积分、优惠券、审计与仓储组件。",
    },
    {
        "id": "L3-RESERVATION",
        "file": "L3_Component_Reservation.drawio",
        "png": "L3_Component_Reservation.png",
        "title": "Component Reservation",
        "goal": "深入 reservation-service 的查询、命令、分配策略、等位和事件发布组件。",
    },
    {
        "id": "L4",
        "file": "L4_Code_ReservationCore.drawio",
        "png": "L4_Code_ReservationCore.png",
        "title": "Code ReservationCore",
        "goal": "给出 Reservation 核心组件的关键类协作与事务边界。",
    },
]


C4_ACTORS = [
    ("顾客", "通过小程序 / Web 完成注册、预约、取消与查看推荐"),
    ("店员", "使用移动工作台处理排台、到店和异常预约"),
    ("运营管理员", "在后台查看跨店报表、活动触达与合规审计"),
]


C4_EXTERNAL_SYSTEMS = [
    ("支付平台", "处理定金、退款与账单对账"),
    ("地图定位服务", "提供门店列表、距离与导航信息"),
    ("短信/微信通知", "发送预约提醒、改签和异常通知"),
    ("AI 模型服务", "为推荐域提供偏好匹配与解释生成能力"),
]


C4_CONTAINERS = [
    ("顾客 Web", "React Web", "顾客访问门店信息、会员中心与预约记录"),
    ("微信小程序", "Mini Program", "承载顾客主预约链路与推荐入口"),
    ("店员移动端", "H5 / Mobile", "处理到店、入座、异常与排台"),
    ("运营后台", "Admin Portal", "查看报表、营销活动与审计日志"),
    ("API Gateway", "Gateway", "统一鉴权、限流、路由和灰度发布"),
    ("member-service", "Python API", "管理会员资料、积分、优惠券与偏好"),
    ("reservation-service", "Python API", "管理可预约时段、资源预占、等位与预约状态"),
    ("order-service", "Service", "管理预约订单、预点单与取消规则"),
    ("store-ops-service", "Service", "管理桌位配置、营业时间、排台与现场改台"),
    ("cat-health-service", "Service", "管理猫咪档案、健康打卡与互动限制"),
    ("recommendation-service", "Service", "生成可解释桌位与主题推荐"),
    ("notification-worker", "Worker", "异步发送通知并记录投递结果"),
    ("MySQL Cluster", "MySQL", "存储事务型核心数据"),
    ("Redis Cache", "Redis", "缓存门店时段、会员会话和热点查询"),
    ("Event Bus", "RabbitMQ", "解耦通知、推荐、审计和运营分析事件"),
]


C4_COMPONENTS_MEMBER = [
    ("MemberController", "暴露会员资料、积分、优惠券和偏好查询接口"),
    ("MemberApplicationService", "编排会员注册、资料更新和权益变更事务"),
    ("ProfilePolicy", "处理手机号唯一性、脱敏和 GDPR 字段校验"),
    ("LoyaltyService", "累计积分、核销权益并同步会员等级"),
    ("CouponService", "发放、冻结和核销优惠券"),
    ("MemberRepository", "访问 Member / MemberProfile / Coupon 数据"),
    ("AuditPublisher", "发布敏感操作审计事件"),
]


C4_COMPONENTS_RESERVATION = [
    ("ReservationController", "暴露时段查询、创建预约、取消与等位接口"),
    ("AvailabilityQueryService", "查询门店时段、桌位与互动限制快照"),
    ("ReservationCommandService", "编排预约创建、资源预占和状态迁移"),
    ("SeatAllocationPolicy", "结合人数、主题、猫咪限制计算可用桌位"),
    ("WaitlistManager", "处理无位时的候补登记与补位通知"),
    ("ReservationRepository", "访问 Reservation / Waitlist / Calendar 数据"),
    ("DomainEventPublisher", "发布预约创建、取消、到店等领域事件"),
]


C4_CODE_FLOW = [
    ("ReservationController", "接收顾客请求并校验身份"),
    ("ReservationApplicationService", "开启事务并编排主流程"),
    ("AvailabilityDomainService", "读取时段、桌位与猫咪限制快照"),
    ("SeatAllocationPolicy", "选择满足偏好的桌位资源"),
    ("ReservationRepository", "持久化 Reservation 与 WaitlistEntry"),
    ("DomainEventPublisher", "投递 ReservationCreated 事件"),
]


OPENAPI_SPECS = {
    "member-service": {
        "openapi": "3.0.3",
        "info": {
            "title": "Member Service API",
            "version": "1.0.0",
            "description": "NekoCafé 会员服务，负责会员资料、偏好、积分与优惠券治理。",
        },
        "servers": [{"url": "https://api.nekocafe.com", "description": "Production"}],
        "tags": [
            {"name": "Member", "description": "会员资料与偏好"},
            {"name": "Loyalty", "description": "积分与优惠券"},
        ],
        "paths": {
            "/member/v1/members/{memberId}": {
                "get": {
                    "tags": ["Member"],
                    "summary": "查询会员详情",
                    "x-ratelimit-limit": 600,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/MemberDetailOk"},
                        "404": {"$ref": "#/components/responses/MemberNotFound"},
                        "403": {"$ref": "#/components/responses/Forbidden"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/member/v1/members/{memberId}/profile": {
                "patch": {
                    "tags": ["Member"],
                    "summary": "更新会员资料与偏好",
                    "x-ratelimit-limit": 120,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/MemberProfileUpdate"}}},
                    },
                    "responses": {
                        "200": {"$ref": "#/components/responses/MemberDetailOk"},
                        "400": {"$ref": "#/components/responses/BadRequest"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/member/v1/members/{memberId}/coupons": {
                "get": {
                    "tags": ["Loyalty"],
                    "summary": "查询会员可用优惠券",
                    "x-ratelimit-limit": 300,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/CouponListOk"},
                        "404": {"$ref": "#/components/responses/MemberNotFound"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/member/v1/members/{memberId}/points": {
                "get": {
                    "tags": ["Loyalty"],
                    "summary": "查询会员积分账户",
                    "x-ratelimit-limit": 300,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/PointAccountOk"},
                        "404": {"$ref": "#/components/responses/MemberNotFound"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/member/v1/members/{memberId}/points/transactions": {
                "get": {
                    "tags": ["Loyalty"],
                    "summary": "查询会员积分变更记录",
                    "x-ratelimit-limit": 180,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/PointTransactionListOk"},
                        "404": {"$ref": "#/components/responses/MemberNotFound"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/member/v1/members/{memberId}/coupons/claim": {
                "post": {
                    "tags": ["Loyalty"],
                    "summary": "领取会员优惠券",
                    "x-ratelimit-limit": 60,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ClaimCouponRequest"}}},
                    },
                    "responses": {
                        "201": {"$ref": "#/components/responses/CouponClaimed"},
                        "404": {"$ref": "#/components/responses/MemberNotFound"},
                        "409": {"$ref": "#/components/responses/CouponClaimConflict"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "schemas": {
                "MemberDetail": {
                    "type": "object",
                    "properties": {
                        "memberId": {"type": "string"},
                        "tenantId": {"type": "string"},
                        "nickname": {"type": "string"},
                        "mobileMasked": {"type": "string"},
                        "loyaltyLevel": {"type": "string"},
                        "preferences": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "MemberProfileUpdate": {
                    "type": "object",
                    "required": ["nickname", "preferences"],
                    "properties": {
                        "nickname": {"type": "string"},
                        "preferences": {"type": "array", "items": {"type": "string"}},
                        "allergyNote": {"type": "string"},
                    },
                },
                "CouponItem": {
                    "type": "object",
                    "properties": {
                        "couponId": {"type": "string"},
                        "title": {"type": "string"},
                        "status": {"type": "string"},
                        "expireAt": {"type": "string", "format": "date-time"},
                    },
                },
                "PointAccount": {
                    "type": "object",
                    "properties": {
                        "memberId": {"type": "string"},
                        "currentPoints": {"type": "integer"},
                        "pendingPoints": {"type": "integer"},
                        "levelCode": {"type": "string"},
                        "benefitSummary": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "PointTransaction": {
                    "type": "object",
                    "properties": {
                        "transactionId": {"type": "string"},
                        "changeType": {"type": "string"},
                        "pointsChanged": {"type": "integer"},
                        "occurredAt": {"type": "string", "format": "date-time"},
                        "source": {"type": "string"},
                    },
                },
                "ClaimCouponRequest": {
                    "type": "object",
                    "required": ["couponTemplateId"],
                    "properties": {
                        "couponTemplateId": {"type": "string"},
                        "campaignCode": {"type": "string"},
                    },
                },
                "CouponClaimResult": {
                    "type": "object",
                    "properties": {
                        "couponId": {"type": "string"},
                        "status": {"type": "string"},
                        "expireAt": {"type": "string", "format": "date-time"},
                    },
                },
                "ErrorBody": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "traceId": {"type": "string"},
                    },
                },
            },
            "responses": {
                "MemberDetailOk": {
                    "description": "会员详情",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/MemberDetail"}}},
                },
                "CouponListOk": {
                    "description": "优惠券列表",
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/CouponItem"}}
                        }
                    },
                },
                "PointAccountOk": {
                    "description": "积分账户详情",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PointAccount"}}},
                },
                "PointTransactionListOk": {
                    "description": "积分变更记录",
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/PointTransaction"}}
                        }
                    },
                },
                "CouponClaimed": {
                    "description": "优惠券领取成功",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CouponClaimResult"}}},
                },
                "MemberNotFound": {
                    "description": "会员不存在",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "BadRequest": {
                    "description": "请求参数错误",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "Forbidden": {
                    "description": "无权限访问",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "CouponClaimConflict": {
                    "description": "优惠券已领取或当前不满足领取条件",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
            },
        },
    },
    "reservation-service": {
        "openapi": "3.0.3",
        "info": {
            "title": "Reservation Service API",
            "version": "1.0.0",
            "description": "NekoCafé 桌位预约服务，负责时段查询、资源预占、预约创建、取消与等位。",
        },
        "servers": [{"url": "https://api.nekocafe.com", "description": "Production"}],
        "tags": [
            {"name": "Availability", "description": "营业日历与时段查询"},
            {"name": "Reservation", "description": "预约创建、取消与状态查询"},
        ],
        "paths": {
            "/reservation/v1/stores/{storeId}/slots": {
                "get": {
                    "tags": ["Availability"],
                    "summary": "查询门店可预约时段",
                    "x-ratelimit-limit": 800,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "storeId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "date", "in": "query", "required": True, "schema": {"type": "string", "format": "date"}},
                        {"name": "partySize", "in": "query", "required": True, "schema": {"type": "integer"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/SlotQueryOk"},
                        "400": {"$ref": "#/components/responses/BadRequest"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/reservations": {
                "post": {
                    "tags": ["Reservation"],
                    "summary": "创建预约",
                    "x-ratelimit-limit": 300,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateReservationRequest"}}},
                    },
                    "responses": {
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "201": {"$ref": "#/components/responses/ReservationCreated"},
                        "409": {"$ref": "#/components/responses/SlotConflict"},
                        "422": {"$ref": "#/components/responses/CatRestriction"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/reservations/{reservationId}": {
                "get": {
                    "tags": ["Reservation"],
                    "summary": "查询预约详情",
                    "x-ratelimit-limit": 600,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "reservationId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/ReservationDetailOk"},
                        "404": {"$ref": "#/components/responses/ReservationNotFound"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/reservations/{reservationId}/cancel": {
                "post": {
                    "tags": ["Reservation"],
                    "summary": "取消预约",
                    "x-ratelimit-limit": 120,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "reservationId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/ReservationDetailOk"},
                        "409": {"$ref": "#/components/responses/CancelWindowExceeded"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/members/{memberId}/reservations": {
                "get": {
                    "tags": ["Reservation"],
                    "summary": "查询会员预约列表",
                    "x-ratelimit-limit": 300,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "memberId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "status", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "businessDate", "in": "query", "required": False, "schema": {"type": "string", "format": "date"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/ReservationListOk"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/waitlist": {
                "post": {
                    "tags": ["Reservation"],
                    "summary": "创建等位请求",
                    "x-ratelimit-limit": 120,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateWaitlistRequest"}}},
                    },
                    "responses": {
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "201": {"$ref": "#/components/responses/WaitlistCreated"},
                        "409": {"$ref": "#/components/responses/SlotConflict"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/waitlist/{waitlistId}": {
                "get": {
                    "tags": ["Reservation"],
                    "summary": "查询等位详情",
                    "x-ratelimit-limit": 240,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "waitlistId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/WaitlistDetailOk"},
                        "404": {"$ref": "#/components/responses/WaitlistNotFound"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
            "/reservation/v1/reservations/{reservationId}/check-in": {
                "post": {
                    "tags": ["Reservation"],
                    "summary": "确认顾客到店",
                    "x-ratelimit-limit": 180,
                    "x-ratelimit-window": "1m",
                    "parameters": [
                        {"name": "reservationId", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Tenant-Id", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"$ref": "#/components/responses/ReservationDetailOk"},
                        "404": {"$ref": "#/components/responses/ReservationNotFound"},
                        "409": {"$ref": "#/components/responses/InvalidReservationState"},
                    },
                    "security": [{"bearerAuth": []}],
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "schemas": {
                "SlotItem": {
                    "type": "object",
                    "properties": {
                        "slotId": {"type": "string"},
                        "startAt": {"type": "string", "format": "date-time"},
                        "capacity": {"type": "integer"},
                        "theme": {"type": "string"},
                    },
                },
                "CreateReservationRequest": {
                    "type": "object",
                    "required": ["memberId", "storeId", "slotId", "partySize"],
                    "properties": {
                        "memberId": {"type": "string"},
                        "storeId": {"type": "string"},
                        "slotId": {"type": "string"},
                        "partySize": {"type": "integer"},
                        "preferredTheme": {"type": "string"},
                        "catInteractionMode": {"type": "string"},
                    },
                },
                "ReservationDetail": {
                    "type": "object",
                    "properties": {
                        "reservationId": {"type": "string"},
                        "status": {"type": "string"},
                        "tableCode": {"type": "string"},
                        "storeId": {"type": "string"},
                        "slotId": {"type": "string"},
                        "partySize": {"type": "integer"},
                        "checkedInAt": {"type": "string", "format": "date-time"},
                    },
                },
                "ReservationListItem": {
                    "type": "object",
                    "properties": {
                        "reservationId": {"type": "string"},
                        "status": {"type": "string"},
                        "storeId": {"type": "string"},
                        "slotStartAt": {"type": "string", "format": "date-time"},
                        "partySize": {"type": "integer"},
                    },
                },
                "CreateWaitlistRequest": {
                    "type": "object",
                    "required": ["memberId", "storeId", "requestedSlot", "partySize"],
                    "properties": {
                        "memberId": {"type": "string"},
                        "storeId": {"type": "string"},
                        "requestedSlot": {"type": "string", "format": "date-time"},
                        "partySize": {"type": "integer"},
                        "preferredTheme": {"type": "string"},
                    },
                },
                "WaitlistDetail": {
                    "type": "object",
                    "properties": {
                        "waitlistId": {"type": "string"},
                        "status": {"type": "string"},
                        "queuePosition": {"type": "integer"},
                        "storeId": {"type": "string"},
                        "requestedSlot": {"type": "string", "format": "date-time"},
                        "partySize": {"type": "integer"},
                    },
                },
                "ErrorBody": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "traceId": {"type": "string"},
                    },
                },
            },
            "responses": {
                "SlotQueryOk": {
                    "description": "时段查询结果",
                    "content": {
                        "application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/SlotItem"}}}
                    },
                },
                "ReservationCreated": {
                    "description": "预约创建成功",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ReservationDetail"}}},
                },
                "ReservationDetailOk": {
                    "description": "预约详情",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ReservationDetail"}}},
                },
                "ReservationListOk": {
                    "description": "会员预约列表",
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/ReservationListItem"}}
                        }
                    },
                },
                "WaitlistCreated": {
                    "description": "等位创建成功",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/WaitlistDetail"}}},
                },
                "WaitlistDetailOk": {
                    "description": "等位详情",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/WaitlistDetail"}}},
                },
                "ReservationNotFound": {
                    "description": "预约不存在",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "WaitlistNotFound": {
                    "description": "等位记录不存在",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "SlotConflict": {
                    "description": "桌位冲突",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "CatRestriction": {
                    "description": "猫咪互动限制阻断当前预约",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "CancelWindowExceeded": {
                    "description": "超过允许取消时间窗",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "BadRequest": {
                    "description": "请求参数错误",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
                "InvalidReservationState": {
                    "description": "当前预约状态不允许执行该操作",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}},
                },
            },
        },
    },
}


DATA_MODEL_CONTEXTS = [
    {
        "context": "BC-MEMBER",
        "tenant_strategy": "行级隔离",
        "entities": [
            {
                "name": "Member",
                "description": "会员主档",
                "fields": [
                    ("member_id", "bigint", "PK"),
                    ("tenant_id", "varchar(32)", "租户隔离键"),
                    ("openid_hash", "varchar(64)", "微信身份映射"),
                    ("mobile [GDPR]", "varchar(32)", "顾客手机号"),
                    ("status", "varchar(16)", "会员状态"),
                ],
            },
            {
                "name": "MemberProfile",
                "description": "会员扩展资料与偏好",
                "fields": [
                    ("profile_id", "bigint", "PK"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("nickname [GDPR]", "varchar(64)", "顾客昵称"),
                    ("allergy_note [GDPR]", "varchar(255)", "过敏与忌口"),
                    ("favorite_theme", "varchar(32)", "偏好主题"),
                ],
            },
            {
                "name": "LoyaltyPointAccount",
                "description": "积分账户",
                "fields": [
                    ("account_id", "bigint", "PK"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("current_points", "int", "当前积分"),
                    ("level_code", "varchar(16)", "会员等级"),
                ],
            },
            {
                "name": "Coupon",
                "description": "优惠券",
                "fields": [
                    ("coupon_id", "bigint", "PK"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("title", "varchar(64)", "优惠券标题"),
                    ("status", "varchar(16)", "可用 / 冻结 / 已核销"),
                    ("expire_at", "datetime", "过期时间"),
                ],
            },
        ],
    },
    {
        "context": "BC-RESERVATION",
        "tenant_strategy": "行级隔离",
        "entities": [
            {
                "name": "Store",
                "description": "门店",
                "fields": [
                    ("store_id", "bigint", "PK"),
                    ("tenant_id", "varchar(32)", "租户隔离键"),
                    ("store_name", "varchar(64)", "门店名称"),
                    ("city_code", "varchar(16)", "城市编码"),
                    ("timezone", "varchar(32)", "时区"),
                ],
            },
            {
                "name": "BusinessCalendar",
                "description": "营业日历",
                "fields": [
                    ("calendar_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("business_date", "date", "营业日期"),
                    ("open_at", "datetime", "开店时间"),
                    ("close_at", "datetime", "闭店时间"),
                ],
            },
            {
                "name": "TableSlot",
                "description": "桌位资源时段",
                "fields": [
                    ("slot_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("table_code", "varchar(32)", "桌位编码"),
                    ("start_at", "datetime", "开始时间"),
                    ("capacity", "int", "容纳人数"),
                ],
            },
            {
                "name": "Reservation",
                "description": "预约主记录",
                "fields": [
                    ("reservation_id", "bigint", "PK"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("slot_id", "bigint", "FK -> TableSlot"),
                    ("status", "varchar(16)", "预约状态"),
                    ("party_size", "int", "人数"),
                ],
            },
            {
                "name": "WaitlistEntry",
                "description": "候补记录",
                "fields": [
                    ("waitlist_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("requested_slot", "datetime", "期望时段"),
                    ("status", "varchar(16)", "候补状态"),
                ],
            },
        ],
    },
    {
        "context": "BC-ORDER",
        "tenant_strategy": "行级隔离",
        "entities": [
            {
                "name": "ReservationOrder",
                "description": "预约订单",
                "fields": [
                    ("order_id", "bigint", "PK"),
                    ("reservation_id", "bigint", "FK -> Reservation"),
                    ("deposit_amount", "decimal(10,2)", "定金"),
                    ("payment_status", "varchar(16)", "支付状态"),
                    ("cancel_rule_code", "varchar(16)", "取消规则"),
                ],
            },
            {
                "name": "PreorderDraft",
                "description": "预点单草稿",
                "fields": [
                    ("draft_id", "bigint", "PK"),
                    ("order_id", "bigint", "FK -> ReservationOrder"),
                    ("menu_snapshot_id", "bigint", "菜单快照"),
                    ("draft_payload", "json", "预点单详情"),
                ],
            },
        ],
    },
    {
        "context": "BC-STORE-OPS",
        "tenant_strategy": "行级隔离",
        "entities": [
            {
                "name": "StoreShiftBoard",
                "description": "排台看板快照",
                "fields": [
                    ("board_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("business_date", "date", "营业日期"),
                    ("board_status", "varchar(16)", "看板状态"),
                ],
            },
            {
                "name": "ShiftSchedule",
                "description": "店员班次",
                "fields": [
                    ("shift_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("staff_code", "varchar(32)", "店员编号"),
                    ("start_at", "datetime", "上班时间"),
                    ("end_at", "datetime", "下班时间"),
                ],
            },
            {
                "name": "AuditLog",
                "description": "运营审计日志",
                "fields": [
                    ("log_id", "bigint", "PK"),
                    ("tenant_id", "varchar(32)", "租户隔离键"),
                    ("operator_id", "varchar(32)", "操作人"),
                    ("action_code", "varchar(32)", "动作编码"),
                    ("trace_id", "varchar(64)", "链路追踪"),
                ],
            },
        ],
    },
    {
        "context": "BC-CAT-HEALTH",
        "tenant_strategy": "行级隔离",
        "entities": [
            {
                "name": "CatProfile",
                "description": "猫咪档案",
                "fields": [
                    ("cat_id", "bigint", "PK"),
                    ("store_id", "bigint", "FK -> Store"),
                    ("cat_name", "varchar(32)", "猫咪名称"),
                    ("health_level", "varchar(16)", "健康等级"),
                    ("interaction_mode", "varchar(16)", "互动限制"),
                ],
            },
            {
                "name": "HealthRecord",
                "description": "健康打卡",
                "fields": [
                    ("record_id", "bigint", "PK"),
                    ("cat_id", "bigint", "FK -> CatProfile"),
                    ("temperature", "decimal(4,1)", "体温"),
                    ("mood_score", "int", "情绪评分"),
                    ("feed_amount", "decimal(5,2)", "进食量"),
                ],
            },
        ],
    },
    {
        "context": "BC-RECOMMENDATION",
        "tenant_strategy": "行级隔离，欧盟租户可升级为 Schema 隔离",
        "entities": [
            {
                "name": "RecommendationRule",
                "description": "推荐规则",
                "fields": [
                    ("rule_id", "bigint", "PK"),
                    ("tenant_id", "varchar(32)", "租户隔离键"),
                    ("rule_type", "varchar(32)", "规则类型"),
                    ("weight", "decimal(5,2)", "权重"),
                ],
            },
            {
                "name": "RecommendationSession",
                "description": "推荐会话",
                "fields": [
                    ("session_id", "bigint", "PK"),
                    ("member_id", "bigint", "FK -> Member"),
                    ("prompt_snapshot", "json", "推荐输入快照"),
                    ("explanation_text", "varchar(255)", "推荐解释"),
                    ("created_at", "datetime", "创建时间"),
                ],
            },
            {
                "name": "Campaign",
                "description": "营销活动",
                "fields": [
                    ("campaign_id", "bigint", "PK"),
                    ("tenant_id", "varchar(32)", "租户隔离键"),
                    ("campaign_name", "varchar(64)", "活动名称"),
                    ("channel_code", "varchar(16)", "触达渠道"),
                ],
            },
            {
                "name": "NotificationTask",
                "description": "通知任务",
                "fields": [
                    ("task_id", "bigint", "PK"),
                    ("channel_code", "varchar(16)", "短信 / 微信"),
                    ("payload_json", "json", "投递载荷"),
                    ("delivery_status", "varchar(16)", "投递状态"),
                ],
            },
        ],
    },
]


INDEX_AND_PARTITION = [
    "Reservation、ReservationOrder 按 business_date 做月分区，配合 store_id + slot_id 联合索引支撑高峰查询。",
    "TableSlot 对 store_id + start_at 建唯一索引，避免同店同桌位同时间重复资源配置。",
    "AuditLog 按 tenant_id + created_at 建覆盖索引，支持 180 天内审计追溯。",
    "RecommendationSession 按 created_at 做冷热分层，90 天后迁移至低频存储。",
]


DATA_LIFECYCLE = [
    ("Reservation", "180 天", "保留运营分析与投诉追溯所需主链路数据"),
    ("AuditLog", "180 天", "满足合规审计与异常复盘"),
    ("NotificationTask", "90 天", "保留投递结果用于重试与对账"),
    ("RecommendationSession", "90 天在线 + 1 年归档", "兼顾推荐解释追溯与存储成本"),
]


MULTI_TENANT_STRATEGY = (
    "默认采用行级隔离：所有核心事务表统一携带 tenant_id 并在 API Gateway 与服务层执行强制注入。"
    "对欧盟或高合规租户，推荐域和审计域支持升级到 Schema 隔离，以降低跨境和审计数据混布风险。"
)


CROSS_BORDER_RULES = [
    "所有带 [GDPR] 标记的字段在跨境同步前必须完成最小化、脱敏或显式授权校验。",
    "member-service 负责敏感会员字段主治理，跨域读取默认只暴露脱敏副本。",
    "RecommendationSession 的 prompt_snapshot 不得直接包含明文手机号、昵称和过敏备注。",
]


def count_entities() -> int:
    return sum(len(context["entities"]) for context in DATA_MODEL_CONTEXTS)


def d2_5_package_dir():
    return SOURCE_DIR / artifact_stem("D2-5")


def d2_4_export_dir():
    return EXPORT_DIR / artifact_stem("D2-4")


def d2_6_export_dir():
    return EXPORT_DIR / artifact_stem("D2-6")


def d2_6_filename() -> str:
    return artifact_filename("D2-6", "docx")
