import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import pptxgen from "/Users/qijinyu.0608/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs/dist/pptxgen.es.js";

const scriptPath = fileURLToPath(import.meta.url);
const rootDir = path.resolve(path.dirname(scriptPath), "..");
const buildJsonPath = path.join(rootDir, "docs", "lab1", ".build", "lab1_data.json");
const sourceDir = path.join(rootDir, "docs", "lab1", "source");
const exportsDir = path.join(rootDir, "docs", "lab1", "exports", `${"计算机23-2_231002208_戚晋瑜_实验一_UMLModels_v1.0"}`);
const payload = JSON.parse(await fs.readFile(buildJsonPath, "utf8"));
const meta = payload.meta;

function artifactFilename(shortName, extension) {
  return `${meta.class_name}_${meta.student_id}_${meta.student_name}_${meta.experiment}_${shortName}_${meta.version}.${extension}`;
}

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = meta.student_name;
pptx.company = "北京林业大学";
pptx.subject = "实验一答辩PPT";
pptx.title = "NekoCafé 实验一答辩";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "SimHei",
  bodyFontFace: "Songti SC",
  lang: "zh-CN",
};

function addTitle(slide, title, subtitle = "") {
  slide.addText(title, { x: 0.6, y: 0.4, w: 8.5, h: 0.6, fontFace: "SimHei", fontSize: 24, bold: true, color: "2F2F2F" });
  if (subtitle) {
    slide.addText(subtitle, { x: 0.6, y: 1.0, w: 8.0, h: 0.3, fontFace: "Songti SC", fontSize: 10, color: "7A7A7A" });
  }
  slide.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.35, w: 1.6, h: 0.08, fill: { color: "D86F45" }, line: { color: "D86F45" } });
}

function addBulletList(slide, items, x = 0.9, y = 1.8, w = 5.4) {
  let offset = y;
  for (const item of items) {
    slide.addText(`• ${item}`, { x, y: offset, w, h: 0.45, fontFace: "Songti SC", fontSize: 16, color: "333333", breakLine: false });
    offset += 0.45;
  }
}

function coverSlide() {
  const slide = pptx.addSlide();
  slide.background = { color: "FBF7F2" };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.8, fill: { color: "D86F45" }, line: { color: "D86F45" } });
  slide.addText("实验一：智能化需求工程与 UML 建模", { x: 0.8, y: 1.2, w: 8.8, h: 0.8, fontFace: "SimHei", fontSize: 28, bold: true, color: "2F2F2F" });
  slide.addText("NekoCafé 猫咪主题餐饮预约平台", { x: 0.8, y: 2.2, w: 7.5, h: 0.5, fontFace: "Songti SC", fontSize: 20, color: "5C5C5C" });
  slide.addText(`${meta.class_name}  ${meta.student_id}  ${meta.student_name}`, { x: 0.8, y: 3.0, w: 6.0, h: 0.4, fontFace: "Songti SC", fontSize: 16, color: "7A7A7A" });
  slide.addText("统一案例贯穿四次软件工程实验", { x: 0.8, y: 4.1, w: 4.2, h: 0.4, fontFace: "Songti SC", fontSize: 16, color: "D86F45" });
  slide.addImage({ path: path.join(exportsDir, "usecase", "U01_主用例图.png"), x: 7.9, y: 1.4, w: 4.6, h: 3.3 });
}

function contentSlide(title, subtitle, bullets, imagePath = null) {
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  addTitle(slide, title, subtitle);
  addBulletList(slide, bullets);
  if (imagePath) {
    slide.addImage({ path: imagePath, x: 7.0, y: 1.7, w: 5.5, h: 4.2 });
  } else {
    slide.addShape(pptx.ShapeType.roundRect, { x: 7.2, y: 1.9, w: 5.2, h: 3.6, fill: { color: "F6EEE6" }, line: { color: "E5D2C3", pt: 1.2 }, radius: 0.12 });
    slide.addText("本页以结论 + 证据结构呈现", { x: 7.8, y: 3.25, w: 4.0, h: 0.5, fontFace: "Songti SC", fontSize: 18, color: "8A6B55", align: "center" });
  }
}

