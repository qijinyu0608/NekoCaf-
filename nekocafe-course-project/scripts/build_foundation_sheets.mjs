import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const scriptPath = fileURLToPath(import.meta.url);
const rootDir = path.resolve(path.dirname(scriptPath), "..");
const foundationDir = path.join(rootDir, "docs", "foundation");

function writeBlock(sheet, range, values) {
  sheet.getRange(range).values = values;
}

function applyHeader(sheet, range) {
  const header = sheet.getRange(range);
  if (header.format) {
    header.format.font.bold = true;
  }
}

async function buildRequirementsWorkbook() {
  const workbook = Workbook.create();

  const functional = workbook.worksheets.add("Functional Requirements");
  const frHeader = [[
    "ID",
    "需求类别",
    "需求描述",
    "来源",
    "MoSCoW",
    "优先级",
    "验收准则",
    "上下文",
    "服务归属",
    "测试覆盖状态",
    "状态",
    "备注",
  ]];
  writeBlock(functional, "A1:L1", frHeader);
  applyHeader(functional, "A1:L1");
  writeBlock(functional, "A2:L7", [
    ["FR-001", "会员", "顾客可以注册并维护会员资料", "顾客访谈", "Must", "P1", "Given 新用户访问注册页 When 提交合法信息 Then 系统创建会员账号", "BC-MEMBER", "member-service", "未开始", "Draft", "实验一主线需求"],
    ["FR-002", "预约", "顾客可以浏览门店与可预约时段", "顾客访谈", "Must", "P1", "Given 顾客进入门店页 When 选择日期 Then 返回可预约时段", "BC-RESERVATION", "reservation-service", "未开始", "Draft", "实验一主线需求"],
    ["FR-003", "预约", "顾客可以创建桌位预约订单", "顾客访谈", "Must", "P1", "Given 顾客已选择门店与时段 When 提交预约 Then 系统生成预约记录", "BC-RESERVATION", "reservation-service", "未开始", "Draft", ""],
    ["FR-004", "订单", "顾客可以取消未到店的预约", "顾客访谈", "Should", "P2", "Given 存在有效预约 When 顾客取消 Then 预约状态变更为已取消", "BC-ORDER", "待定", "未开始", "Draft", "设计层先保留"],
    ["FR-005", "店员", "店员可以查看当日预约并安排桌位", "店员访谈", "Must", "P1", "Given 店员进入后台 When 查看当日排班 Then 系统展示预约与桌位占用", "BC-STORE-OPS", "待定", "未开始", "Draft", ""],
    ["FR-006", "猫咪健康", "店员可以记录猫咪健康打卡", "店员访谈", "Could", "P3", "Given 店员进入猫咪档案页 When 填写健康信息 Then 系统保存打卡记录", "BC-CAT-HEALTH", "待定", "未开始", "Draft", ""],
  ]);

  const nonFunctional = workbook.worksheets.add("Non-Functional Requirements");
  writeBlock(nonFunctional, "A1:J1", [[
    "ID",
    "ISO25010 分类",
    "需求描述",
    "来源",
    "MoSCoW",
    "优先级",
    "响应度量",
    "上下文",
    "测试覆盖状态",
    "备注",
  ]]);
  applyHeader(nonFunctional, "A1:J1");
  writeBlock(nonFunctional, "A2:J5", [
    ["NFR-001", "性能效率", "高峰期预约接口支持 5000 QPS", "总览文档", "Must", "P1", "峰值 5000 QPS 下错误率低于 1%", "BC-RESERVATION", "未开始", "实验二架构驱动力"],
    ["NFR-002", "可靠性", "核心预约接口 SLA 不低于 99.9%", "总览文档", "Must", "P1", "月度可用性 >= 99.9%", "BC-RESERVATION", "未开始", ""],
    ["NFR-003", "安全性", "个人信息处理需符合《个人信息保护法》", "运营总监访谈", "Must", "P1", "敏感字段具备权限控制与合规标注", "BC-MEMBER", "未开始", ""],
    ["NFR-004", "可维护性", "新门店上线需要做到零停机", "CTO 追问", "Should", "P2", "新增门店配置变更不导致服务中断", "BC-STORE-OPS", "未开始", "实验三关注"],
  ]);

  const indexSheet = workbook.worksheets.add("Usage Notes");
  writeBlock(indexSheet, "A1:B6", [
    ["字段", "说明"],
    ["上下文", "实验二限界上下文映射的连接字段"],
    ["服务归属", "实验三代码实现时映射到具体服务"],
    ["测试覆盖状态", "实验四回填自动化覆盖进度"],
    ["状态", "Draft / Baseline / Accepted / Deprecated"],
    ["备注", "记录冲突、依赖与暂缓原因"],
  ]);
  applyHeader(indexSheet, "A1:B1");

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(foundationDir, "requirements-baseline.xlsx"));
}

