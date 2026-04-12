const runtime = window.APP_RUNTIME || {};

const TEXT = {
  "zh-CN": {
    pageTitle: "混合陶瓷球轴承电容分析平台",
    pageIntro:
      "统一计算混合陶瓷球轴承的本体电容、寄生并联网络、分压、电场和风险等级，并保留更轻量的页面交互。",
    runtimeCardLabel: "运行环境",
    runtimeCardValueFlask: "Flask Runtime",
    runtimeCardValuePages: "GitHub Pages + Pyodide",
    modelCardLabel: "模型版本",
    noteCardLabel: "模型说明",
    controlsEyebrow: "Study Setup",
    controlsTitle: "工况设置",
    singleMode: "单工况",
    compareMode: "Case A / B",
    languageLabel: "语言",
    capacitanceUnitLabel: "电容单位",
    fieldUnitLabel: "场强单位",
    loadUnitLabel: "载荷单位",
    exportCaseLabel: "CSV 导出对象",
    calculateButton: "计算",
    shareButton: "复制分享链接",
    pdfButton: "导出 PDF",
    csvButton: "导出单球 CSV",
    statusReady: "准备就绪",
    statusLoadingRuntime: "加载 Python 运行时...",
    statusLoadingPackages: "加载数值计算库...",
    statusLoadingModel: "加载共享模型...",
    statusLoadingConfig: "读取共享配置...",
    statusCalculating: "计算中...",
    statusComplete: "计算完成",
    statusCopied: "分享链接已复制",
    statusPdfDone: "PDF 已导出",
    statusCsvDone: "CSV 已导出",
    statusFailed: "计算失败",
    summaryEyebrow: "Results",
    summaryTitle: "关键结果",
    summaryNote: "同时展示本体电容、寄生并联、电场、阻抗和风险判断。",
    comparisonEyebrow: "Compare",
    comparisonTitle: "Case A / B 差异",
    comparisonNote: "展示等效总电容、油膜场强和风险等级差值。",
    explanationsEyebrow: "Interpretation",
    explanationsTitle: "结果解释",
    factorsEyebrow: "Drivers",
    factorsTitle: "关键指标",
    voltageChartEyebrow: "Voltage",
    voltageChartTitle: "三段分压",
    fieldChartEyebrow: "Field",
    fieldChartTitle: "三段场强",
    frequencyChartEyebrow: "Impedance",
    frequencyChartTitle: "扫频阻抗",
    sweepChartEyebrow: "Sweep",
    sweepChartTitle: "扫参趋势",
    sweepVariableLabel: "变量",
    sweepMetricLabel: "指标",
    sensitivityChartEyebrow: "Sensitivity",
    sensitivityChartTitle: "敏感性排序",
    sensitivityMetricLabel: "排序指标",
    detailsEyebrow: "Path Detail",
    detailsTitle: "单球明细",
    detailsNote: "每条路径都按内圈油膜、陶瓷球本体、外圈油膜的串联网络求解。",
    caseATitle: "Case A",
    caseANote: "默认用于当前工况分析。",
    caseBTitle: "Case B",
    caseBNote: "用于并列比较第二组工况。",
    modelNoteFallback: "纯电容阻抗模型，不含泄漏电阻或导电油膜支路。",
    diagnosticModel: "模型加载失败",
    diagnosticValidation: "参数校验失败",
    diagnosticRender: "页面渲染失败",
    diagnosticPdf: "PDF 导出失败",
    diagnosticUnknown: "运行失败",
    copyFailed: "复制失败，请手动复制当前地址。",
    intrinsicCapacitance: "轴承本体电容",
    effectiveCapacitance: "测量等效总电容",
    parasiticTotal: "显式寄生总电容",
    spotImpedance: "单点阻抗 |Z|",
    loadedBalls: "加载滚动体数量",
    maxOilField: "最大油膜场强",
    riskLevel: "风险等级",
    dominantSegment: "主分压承担段",
    comparisonCapDelta: "总电容差值",
    comparisonFieldDelta: "最大场强差值",
    comparisonRiskDelta: "风险等级差值",
    comparisonSegmentShift: "主段/风险段变化",
    caseAEffective: "Case A 总电容",
    caseBEffective: "Case B 总电容",
    caseARisk: "Case A 风险",
    caseBRisk: "Case B 风险",
    caseAField: "Case A 最大油膜场强",
    caseBField: "Case B 最大油膜场强",
    caseADominant: "Case A 主分压段",
    caseBDominant: "Case B 主分压段",
    explanationCeramicTitle: "为什么陶瓷球分压最大",
    explanationCeramicBody:
      "串联通路中三段电荷相同，小电容承担大电压。当前结果里陶瓷球段的平均分压最高，因此它是主分压承担段。",
    explanationRiskTitle: "当前风险主要由哪一段触发",
    explanationParasiticTitle: "当前是本体主导还是寄生主导",
    explanationImpedanceTitle: "阻抗读数如何理解",
    explanationRiskCompareTitle: "两组工况的风险对比",
    explanationParasiticCompareTitle: "两组工况的主导模式对比",
    parasiticDominant: "寄生主导",
    intrinsicDominant: "本体主导",
    detailSectionSingle: "当前工况",
    detailSectionCaseA: "Case A 单球明细",
    detailSectionCaseB: "Case B 单球明细",
    noDetail: "当前工况下没有加载滚动体路径。",
    tableAngle: "角位置",
    tableLoad: "载荷",
    tableContactAngle: "接触角",
    tableInnerFilm: "内圈膜厚",
    tableOuterFilm: "外圈膜厚",
    tableInnerCap: "内圈油膜",
    tableCeramicCap: "陶瓷球本体",
    tableOuterCap: "外圈油膜",
    tablePathCap: "串联等效",
    tableInnerVoltage: "内圈分压",
    tableCeramicVoltage: "陶瓷球分压",
    tableOuterVoltage: "外圈分压",
    tableInnerField: "内圈场强",
    tableCeramicField: "陶瓷等效场强",
    tableOuterField: "外圈场强",
    tableDominant: "主承担段",
    metricTotalCapacitance: "总电容",
    metricMaxField: "最大油膜场强",
    metricRiskNumeric: "风险等级",
    sweepVariableSpeed: "转速",
    sweepVariableTemperature: "温度",
    sweepVariableRadialLoad: "径向载荷",
    sensitivityMetricCap: "总电容",
    sensitivityMetricField: "最大油膜场强",
    sensitivityMetricRisk: "风险等级",
    fieldRiskReasonStable: "当前最大油膜场强较低且 λ 比保持在安全区间，属于稳定 EHL 状态。",
    fieldRiskReasonAbove2: "最大油膜场强超过 2 MV/m，进入中等风险区。",
    fieldRiskReasonAbove5: "最大油膜场强超过 5 MV/m，进入高风险区。",
    fieldRiskReasonAbove10: "最大油膜场强超过 10 MV/m，已落入临界风险区。",
    fieldRiskReasonBelow3: "最小 λ 比低于 3，表明粗糙峰影响开始显著。",
    fieldRiskReasonBelow15: "最小 λ 比低于 1.5，油膜安全裕度已经偏小。",
    fieldRiskReasonBelow1: "最小 λ 比低于 1，意味着接触逼近或进入边界润滑状态。",
    csvCaseA: "Case A",
    csvCaseB: "Case B",
    footerVersionPrefix: "Model v",
    shareLinkCopied: "当前参数已写入 URL，并复制到剪贴板。",
    sweepXAxisSpeed: "转速 (rpm)",
    sweepXAxisTemperature: "温度 (°C)",
    sweepXAxisLoad: "径向载荷",
    frequencyXAxis: "频率 (Hz)",
    frequencyYAxis: "阻抗 (Ω)",
    voltageYAxis: "分压占比 (%)",
    fieldYAxis: "等效场强",
    sensitivityXAxisCap: "最大绝对变化 (pF)",
    sensitivityXAxisField: "最大绝对变化 (MV/m)",
    sensitivityXAxisRisk: "最大绝对变化 (风险等级)",
    pdfTitle: "混合陶瓷球轴承电容分析报告",
    pdfSectionInputs: "输入摘要",
    pdfSectionSummary: "关键结果",
    pdfSectionCompare: "对比结论",
    pdfSectionCharts: "图表"
  },
  "en-US": {
    pageTitle: "Hybrid Ceramic Bearing Capacitance Studio",
    pageIntro:
      "Unified analysis of intrinsic bearing capacitance, explicit parasitic branches, voltage split, electric field, and risk level with a lighter UI path.",
    runtimeCardLabel: "Runtime",
    runtimeCardValueFlask: "Flask Runtime",
    runtimeCardValuePages: "GitHub Pages + Pyodide",
    modelCardLabel: "Model Version",
    noteCardLabel: "Model Note",
    controlsEyebrow: "Study Setup",
    controlsTitle: "Inputs",
    singleMode: "Single Case",
    compareMode: "Case A / B",
    languageLabel: "Language",
    capacitanceUnitLabel: "Capacitance Unit",
    fieldUnitLabel: "Field Unit",
    loadUnitLabel: "Load Unit",
    exportCaseLabel: "CSV Target",
    calculateButton: "Calculate",
    shareButton: "Copy Share Link",
    pdfButton: "Export PDF",
    csvButton: "Export Ball CSV",
    statusReady: "Ready",
    statusLoadingRuntime: "Loading Python runtime...",
    statusLoadingPackages: "Loading numeric packages...",
    statusLoadingModel: "Loading shared model...",
    statusLoadingConfig: "Loading shared config...",
    statusCalculating: "Calculating...",
    statusComplete: "Complete",
    statusCopied: "Share link copied",
    statusPdfDone: "PDF exported",
    statusCsvDone: "CSV exported",
    statusFailed: "Failed",
    summaryEyebrow: "Results",
    summaryTitle: "Key Results",
    summaryNote: "Intrinsic capacitance, parasitic branches, field, impedance, and risk are shown together.",
    comparisonEyebrow: "Compare",
    comparisonTitle: "Case A / B Delta",
    comparisonNote: "Shows total capacitance, oil-film field, and risk-level deltas.",
    explanationsEyebrow: "Interpretation",
    explanationsTitle: "Interpretation",
    factorsEyebrow: "Drivers",
    factorsTitle: "Key Indicators",
    voltageChartEyebrow: "Voltage",
    voltageChartTitle: "Voltage Split",
    fieldChartEyebrow: "Field",
    fieldChartTitle: "Segment Field",
    frequencyChartEyebrow: "Impedance",
    frequencyChartTitle: "Frequency Sweep",
    sweepChartEyebrow: "Sweep",
    sweepChartTitle: "Operating Sweeps",
    sweepVariableLabel: "Variable",
    sweepMetricLabel: "Metric",
    sensitivityChartEyebrow: "Sensitivity",
    sensitivityChartTitle: "Sensitivity Ranking",
    sensitivityMetricLabel: "Ranking Metric",
    detailsEyebrow: "Path Detail",
    detailsTitle: "Per-Ball Details",
    detailsNote: "Each path is solved as inner oil film, ceramic body, and outer oil film in series.",
    caseATitle: "Case A",
    caseANote: "Default working case.",
    caseBTitle: "Case B",
    caseBNote: "Second working case for side-by-side comparison.",
    modelNoteFallback: "Pure capacitive impedance model without leakage resistance or conductive oil-film branches.",
    diagnosticModel: "Model Load Failure",
    diagnosticValidation: "Validation Failure",
    diagnosticRender: "Rendering Failure",
    diagnosticPdf: "PDF Export Failure",
    diagnosticUnknown: "Runtime Failure",
    copyFailed: "Copy failed. Please copy the URL manually.",
    intrinsicCapacitance: "Intrinsic Bearing Capacitance",
    effectiveCapacitance: "Measured Total Capacitance",
    parasiticTotal: "Explicit Parasitic Total",
    spotImpedance: "Spot Impedance |Z|",
    loadedBalls: "Loaded Ball Count",
    maxOilField: "Max Oil-Film Field",
    riskLevel: "Risk Level",
    dominantSegment: "Dominant Voltage Segment",
    comparisonCapDelta: "Total Capacitance Delta",
    comparisonFieldDelta: "Max Field Delta",
    comparisonRiskDelta: "Risk Level Delta",
    comparisonSegmentShift: "Segment Change Flags",
    caseAEffective: "Case A Total Capacitance",
    caseBEffective: "Case B Total Capacitance",
    caseARisk: "Case A Risk",
    caseBRisk: "Case B Risk",
    caseAField: "Case A Max Oil-Film Field",
    caseBField: "Case B Max Oil-Film Field",
    caseADominant: "Case A Dominant Segment",
    caseBDominant: "Case B Dominant Segment",
    explanationCeramicTitle: "Why the ceramic segment takes most voltage",
    explanationCeramicBody:
      "Series segments carry the same charge. The smallest capacitance therefore takes the largest voltage drop. In this result the ceramic segment has the highest mean voltage share.",
    explanationRiskTitle: "What drives the present risk level",
    explanationParasiticTitle: "Intrinsic-dominant or parasitic-dominant",
    explanationImpedanceTitle: "How to read the impedance result",
    explanationRiskCompareTitle: "Risk comparison between the two cases",
    explanationParasiticCompareTitle: "Dominance mode comparison",
    parasiticDominant: "Parasitic-dominant",
    intrinsicDominant: "Intrinsic-dominant",
    detailSectionSingle: "Active Case",
    detailSectionCaseA: "Case A Ball Paths",
    detailSectionCaseB: "Case B Ball Paths",
    noDetail: "No loaded rolling-element path exists under the current condition.",
    tableAngle: "Angle",
    tableLoad: "Load",
    tableContactAngle: "Contact Angle",
    tableInnerFilm: "Inner Film",
    tableOuterFilm: "Outer Film",
    tableInnerCap: "Inner Film Cap",
    tableCeramicCap: "Ceramic Body Cap",
    tableOuterCap: "Outer Film Cap",
    tablePathCap: "Series Total",
    tableInnerVoltage: "Inner Voltage",
    tableCeramicVoltage: "Ceramic Voltage",
    tableOuterVoltage: "Outer Voltage",
    tableInnerField: "Inner Field",
    tableCeramicField: "Ceramic Eq Field",
    tableOuterField: "Outer Field",
    tableDominant: "Dominant Segment",
    metricTotalCapacitance: "Total Capacitance",
    metricMaxField: "Max Oil-Film Field",
    metricRiskNumeric: "Risk Level",
    sweepVariableSpeed: "Speed",
    sweepVariableTemperature: "Temperature",
    sweepVariableRadialLoad: "Radial Load",
    sensitivityMetricCap: "Total Capacitance",
    sensitivityMetricField: "Max Oil-Film Field",
    sensitivityMetricRisk: "Risk Level",
    fieldRiskReasonStable: "The maximum oil-film field is low and lambda remains in a safe range, indicating stable EHL operation.",
    fieldRiskReasonAbove2: "The maximum oil-film field exceeds 2 MV/m and enters the medium-risk band.",
    fieldRiskReasonAbove5: "The maximum oil-film field exceeds 5 MV/m and enters the high-risk band.",
    fieldRiskReasonAbove10: "The maximum oil-film field exceeds 10 MV/m and falls in the critical band.",
    fieldRiskReasonBelow3: "The minimum lambda ratio falls below 3, so roughness interaction becomes important.",
    fieldRiskReasonBelow15: "The minimum lambda ratio falls below 1.5 and the film margin is becoming small.",
    fieldRiskReasonBelow1: "The minimum lambda ratio falls below 1, indicating near-boundary or boundary lubrication.",
    csvCaseA: "Case A",
    csvCaseB: "Case B",
    footerVersionPrefix: "Model v",
    shareLinkCopied: "The current parameters were written to the URL and copied to the clipboard.",
    sweepXAxisSpeed: "Speed (rpm)",
    sweepXAxisTemperature: "Temperature (°C)",
    sweepXAxisLoad: "Radial Load",
    frequencyXAxis: "Frequency (Hz)",
    frequencyYAxis: "Impedance (Ohm)",
    voltageYAxis: "Voltage Share (%)",
    fieldYAxis: "Equivalent Field",
    sensitivityXAxisCap: "Max absolute change (pF)",
    sensitivityXAxisField: "Max absolute change (MV/m)",
    sensitivityXAxisRisk: "Max absolute change (risk level)",
    pdfTitle: "Hybrid Ceramic Bearing Capacitance Report",
    pdfSectionInputs: "Input Summary",
    pdfSectionSummary: "Key Results",
    pdfSectionCompare: "Comparison",
    pdfSectionCharts: "Charts"
  }
};