coverSlide();
contentSlide("个人分工", "以个人提交口径组织实验一交付", ["需求获取与 AI 访谈脚本设计", "FR/NFR 主表、Glossary、RTM 建立", "UML 图集、SRS、验证报告与 AI 记录定稿"]);
contentSlide("案例与干系人地图", "统一案例作为四次实验唯一业务背景", ["顾客关注预约便捷、价格透明与互动体验", "店员关注排台效率、异常处理与健康打卡", "运营总监关注跨店经营、活动效果与合规审计"], path.join(rootDir, "docs", "lab1", ".build", "priority_matrix.png"));
contentSlide("需求获取过程", "AI 扩面，人工定边界", ["先按顾客、店员、运营总监三类角色生成访谈大纲", "再完成 4 轮模拟访谈并归并 30+10 条需求", "最后通过 MoSCoW、Glossary、RTM 收敛基线"], path.join(rootDir, "docs", "lab1", ".build", "onion_model.png"));
contentSlide("需求清单概览", "功能需求与非功能需求同源整理", ["功能需求 30 条，覆盖会员、预约、运营、猫咪健康等能力", "非功能需求 10 条，覆盖性能、可靠性、安全性、易用性", "所有功能需求均附 Given-When-Then 验收准则"]);
contentSlide("主用例图", "顾客、店员、运营三条主链路", ["主图覆盖预约、会员、排台、健康打卡、运营分析", "子图继续拆出会员域与预约域", "推荐与通知通过 include / extend 关系表达"], path.join(exportsDir, "usecase", "U01_主用例图.png"));
contentSlide("活动与顺序图", "从流程到跨服务调用", ["活动图说明桌位预约和猫咪健康打卡的控制流", "顺序图说明预约创建与店员到店处理的调用链", "为实验二服务拆分与实验三 PoC 提供直接输入"], path.join(exportsDir, "activity", "A01_桌位预约活动图.png"));
contentSlide("类图与状态图", "实体、关系与生命周期闭环", ["领域类图保留 16 个核心实体，支持后续服务拆分", "订单状态机覆盖待确认、已确认、已到店、已入座、已离店、已取消、已爽约", "图稿与 RTM 保持双向追溯"], path.join(exportsDir, "class", "C01_领域类图.png"));
contentSlide("非功能需求与合规", "性能与合规作为架构驱动力", ["预约主链路要求 5000 QPS 与 99.9% SLA", "个人信息处理需符合个保法并具备审计留痕", "店员后台需支持异常颜色区分和移动端兼容性"], path.join(exportsDir, "state", "T01_订单状态机.png"));
contentSlide("需求验证发现", "二义性、冲突、缺失三类问题", ["桌位偏好、取消/爽约规则、推荐解释性是初稿主要问题", "通知失败重试和猫咪异常分流被补充进基线", "除活动授权边界外，requirements-v1.0 可冻结"]);
contentSlide("后续实验输入", "实验一向实验二到实验四持续供数", ["实验二继续沿用 FR/NFR/UC/BC/SVC/TC 编号体系", "实验三聚焦 member-service 与 reservation-service 两个核心服务", "实验四在同一 RTM 上回填测试用例和缺陷追踪"]);
contentSlide("Q&A", "欢迎围绕需求、图稿与追溯链继续追问", ["可继续展开单个用例的流程细节", "可进一步解释某张 UML 图与需求的映射", "也可继续补最终 PDF / ZIP 提交态产物"]);

await fs.mkdir(sourceDir, { recursive: true });
await pptx.writeFile({ fileName: path.join(sourceDir, artifactFilename(payload.artifact_names["D1-8"], "pptx")) });