async function buildGlossaryWorkbook() {
  const workbook = Workbook.create();

  const glossary = workbook.worksheets.add("Glossary");
  writeBlock(glossary, "A1:F1", [[
    "术语",
    "英文",
    "定义",
    "同义词",
    "反义词",
    "出处",
  ]]);
  applyHeader(glossary, "A1:F1");
  writeBlock(glossary, "A2:F7", [
    ["会员", "Member", "在平台中拥有注册资料与消费权益的顾客", "用户", "游客", "实验一需求获取"],
    ["预约", "Reservation", "顾客针对门店、时段和桌位发起的占位请求", "订位", "临时到店", "实验一需求获取"],
    ["预约订单", "Reservation Order", "系统持久化后的预约记录实体", "预约记录", "草稿请求", "实验一 SRS"],
    ["限界上下文", "Bounded Context", "DDD 中用于界定模型边界的上下文范围", "上下文", "共享大模型", "实验二设计"],
    ["服务", "Service", "在 monorepo 中可独立部署的业务单元", "微服务", "模块说明", "实验三设计"],
    ["测试用例", "Test Case", "用于验证需求与质量目标的执行步骤集合", "TC", "随机检查", "实验四测试计划"],
  ]);

  const rtm = workbook.worksheets.add("RTM");
  writeBlock(rtm, "A1:G1", [[
    "需求ID",
    "来源",
    "用例ID",
    "类图实体",
    "服务归属",
    "自动化测试用例ID",
    "状态",
  ]]);
  applyHeader(rtm, "A1:G1");
  writeBlock(rtm, "A2:G6", [
    ["FR-001", "顾客访谈", "UC-001", "Member", "member-service", "", "Draft"],
    ["FR-002", "顾客访谈", "UC-002", "Store / Slot", "reservation-service", "", "Draft"],
    ["FR-003", "顾客访谈", "UC-003", "Reservation", "reservation-service", "", "Draft"],
    ["FR-005", "店员访谈", "UC-005", "SeatSchedule", "待定", "", "Draft"],
    ["NFR-001", "总览文档", "", "", "reservation-service", "", "Draft"],
  ]);

  const naming = workbook.worksheets.add("Naming");
  writeBlock(naming, "A1:C1", [["对象类型", "前缀", "示例"]]);
  applyHeader(naming, "A1:C1");
  writeBlock(naming, "A2:C7", [
    ["功能需求", "FR", "FR-001"],
    ["非功能需求", "NFR", "NFR-001"],
    ["用例", "UC", "UC-001"],
    ["限界上下文", "BC", "BC-RESERVATION"],
    ["服务", "SVC", "SVC-RESERVATION"],
    ["测试用例", "TC", "TC-001"],
  ]);

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(foundationDir, "glossary-rtm-master.xlsx"));
}

await fs.mkdir(foundationDir, { recursive: true });
await buildRequirementsWorkbook();
await buildGlossaryWorkbook();