const SEGMENT_TEXT = {
  "zh-CN": {
    inner_oil_film: "内圈油膜",
    ceramic_ball: "陶瓷球本体",
    outer_oil_film: "外圈油膜",
    parasitic_total: "寄生网络",
    no_loaded_path: "无加载通路"
  },
  "en-US": {
    inner_oil_film: "Inner Oil Film",
    ceramic_ball: "Ceramic Ball",
    outer_oil_film: "Outer Oil Film",
    parasitic_total: "Parasitic Network",
    no_loaded_path: "No Loaded Path"
  }
};

const RISK_TEXT = {
  "zh-CN": { low: "低", medium: "中", high: "高", critical: "临界" },
  "en-US": { low: "Low", medium: "Medium", high: "High", critical: "Critical" }
};

const REASON_TEXT = {
  "zh-CN": {
    stable_ehl: TEXT["zh-CN"].fieldRiskReasonStable,
    field_above_2: TEXT["zh-CN"].fieldRiskReasonAbove2,
    field_above_5: TEXT["zh-CN"].fieldRiskReasonAbove5,
    field_above_10: TEXT["zh-CN"].fieldRiskReasonAbove10,
    lambda_below_3: TEXT["zh-CN"].fieldRiskReasonBelow3,
    lambda_below_1_5: TEXT["zh-CN"].fieldRiskReasonBelow15,
    lambda_below_1: TEXT["zh-CN"].fieldRiskReasonBelow1
  },
  "en-US": {
    stable_ehl: TEXT["en-US"].fieldRiskReasonStable,
    field_above_2: TEXT["en-US"].fieldRiskReasonAbove2,
    field_above_5: TEXT["en-US"].fieldRiskReasonAbove5,
    field_above_10: TEXT["en-US"].fieldRiskReasonAbove10,
    lambda_below_3: TEXT["en-US"].fieldRiskReasonBelow3,
    lambda_below_1_5: TEXT["en-US"].fieldRiskReasonBelow15,
    lambda_below_1: TEXT["en-US"].fieldRiskReasonBelow1
  }
};

