import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "/Users/qijinyu.0608/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const scriptPath = fileURLToPath(import.meta.url);
const rootDir = path.resolve(path.dirname(scriptPath), "..");
const buildJsonPath = path.join(rootDir, "docs", "lab1", ".build", "lab1_data.json");
const lab1SourceDir = path.join(rootDir, "docs", "lab1", "source");

const payload = JSON.parse(await fs.readFile(buildJsonPath, "utf8"));
const meta = payload.meta;

function artifactFilename(shortName, extension) {
  return `${meta.class_name}_${meta.student_id}_${meta.student_name}_${meta.experiment}_${shortName}_${meta.version}.${extension}`;
}

function styleHeader(range) {
  range.format.font.bold = true;
  range.format.fill.color = "#D86F45";
  range.format.font.color = "#FFFFFF";
  range.format.wrapText = true;
}

function styleBody(range) {
  range.format.wrapText = true;
  range.format.autofitColumns();
  range.format.autofitRows();
}

function addSummarySheet(workbook) {
  const summary = workbook.worksheets.add("需求统计");
  summary.getRange("A1:B1").values = [["指标", "数值"]];
  styleHeader(summary.getRange("A1:B1"));
  const fr = payload.functional_requirements;
  const nfr = payload.non_functional_requirements;
  const mustCount = fr.filter((item) => item.moscow === "Must").length + nfr.filter((item) => item.moscow === "Must").length;
  summary.getRange("A2:B8").values = [
    ["功能需求总数", fr.length],
    ["非功能需求总数", nfr.length],
    ["Must 总数", mustCount],
    ["Should 总数", fr.filter((item) => item.moscow === "Should").length + nfr.filter((item) => item.moscow === "Should").length],
    ["Could 总数", fr.filter((item) => item.moscow === "Could").length + nfr.filter((item) => item.moscow === "Could").length],
    ["涉及限界上下文", new Set(fr.map((item) => item.context)).size],
    ["基线状态需求数", fr.filter((item) => item.status === "Baseline").length + nfr.filter((item) => item.status === "Baseline").length],
  ];
  styleBody(summary.getRange("A2:B8"));
  summary.freezePanes.freezeRows(1);
}

async function buildRequirementsWorkbook() {
  const workbook = Workbook.create();

  const functional = workbook.worksheets.add("功能需求");
  functional.getRange("A1:L1").values = [[
    "ID",
    "需求类别",
    "需求描述",
    "来源(干系人)",
    "MoSCoW",
    "优先级",
    "验收准则(Given-When-Then)",
    "上下文",
    "服务归属",
    "状态",
    "用例ID",
    "类图实体",
  ]];
  styleHeader(functional.getRange("A1:L1"));
  functional.getRange(`A2:L${payload.functional_requirements.length + 1}`).values = payload.functional_requirements.map((item) => [
    item.id,
    item.category,
    item.description,
    item.source,
    item.moscow,
    item.priority,
    item.acceptance,
    item.context,
    item.service,
    item.status,
    item.use_case,
    item.entity,
  ]);
  styleBody(functional.getRange(`A2:L${payload.functional_requirements.length + 1}`));
  functional.freezePanes.freezeRows(1);

  const nonFunctional = workbook.worksheets.add("非功能需求");
  nonFunctional.getRange("A1:J1").values = [[
    "ID",
    "ISO25010 特性",
    "需求描述",
    "来源",
    "MoSCoW",
    "优先级",
    "度量指标",
    "上下文",
    "验证方法",
    "状态",
  ]];
  styleHeader(nonFunctional.getRange("A1:J1"));
  nonFunctional.getRange(`A2:J${payload.non_functional_requirements.length + 1}`).values = payload.non_functional_requirements.map((item) => [
    item.id,
    item.iso,
    item.description,
    item.source,
    item.moscow,
    item.priority,
    item.metric,
    item.context,
    item.verification,
    item.status,
  ]);
  styleBody(nonFunctional.getRange(`A2:J${payload.non_functional_requirements.length + 1}`));
  nonFunctional.freezePanes.freezeRows(1);

  addSummarySheet(workbook);

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(lab1SourceDir, artifactFilename(payload.artifact_names["D1-2"], "xlsx")));
}

async function buildGlossaryWorkbook() {
  const workbook = Workbook.create();

  const glossary = workbook.worksheets.add("Glossary");
  glossary.getRange("A1:F1").values = [[
    "术语",
    "英文",
    "定义",
    "同义词",
    "反义词",
    "出处",
  ]];
  styleHeader(glossary.getRange("A1:F1"));
  glossary.getRange(`A2:F${payload.glossary.length + 1}`).values = payload.glossary.map((item) => [
    item.term,
    item.english,
    item.definition,
    item.synonym,
    item.antonym,
    item.source,
  ]);
  styleBody(glossary.getRange(`A2:F${payload.glossary.length + 1}`));
  glossary.freezePanes.freezeRows(1);

  const rtm = workbook.worksheets.add("RTM");
  rtm.getRange("A1:I1").values = [[
    "需求ID",
    "来源",
    "用例ID",
    "类图实体",
    "图稿编号",
    "测试用例预占ID",
    "当前状态",
    "负责人",
    "备注",
  ]];
  styleHeader(rtm.getRange("A1:I1"));
  const rows = [
    ...payload.functional_requirements.map((item, index) => [
      item.id,
      item.source,
      item.use_case,
      item.entity,
      item.use_case.startsWith("UC-00") ? "UML 主图/子图" : "UML 补图",
      `TC-${String(index + 1).padStart(3, "0")}`,
      item.status,
      meta.student_name,
      `${item.context} / ${item.service}`,
    ]),
    ...payload.non_functional_requirements.map((item, index) => [
      item.id,
      item.source,
      "",
      "",
      "SRS / 验证报告",
      `TC-NFR-${String(index + 1).padStart(2, "0")}`,
      item.status,
      meta.student_name,
      `${item.context} / ${item.verification}`,
    ]),
  ];
  rtm.getRange(`A2:I${rows.length + 1}`).values = rows;
  styleBody(rtm.getRange(`A2:I${rows.length + 1}`));
  rtm.freezePanes.freezeRows(1);

  const naming = workbook.worksheets.add("Naming");
  naming.getRange("A1:C1").values = [["对象类型", "前缀", "示例"]];
  styleHeader(naming.getRange("A1:C1"));
  naming.getRange("A2:C7").values = [
    ["功能需求", "FR", "FR-001"],
    ["非功能需求", "NFR", "NFR-001"],
    ["用例", "UC", "UC-001"],
    ["限界上下文", "BC", "BC-RESERVATION"],
    ["服务", "SVC", "SVC-RESERVATION"],
    ["测试用例", "TC", "TC-001"],
  ];
  styleBody(naming.getRange("A2:C7"));
  naming.freezePanes.freezeRows(1);

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(lab1SourceDir, artifactFilename(payload.artifact_names["D1-5"], "xlsx")));
}

await fs.mkdir(lab1SourceDir, { recursive: true });
await buildRequirementsWorkbook();
await buildGlossaryWorkbook();