const PARAMETER_TEXT = {
  "zh-CN": {
    ball_diameter_mm: "球径 Dw",
    pitch_diameter_mm: "节圆直径 / PCD",
    composite_roughness_um: "综合粗糙度",
    ceramic_relative_permittivity: "陶瓷介电常数",
    relative_permittivity_25c: "油品介电常数",
    background_capacitance_pf: "背景电容",
    radial_load_n: "径向载荷",
    inner_ring_temp_c: "内圈温度"
  },
  "en-US": {
    ball_diameter_mm: "Ball Diameter Dw",
    pitch_diameter_mm: "Pitch Diameter / PCD",
    composite_roughness_um: "Composite Roughness",
    ceramic_relative_permittivity: "Ceramic Permittivity",
    relative_permittivity_25c: "Oil Permittivity",
    background_capacitance_pf: "Background Capacitance",
    radial_load_n: "Radial Load",
    inner_ring_temp_c: "Inner Ring Temp"
  }
};

const RESERVED_QUERY_KEYS = new Set([
  "mode",
  "lang",
  "capacitance_unit",
  "field_unit",
  "load_unit",
  "export_case",
  "case"
]);

const BRIDGE_CODE = String.raw`
import json
from hybrid_bearing_capacitance import analyze_case_payload, compare_case_payloads

def analyze_single_from_json(raw_text):
    payload = json.loads(raw_text)
    return json.dumps(analyze_case_payload(payload), ensure_ascii=False)

def analyze_compare_from_json(case_a_raw, case_b_raw):
    case_a = json.loads(case_a_raw)
    case_b = json.loads(case_b_raw)
    return json.dumps(compare_case_payloads(case_a, case_b), ensure_ascii=False)
`;

const state = {
  config: null,
  mode: "single",
  lang: "zh-CN",
  units: {
    capacitance: "pF",
    field: "MV/m",
    load: "N"
  },
  sweepVariable: "speed",
  sweepMetric: "effective_capacitance_pf",
  sensitivityMetric: "effective_capacitance_pf",
  exportCase: "a",
  caseValues: {
    a: {},
    b: {}
  },
  result: null
};

let pyodideRuntime = null;

function $(id) {
  return document.getElementById(id);
}

function t(key) {
  return TEXT[state.lang][key] || key;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function localeText(bundle) {
  if (!bundle) {
    return "";
  }
  return bundle[state.lang] || bundle["zh-CN"] || bundle["en-US"] || "";
}

function segmentLabel(code) {
  return SEGMENT_TEXT[state.lang][code] || code;
}

function riskLabel(level) {
  return RISK_TEXT[state.lang][level] || level;
}

function reasonLabel(code) {
  return REASON_TEXT[state.lang][code] || code;
}

function parameterLabel(parameter) {
  return PARAMETER_TEXT[state.lang][parameter] || parameter;
}

function formatNumber(value, digits = 4) {
  if (!Number.isFinite(Number(value))) {
    return "∞";
  }
  return Number(value).toFixed(digits);
}

function formatCapacitanceValue(valuePf, digits = 4) {
  if (state.units.capacitance === "nF") {
    return `${formatNumber(Number(valuePf) / 1000, Math.max(digits + 2, 6))} nF`;
  }
  return `${formatNumber(valuePf, digits)} pF`;
}

function formatFieldValue(valueMvM, digits = 3) {
  const numeric = Number(valueMvM);
  if (state.units.field === "V/um") {
    return `${formatNumber(numeric, digits)} V/μm`;
  }
  return `${formatNumber(numeric, digits)} MV/m`;
}

function formatLoadValue(valueN, digits = 2) {
  const numeric = Number(valueN);
  if (state.units.load === "kN") {
    return `${formatNumber(numeric / 1000, Math.max(digits + 1, 3))} kN`;
  }
  return `${formatNumber(numeric, digits)} N`;
}

function formatPercent(value, digits = 2) {
  return `${formatNumber(Number(value) * 100, digits)}%`;
}

function formatVoltage(value, digits = 4) {
  return `${formatNumber(value, digits)} V`;
}

function formatOhm(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return "∞ Ω";
  }
  if (numeric === 0) {
    return "0 Ω";
  }
  if (Math.abs(numeric) >= 100000 || Math.abs(numeric) < 0.1) {
    return `${numeric.toExponential(3)} Ω`;
  }
  return `${numeric.toFixed(3)} Ω`;
}

function createError(kind, message) {
  const error = new Error(message);
  error.kind = kind;
  return error;
}

function setStatus(message) {
  $("status-pill").textContent = message;
}

function clearError() {
  $("error-box").classList.add("hidden");
  $("error-box").innerHTML = "";
}

function showDiagnostic(kind, message) {
  const titleKey = {
    model: "diagnosticModel",
    validation: "diagnosticValidation",
    render: "diagnosticRender",
    pdf: "diagnosticPdf"
  }[kind] || "diagnosticUnknown";
  $("error-box").innerHTML = `<strong>${escapeHtml(t(titleKey))}</strong><div>${escapeHtml(message)}</div>`;
  $("error-box").classList.remove("hidden");
}

async function fetchConfig() {
  setStatus(t("statusLoadingConfig"));
  const response = await fetch(runtime.configUrl, { cache: "no-store" });
  if (!response.ok) {
    throw createError("model", "Unable to load shared UI configuration.");
  }
  return response.json();
}

async function apiCalculate(body) {
  const response = await fetch(runtime.calculateUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw createError(data.error_type === "validation" ? "validation" : "model", data.error || "Calculation failed.");
  }
  return data;
}

async function ensurePagesRuntime() {
  if (pyodideRuntime) {
    return pyodideRuntime;
  }
  if (typeof loadPyodide !== "function") {
    throw createError("model", "Pyodide runtime is unavailable.");
  }

  setStatus(t("statusLoadingRuntime"));
  pyodideRuntime = await loadPyodide({ indexURL: runtime.pyodideIndexUrl });
  setStatus(t("statusLoadingPackages"));
  await pyodideRuntime.loadPackage(["numpy", "scipy"]);

  setStatus(t("statusLoadingModel"));
  const response = await fetch(runtime.modelUrl, { cache: "no-store" });
  if (!response.ok) {
    throw createError("model", "Unable to load the shared Python model.");
  }
  const source = await response.text();
  pyodideRuntime.FS.writeFile("hybrid_bearing_capacitance.py", source);
  await pyodideRuntime.runPythonAsync(
    "import importlib\nimport hybrid_bearing_capacitance\nimportlib.reload(hybrid_bearing_capacitance)"
  );
  pyodideRuntime.runPython(BRIDGE_CODE);
  return pyodideRuntime;
}

async function pagesCalculateSingle(payload) {
  const runtimeHandle = await ensurePagesRuntime();
  runtimeHandle.globals.set("single_payload_json", JSON.stringify(payload));
  const raw = await runtimeHandle.runPythonAsync("analyze_single_from_json(single_payload_json)");
  runtimeHandle.globals.delete("single_payload_json");
  return JSON.parse(raw);
}

async function pagesCalculateCompare(caseAPayload, caseBPayload) {
  const runtimeHandle = await ensurePagesRuntime();
  runtimeHandle.globals.set("case_a_payload_json", JSON.stringify(caseAPayload));
  runtimeHandle.globals.set("case_b_payload_json", JSON.stringify(caseBPayload));
  const raw = await runtimeHandle.runPythonAsync(
    "analyze_compare_from_json(case_a_payload_json, case_b_payload_json)"
  );
  runtimeHandle.globals.delete("case_a_payload_json");
  runtimeHandle.globals.delete("case_b_payload_json");
  return JSON.parse(raw);
}

function currentCasePayload(caseKey) {
  return deepClone(state.caseValues[caseKey]);
}

function currentSingleResult() {
  if (!state.result) {
    return null;
  }
  return state.mode === "compare"
    ? state.exportCase === "b"
      ? state.result.case_b
      : state.result.case_a
    : state.result;
}

function valueFromParams(params, key, fallback) {
  return params.has(key) ? params.get(key) : fallback;
}

function initStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const baseDefaults = state.config.defaults;
  const buildCaseState = (prefix = "") => {
    const next = {};
    Object.keys(baseDefaults).forEach((key) => {
      next[key] = String(valueFromParams(params, `${prefix}${key}`, baseDefaults[key]));
    });
    const tempKey = `${prefix}temperature_c`;
    if (params.has(tempKey)) {
      next.inner_ring_temp_c = params.get(tempKey);
      next.outer_ring_temp_c = params.get(tempKey);
    }
    return next;
  };

  state.mode = params.get("mode") === "compare" ? "compare" : "single";
  state.units.capacitance = params.get("capacitance_unit") || "pF";
  state.units.field = params.get("field_unit") || "MV/m";
  state.units.load = params.get("load_unit") || "N";
  state.exportCase = params.get("export_case") || "a";
  state.caseValues.a = buildCaseState(state.mode === "compare" ? "a_" : "");
  const comparePayloadFound = Array.from(params.keys()).some((key) => key.startsWith("b_"));
  state.caseValues.b = comparePayloadFound ? buildCaseState("b_") : deepClone(state.caseValues.a);
}

function determineInitialLanguage() {
  const params = new URLSearchParams(window.location.search);
  if (runtime.kind === "pages") {
    return localStorage.getItem("bearing_capacitance_lang") || params.get("lang") || runtime.initialLang || "zh-CN";
  }
  return params.get("lang") || runtime.initialLang || "zh-CN";
}

function applyPreset(caseKey, presetName) {
  const preset = state.config.presets[presetName];
  if (!preset) {
    return;
  }
  state.caseValues[caseKey].bearing_code = presetName;
  Object.entries(preset).forEach(([key, value]) => {
    state.caseValues[caseKey][key] = String(value);
  });
}

function syncCaseStateFromDom() {
  ["a", "b"].forEach((caseKey) => {
    const host = $(`case-${caseKey}-panel`);
    if (!host) {
      return;
    }
    host.querySelectorAll("input, select").forEach((element) => {
      state.caseValues[caseKey][element.name] = element.value;
    });
  });
}

function renderStaticText() {
  $("page-title").textContent = t("pageTitle");
  $("page-intro").textContent = t("pageIntro");
  $("runtime-card-label").textContent = t("runtimeCardLabel");
  $("runtime-card-value").textContent =
    runtime.kind === "pages" ? t("runtimeCardValuePages") : t("runtimeCardValueFlask");
  $("model-card-label").textContent = t("modelCardLabel");
  $("note-card-label").textContent = t("noteCardLabel");
  $("model-note").textContent = runtime.modelNote || t("modelNoteFallback");
  $("controls-eyebrow").textContent = t("controlsEyebrow");
  $("controls-title").textContent = t("controlsTitle");
  $("single-mode-button").textContent = t("singleMode");
  $("compare-mode-button").textContent = t("compareMode");
  $("language-label").textContent = t("languageLabel");
  $("capacitance-unit-label").textContent = t("capacitanceUnitLabel");
  $("field-unit-label").textContent = t("fieldUnitLabel");
  $("load-unit-label").textContent = t("loadUnitLabel");
  $("export-case-label").textContent = t("exportCaseLabel");
  $("calculate-button").textContent = t("calculateButton");
  $("share-button").textContent = t("shareButton");
  $("pdf-button").textContent = t("pdfButton");
  $("csv-button").textContent = t("csvButton");
  $("summary-eyebrow").textContent = t("summaryEyebrow");
  $("summary-title").textContent = t("summaryTitle");
  $("summary-note").textContent = t("summaryNote");
  $("comparison-eyebrow").textContent = t("comparisonEyebrow");
  $("comparison-title").textContent = t("comparisonTitle");
  $("comparison-note").textContent = t("comparisonNote");
  $("explanations-eyebrow").textContent = t("explanationsEyebrow");
  $("explanations-title").textContent = t("explanationsTitle");
  $("factors-eyebrow").textContent = t("factorsEyebrow");
  $("factors-title").textContent = t("factorsTitle");
  $("details-eyebrow").textContent = t("detailsEyebrow");
  $("details-title").textContent = t("detailsTitle");
  $("details-note").textContent = t("detailsNote");
  $("case-a-title").textContent = t("caseATitle");
  $("case-a-note").textContent = t("caseANote");
  $("case-b-title").textContent = t("caseBTitle");
  $("case-b-note").textContent = t("caseBNote");
  $("footer-version").textContent = `${t("footerVersionPrefix")}${runtime.modelVersion || state.config.version}`;
  $("footer-note").textContent = runtime.modelNote || t("modelNoteFallback");
  $("export-case-select").options[0].textContent = t("csvCaseA");
  $("export-case-select").options[1].textContent = t("csvCaseB");

  $("single-mode-button").classList.toggle("active", state.mode === "single");
  $("compare-mode-button").classList.toggle("active", state.mode === "compare");
  $("case-b-panel").classList.toggle("hidden", state.mode !== "compare");
  $("export-case-field").classList.toggle("hidden", state.mode !== "compare");
}

function renderCaseGroups(caseKey) {
  const values = state.caseValues[caseKey];
  const html = state.config.groups
    .map((group) => {
      const fields = group.fields
        .map((field) => {
          const currentValue = values[field.name] ?? state.config.defaults[field.name] ?? "";
          const input =
            field.kind === "select"
              ? `<select name="${escapeHtml(field.name)}">${field.options
                  .map((option) => {
                    const selected = String(currentValue) === String(option.value) ? " selected" : "";
                    return `<option value="${escapeHtml(option.value)}"${selected}>${escapeHtml(
                      localeText(option.label)
                    )}</option>`;
                  })
                  .join("")}</select>`
              : `<input type="number" step="${escapeHtml(field.step || "any")}" inputmode="decimal" name="${escapeHtml(
                  field.name
                )}" value="${escapeHtml(String(currentValue))}">`;

          return `
            <label class="field-card">
              <div class="field-top">
                <strong>${escapeHtml(localeText(field.label))}</strong>
                <em>${escapeHtml(field.unit || "-")}</em>
              </div>
              ${input}
              <div class="field-help">${escapeHtml(localeText(field.help))}</div>
            </label>
          `;
        })
        .join("");

      return `
        <section class="group-block">
          <div class="group-header">
            <h3>${escapeHtml(localeText(group.title))}</h3>
            <p>${escapeHtml(localeText(group.description))}</p>
          </div>
          <div class="field-grid">${fields}</div>
        </section>
      `;
    })
    .join("");

  $(`case-${caseKey}-groups`).innerHTML = html;
}

function renderForms() {
  renderCaseGroups("a");
  renderCaseGroups("b");
}

function buildUrlParams() {
  const params = new URLSearchParams();
  params.set("mode", state.mode);
  params.set("lang", state.lang);
  params.set("capacitance_unit", state.units.capacitance);
  params.set("field_unit", state.units.field);
  params.set("load_unit", state.units.load);
  params.set("export_case", state.exportCase);

  const appendCase = (payload, prefix = "") => {
    Object.entries(payload).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        return;
      }
      params.set(`${prefix}${key}`, String(value));
    });
  };

  if (state.mode === "compare") {
    appendCase(state.caseValues.a, "a_");
    appendCase(state.caseValues.b, "b_");
  } else {
    appendCase(state.caseValues.a);
  }
  return params;
}

function updateUrlFromState() {
  const params = buildUrlParams();
  const newUrl = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState(null, "", newUrl);
}

async function copyShareLink() {
  syncCaseStateFromDom();
  updateUrlFromState();
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(window.location.href);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = window.location.href;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    setStatus(t("statusCopied"));
  } catch (error) {
    showDiagnostic("render", t("copyFailed"));
  }
}

function toggleMode(mode) {
  state.mode = mode;
  if (mode === "compare" && (!state.caseValues.b || Object.keys(state.caseValues.b).length === 0)) {
    state.caseValues.b = deepClone(state.caseValues.a);
  }
  renderStaticText();
  renderForms();
  state.result = null;
  $("summary-grid").innerHTML = "";
  $("comparison-grid").innerHTML = "";
  $("key-values").innerHTML = "";
  $("explanation-grid").innerHTML = "";
  $("detail-sections").innerHTML = "";
  $("comparison-panel").classList.add("hidden");
  calculateAndRender();
}

function summaryCard(title, value, note, accent = "") {
  return `
    <article class="metric-card ${accent}">
      <span>${escapeHtml(title)}</span>
      <strong>${escapeHtml(value)}</strong>
      <p>${escapeHtml(note)}</p>
    </article>
  `;
}

function renderSummaryGrid(cardsHtml) {
  $("summary-grid").innerHTML = cardsHtml.join("");
}

function renderKeyValues(rows) {
  $("key-values").innerHTML = rows
    .map(
      ([label, value]) => `
        <div>
          <dt>${escapeHtml(label)}</dt>
          <dd>${escapeHtml(value)}</dd>
        </div>
      `
    )
    .join("");
}

function renderExplanationCards(cards) {
  $("explanation-grid").innerHTML = cards
    .map(
      (card) => `
        <article class="explanation-card">
          <h3>${escapeHtml(card.title)}</h3>
          <p>${escapeHtml(card.body)}</p>
        </article>
      `
    )
    .join("");
}

function singleSummaryCards(result) {
  const summary = result.summary;
  return [
    summaryCard(
      t("effectiveCapacitance"),
      formatCapacitanceValue(summary.effective_capacitance_pf),
      `${t("parasiticTotal")}: ${formatCapacitanceValue(summary.parasitic_total_pf)}`,
      "accent"
    ),
    summaryCard(
      t("intrinsicCapacitance"),
      formatCapacitanceValue(summary.intrinsic_capacitance_pf),
      `${t("dominantSegment")}: ${segmentLabel(summary.dominant_voltage_segment_code)}`
    ),
    summaryCard(
      t("spotImpedance"),
      formatOhm(summary.single_frequency_response.impedance_magnitude_ohm),
      `${formatNumber(summary.single_frequency_hz, 0)} Hz`
    ),
    summaryCard(
      t("loadedBalls"),
      `${summary.loaded_ball_count}`,
      `${formatLoadValue(summary.mean_ball_load_n)} / ${formatLoadValue(summary.max_ball_load_n)}`
    ),
    summaryCard(
      t("maxOilField"),
      formatFieldValue(summary.max_oil_film_field_mv_m),
      `${segmentLabel(summary.risk_segment_code)}`
    ),
    summaryCard(
      t("riskLevel"),
      riskLabel(summary.risk_level),
      reasonLabel(summary.risk_trigger_reason_code),
      summary.risk_level === "high" || summary.risk_level === "critical" ? "warning" : ""
    ),
    summaryCard(
      t("dominantSegment"),
      segmentLabel(summary.dominant_voltage_segment_code),
      `${formatPercent(summary.mean_ceramic_voltage_ratio)} ceramic`
    ),
    summaryCard(
      t("parasiticTotal"),
      formatCapacitanceValue(summary.parasitic_total_pf),
      summary.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")
    )
  ];
}

function compareSummaryCards(result) {
  const summaryA = result.case_a.summary;
  const summaryB = result.case_b.summary;
  return [
    summaryCard(t("caseAEffective"), formatCapacitanceValue(summaryA.effective_capacitance_pf), t("caseATitle"), "accent"),
    summaryCard(t("caseBEffective"), formatCapacitanceValue(summaryB.effective_capacitance_pf), t("caseBTitle"), "accent"),
    summaryCard(t("caseARisk"), riskLabel(summaryA.risk_level), reasonLabel(summaryA.risk_trigger_reason_code)),
    summaryCard(t("caseBRisk"), riskLabel(summaryB.risk_level), reasonLabel(summaryB.risk_trigger_reason_code)),
    summaryCard(t("caseAField"), formatFieldValue(summaryA.max_oil_film_field_mv_m), segmentLabel(summaryA.risk_segment_code)),
    summaryCard(t("caseBField"), formatFieldValue(summaryB.max_oil_film_field_mv_m), segmentLabel(summaryB.risk_segment_code)),
    summaryCard(t("caseADominant"), segmentLabel(summaryA.dominant_voltage_segment_code), formatPercent(summaryA.mean_ceramic_voltage_ratio)),
    summaryCard(t("caseBDominant"), segmentLabel(summaryB.dominant_voltage_segment_code), formatPercent(summaryB.mean_ceramic_voltage_ratio))
  ];
}

function renderComparisonGrid(result) {
  const comparison = result.comparison;
  $("comparison-grid").innerHTML = [
    summaryCard(
      t("comparisonCapDelta"),
      formatCapacitanceValue(comparison.effective_capacitance_delta_pf),
      "Case B - Case A"
    ),
    summaryCard(
      t("comparisonFieldDelta"),
      formatFieldValue(comparison.max_oil_film_field_delta_mv_m),
      "Case B - Case A"
    ),
    summaryCard(
      t("comparisonRiskDelta"),
      formatNumber(comparison.risk_level_delta, 0),
      "Case B - Case A"
    ),
    summaryCard(
      t("comparisonSegmentShift"),
      `${comparison.dominant_segment_changed ? "Dominant" : "Stable"} / ${comparison.risk_segment_changed ? "Risk" : "Stable"}`,
      comparison.dominant_segment_changed || comparison.risk_segment_changed ? "Changed" : "Unchanged"
    )
  ].join("");
}

function singleKeyRows(result) {
  const summary = result.summary;
  return [
    ["|Z| / Xc", formatOhm(summary.single_frequency_response.reactance_ohm)],
    ["Inner ν", `${formatNumber(summary.inner_operating_kinematic_viscosity_cst, 2)} cSt`],
    ["Outer ν", `${formatNumber(summary.outer_operating_kinematic_viscosity_cst, 2)} cSt`],
    ["Inner μ", `${formatNumber(summary.inner_operating_dynamic_viscosity_pa_s, 5)} Pa·s`],
    ["Outer μ", `${formatNumber(summary.outer_operating_dynamic_viscosity_pa_s, 5)} Pa·s`],
    ["λ inner / outer", `${formatNumber(summary.min_inner_lambda, 2)} / ${formatNumber(summary.min_outer_lambda, 2)}`],
    ["Operating clearance", `${formatNumber(summary.operating_clearance_mm, 4)} mm`],
    ["Radial / axial displacement", `${formatNumber(summary.radial_displacement_um, 3)} / ${formatNumber(summary.axial_displacement_um, 3)} μm`],
    ["Equivalent modulus", `${formatNumber(summary.equivalent_modulus_gpa, 2)} GPa`],
    ["Parasitic mode", summary.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")],
    ["Solver", summary.solver_converged ? "Converged" : "Fallback"],
    ["Version", result.version]
  ];
}

function compareKeyRows(result) {
  const summaryA = result.case_a.summary;
  const summaryB = result.case_b.summary;
  return [
    ["Case A λ inner / outer", `${formatNumber(summaryA.min_inner_lambda, 2)} / ${formatNumber(summaryA.min_outer_lambda, 2)}`],
    ["Case B λ inner / outer", `${formatNumber(summaryB.min_inner_lambda, 2)} / ${formatNumber(summaryB.min_outer_lambda, 2)}`],
    ["Case A parasitic mode", summaryA.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")],
    ["Case B parasitic mode", summaryB.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")],
    ["Case A loaded balls", `${summaryA.loaded_ball_count}`],
    ["Case B loaded balls", `${summaryB.loaded_ball_count}`],
    ["Case A operating clearance", `${formatNumber(summaryA.operating_clearance_mm, 4)} mm`],
    ["Case B operating clearance", `${formatNumber(summaryB.operating_clearance_mm, 4)} mm`],
    ["Case A / B spot |Z|", `${formatOhm(summaryA.single_frequency_response.impedance_magnitude_ohm)} / ${formatOhm(summaryB.single_frequency_response.impedance_magnitude_ohm)}`],
    ["Version", result.version]
  ];
}

function singleExplanations(result) {
  const summary = result.summary;
  return [
    {
      title: t("explanationCeramicTitle"),
      body: `${t("explanationCeramicBody")} ${t("dominantSegment")}: ${segmentLabel(
        summary.dominant_voltage_segment_code
      )}. Mean ceramic share ${formatPercent(summary.mean_ceramic_voltage_ratio)}.`
    },
    {
      title: t("explanationRiskTitle"),
      body: `${segmentLabel(summary.risk_segment_code)} ${reasonLabel(summary.risk_trigger_reason_code)} ${t(
        "riskLevel"
      )}: ${riskLabel(summary.risk_level)}.`
    },
    {
      title: t("explanationParasiticTitle"),
      body: `${summary.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")}. Intrinsic ${formatCapacitanceValue(
        summary.intrinsic_capacitance_pf
      )}, parasitic ${formatCapacitanceValue(summary.parasitic_total_pf)}.`
    },
    {
      title: t("explanationImpedanceTitle"),
      body: `${formatNumber(summary.single_frequency_hz, 0)} Hz 下 |Z| = ${formatOhm(
        summary.single_frequency_response.impedance_magnitude_ohm
      )}，相位固定为 -90°，因为当前版本仅建模纯电容等效阻抗。`
    }
  ];
}

function compareExplanations(result) {
  const summaryA = result.case_a.summary;
  const summaryB = result.case_b.summary;
  return [
    {
      title: t("explanationCeramicTitle"),
      body: `Case A ${formatPercent(summaryA.mean_ceramic_voltage_ratio)}，Case B ${formatPercent(
        summaryB.mean_ceramic_voltage_ratio
      )}。两组工况都遵循串联电容中小电容承担大分压的规律。`
    },
    {
      title: t("explanationRiskCompareTitle"),
      body: `Case A: ${riskLabel(summaryA.risk_level)} / ${segmentLabel(summaryA.risk_segment_code)}。 Case B: ${riskLabel(
        summaryB.risk_level
      )} / ${segmentLabel(summaryB.risk_segment_code)}。`
    },
    {
      title: t("explanationParasiticCompareTitle"),
      body: `Case A ${summaryA.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t(
        "intrinsicDominant"
      )}；Case B ${summaryB.parasitic_mode === "parasitic_dominant" ? t("parasiticDominant") : t("intrinsicDominant")}。`
    },
    {
      title: t("explanationImpedanceTitle"),
      body: `Case A |Z| ${formatOhm(summaryA.single_frequency_response.impedance_magnitude_ohm)}；Case B |Z| ${formatOhm(
        summaryB.single_frequency_response.impedance_magnitude_ohm
      )}。`
    }
  ];
}

function detailTableHtml(details) {
  if (!details.length) {
    return `<p class="small-text">${escapeHtml(t("noDetail"))}</p>`;
  }
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>${escapeHtml(t("tableAngle"))}</th>
            <th>${escapeHtml(t("tableLoad"))}</th>
            <th>${escapeHtml(t("tableContactAngle"))}</th>
            <th>${escapeHtml(t("tableInnerFilm"))}</th>
            <th>${escapeHtml(t("tableOuterFilm"))}</th>
            <th>${escapeHtml(t("tableInnerCap"))}</th>
            <th>${escapeHtml(t("tableCeramicCap"))}</th>
            <th>${escapeHtml(t("tableOuterCap"))}</th>
            <th>${escapeHtml(t("tablePathCap"))}</th>
            <th>${escapeHtml(t("tableInnerVoltage"))}</th>
            <th>${escapeHtml(t("tableCeramicVoltage"))}</th>
            <th>${escapeHtml(t("tableOuterVoltage"))}</th>
            <th>${escapeHtml(t("tableInnerField"))}</th>
            <th>${escapeHtml(t("tableCeramicField"))}</th>
            <th>${escapeHtml(t("tableOuterField"))}</th>
            <th>${escapeHtml(t("tableDominant"))}</th>
          </tr>
        </thead>
        <tbody>
          ${details
            .map(
              (detail) => `
                <tr>
                  <td>${formatNumber(detail.angle_deg, 1)}°</td>
                  <td>${formatLoadValue(detail.load_n)}</td>
                  <td>${formatNumber(detail.contact_angle_deg, 3)}°</td>
                  <td>${formatNumber(detail.inner_film_thickness_um, 4)} μm</td>
                  <td>${formatNumber(detail.outer_film_thickness_um, 4)} μm</td>
                  <td>${formatCapacitanceValue(detail.inner_contact_capacitance_pf, 5)}</td>
                  <td>${formatCapacitanceValue(detail.ceramic_body_capacitance_pf, 5)}</td>
                  <td>${formatCapacitanceValue(detail.outer_contact_capacitance_pf, 5)}</td>
                  <td>${formatCapacitanceValue(detail.path_capacitance_pf, 5)}</td>
                  <td>${formatVoltage(detail.inner_voltage_v)} / ${formatPercent(detail.inner_voltage_ratio, 1)}</td>
                  <td>${formatVoltage(detail.ceramic_voltage_v)} / ${formatPercent(detail.ceramic_voltage_ratio, 1)}</td>
                  <td>${formatVoltage(detail.outer_voltage_v)} / ${formatPercent(detail.outer_voltage_ratio, 1)}</td>
                  <td>${formatFieldValue(detail.inner_field_mv_m)}</td>
                  <td>${formatFieldValue(detail.ceramic_equivalent_field_mv_m)}</td>
                  <td>${formatFieldValue(detail.outer_field_mv_m)}</td>
                  <td>${segmentLabel(detail.dominant_voltage_segment_code)}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderDetailSections(result) {
  if (state.mode === "compare") {
    $("detail-sections").innerHTML = `
      <section class="detail-subpanel">
        <h3>${escapeHtml(t("detailSectionCaseA"))}</h3>
        ${detailTableHtml(result.case_a.details)}
      </section>
      <section class="detail-subpanel">
        <h3>${escapeHtml(t("detailSectionCaseB"))}</h3>
        ${detailTableHtml(result.case_b.details)}
      </section>
    `;
  } else {
    $("detail-sections").innerHTML = `
      <section class="detail-subpanel">
        <h3>${escapeHtml(t("detailSectionSingle"))}</h3>
        ${detailTableHtml(result.details)}
      </section>
    `;
  }
}

function renderSingleResult(result) {
  renderSummaryGrid(singleSummaryCards(result));
  renderKeyValues(singleKeyRows(result));
  renderExplanationCards(singleExplanations(result));
  $("comparison-panel").classList.add("hidden");
  renderDetailSections(result);
}

function renderCompareResult(result) {
  renderSummaryGrid(compareSummaryCards(result));
  renderKeyValues(compareKeyRows(result));
  renderExplanationCards(compareExplanations(result));
  renderComparisonGrid(result);
  $("comparison-panel").classList.remove("hidden");
  renderDetailSections(result);
}

function renderResults() {
  clearError();
  if (!state.result) {
    return;
  }
  try {
    if (state.mode === "compare") {
      renderCompareResult(state.result);
    } else {
      renderSingleResult(state.result);
    }
  } catch (error) {
    throw createError("render", error.message || String(error));
  }
}

function buildClientCsv(details) {
  const rows = [state.config.csv_headers];
  details.forEach((detail) => {
    rows.push([
      formatNumber(detail.angle_deg, 1),
      formatNumber(detail.load_n, 2),
      formatNumber(detail.contact_angle_deg, 3),
      formatNumber(detail.inner_film_thickness_um, 4),
      formatNumber(detail.outer_film_thickness_um, 4),
      formatNumber(detail.inner_contact_capacitance_pf, 5),
      formatNumber(detail.ceramic_body_capacitance_pf, 5),
      formatNumber(detail.outer_contact_capacitance_pf, 5),
      formatNumber(detail.path_capacitance_pf, 5),
      formatNumber(detail.inner_voltage_ratio, 4),
      formatNumber(detail.ceramic_voltage_ratio, 4),
      formatNumber(detail.outer_voltage_ratio, 4),
      formatNumber(detail.inner_voltage_v, 5),
      formatNumber(detail.ceramic_voltage_v, 5),
      formatNumber(detail.outer_voltage_v, 5),
      formatNumber(detail.inner_field_mv_m, 4),
      formatNumber(detail.ceramic_equivalent_field_mv_m, 4),
      formatNumber(detail.outer_field_mv_m, 4),
      segmentLabel(detail.dominant_voltage_segment_code)
    ]);
  });
  return rows.map((row) => row.join(",")).join("\n");
}

function triggerDownload(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function exportCsv() {
  const active = currentSingleResult();
  if (!active) {
    return;
  }
  triggerDownload(
    state.mode === "compare" ? `hybrid_bearing_capacitance_case_${state.exportCase}.csv` : "hybrid_bearing_capacitance.csv",
    buildClientCsv(active.details),
    "text/csv;charset=utf-8"
  );
  setStatus(t("statusCsvDone"));
}

function pdfInputLines(caseKey) {
  const values = state.caseValues[caseKey];
  return [
    `${caseKey === "a" ? "Case A" : "Case B"}: ${values.bearing_code}, ${values.speed_rpm} rpm, ${values.radial_load_n} N, ${values.inner_ring_temp_c}/${values.outer_ring_temp_c} °C`,
    `Dw ${values.ball_diameter_mm} mm, PCD ${values.pitch_diameter_mm} mm, Z ${values.rolling_elements}`,
    `Fa ${values.axial_load_n} N, preload ${values.axial_preload_n} N, V ${values.applied_voltage_v} V, f ${values.single_frequency_hz} Hz`
  ];
}

function addWrappedText(doc, lines, x, y, width, lineHeight = 14) {
  let currentY = y;
  lines.forEach((line) => {
    const wrapped = doc.splitTextToSize(line, width);
    doc.text(wrapped, x, currentY);
    currentY += wrapped.length * lineHeight;
  });
  return currentY;
}

async function exportPdf() {
  try {
    if (!window.jspdf?.jsPDF) {
      throw createError("pdf", "jsPDF is not available.");
    }
    if (!state.result) {
      return;
    }

    const doc = new window.jspdf.jsPDF({ unit: "pt", format: "a4" });
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 40;
    let y = margin;

    doc.setFontSize(18);
    doc.text(t("pdfTitle"), margin, y);
    y += 26;
    doc.setFontSize(10);
    doc.text(`${new Date().toLocaleString()} | ${runtime.modelVersion || state.config.version}`, margin, y);
    y += 24;

    doc.setFontSize(13);
    doc.text(t("pdfSectionInputs"), margin, y);
    y += 16;
    doc.setFontSize(10);
    const inputLines =
      state.mode === "compare" ? [...pdfInputLines("a"), ...pdfInputLines("b")] : pdfInputLines("a");
    y = addWrappedText(doc, inputLines, margin, y, pageWidth - margin * 2);

    y += 12;
    doc.setFontSize(13);
    doc.text(t("pdfSectionSummary"), margin, y);
    y += 16;
    doc.setFontSize(10);

    const summaryLines =
      state.mode === "compare"
        ? [
            `Case A total: ${formatCapacitanceValue(state.result.case_a.summary.effective_capacitance_pf)} | risk: ${riskLabel(
              state.result.case_a.summary.risk_level
            )}`,
            `Case B total: ${formatCapacitanceValue(state.result.case_b.summary.effective_capacitance_pf)} | risk: ${riskLabel(
              state.result.case_b.summary.risk_level
            )}`,
            `Delta total: ${formatCapacitanceValue(state.result.comparison.effective_capacitance_delta_pf)} | delta field: ${formatFieldValue(
              state.result.comparison.max_oil_film_field_delta_mv_m
            )}`
          ]
        : [
            `Total: ${formatCapacitanceValue(state.result.summary.effective_capacitance_pf)} | intrinsic: ${formatCapacitanceValue(
              state.result.summary.intrinsic_capacitance_pf
            )}`,
            `Risk: ${riskLabel(state.result.summary.risk_level)} | segment: ${segmentLabel(
              state.result.summary.risk_segment_code
            )}`,
            `Spot |Z|: ${formatOhm(state.result.summary.single_frequency_response.impedance_magnitude_ohm)}`
          ];
    y = addWrappedText(doc, summaryLines, margin, y, pageWidth - margin * 2);

    if (state.mode === "compare") {
      y += 10;
      doc.setFontSize(13);
      doc.text(t("pdfSectionCompare"), margin, y);
      y += 16;
      doc.setFontSize(10);
      y = addWrappedText(
        doc,
        [
          `Dominant segment changed: ${state.result.comparison.dominant_segment_changed}`,
          `Risk segment changed: ${state.result.comparison.risk_segment_changed}`
        ],
        margin,
        y,
        pageWidth - margin * 2
      );
    }

    doc.save("hybrid-bearing-capacitance-report.pdf");
    setStatus(t("statusPdfDone"));
  } catch (error) {
    showDiagnostic(error.kind || "pdf", error.message || String(error));
  }
}

async function calculateAndRender() {
  clearError();
  syncCaseStateFromDom();
  try {
    setStatus(t("statusCalculating"));
    let result;
    if (runtime.kind === "pages") {
      result =
        state.mode === "compare"
          ? await pagesCalculateCompare(currentCasePayload("a"), currentCasePayload("b"))
          : await pagesCalculateSingle(currentCasePayload("a"));
    } else {
      result =
        state.mode === "compare"
          ? await apiCalculate({
              mode: "compare",
              case_a_payload: currentCasePayload("a"),
              case_b_payload: currentCasePayload("b")
            })
          : await apiCalculate({ mode: "single", payload: currentCasePayload("a") });
    }
    state.result = result;
    renderResults();
    updateUrlFromState();
    setStatus(t("statusComplete"));
  } catch (error) {
    showDiagnostic(error.kind || "model", error.message || String(error));
    setStatus(t("statusFailed"));
  }
}

function handleCaseFieldChange(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
    return;
  }
  const casePanel = target.closest(".case-panel");
  if (!casePanel) {
    return;
  }
  const caseKey = casePanel.dataset.case;
  state.caseValues[caseKey][target.name] = target.value;
  if (target.name === "bearing_code" && target.value !== "custom") {
    applyPreset(caseKey, target.value);
    renderForms();
  }
}

function bindEvents() {
  $("calculate-button").addEventListener("click", calculateAndRender);
  $("share-button").addEventListener("click", copyShareLink);
  $("pdf-button").addEventListener("click", exportPdf);
  $("csv-button").addEventListener("click", exportCsv);
  $("single-mode-button").addEventListener("click", () => toggleMode("single"));
  $("compare-mode-button").addEventListener("click", () => toggleMode("compare"));
  $("case-a-panel").addEventListener("change", handleCaseFieldChange);
  $("case-b-panel").addEventListener("change", handleCaseFieldChange);
  $("case-a-panel").addEventListener("input", handleCaseFieldChange);
  $("case-b-panel").addEventListener("input", handleCaseFieldChange);

  $("language-select").addEventListener("change", (event) => {
    state.lang = event.target.value;
    if (runtime.kind === "pages") {
      localStorage.setItem("bearing_capacitance_lang", state.lang);
    }
    renderStaticText();
    renderForms();
    if (state.result) {
      renderResults();
    }
  });

  $("capacitance-unit-select").addEventListener("change", (event) => {
    state.units.capacitance = event.target.value;
    if (state.result) {
      renderResults();
    }
  });

  $("field-unit-select").addEventListener("change", (event) => {
    state.units.field = event.target.value;
    if (state.result) {
      renderResults();
    }
  });

  $("load-unit-select").addEventListener("change", (event) => {
    state.units.load = event.target.value;
    if (state.result) {
      renderResults();
    }
  });

  $("export-case-select").addEventListener("change", (event) => {
    state.exportCase = event.target.value;
  });

}

async function initialize() {
  try {
    state.lang = determineInitialLanguage();
    bindEvents();
    state.config = await fetchConfig();
    initStateFromUrl();
    $("language-select").value = state.lang;
    $("capacitance-unit-select").value = state.units.capacitance;
    $("field-unit-select").value = state.units.field;
    $("load-unit-select").value = state.units.load;
    $("export-case-select").value = state.exportCase;
    renderStaticText();
    renderForms();
    setStatus(t("statusReady"));
  } catch (error) {
    showDiagnostic(error.kind || "model", error.message || String(error));
    setStatus(t("statusFailed"));
  }
}

window.addEventListener("DOMContentLoaded", initialize);
