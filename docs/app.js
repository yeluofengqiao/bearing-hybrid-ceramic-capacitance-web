const MODEL_URL = "./hybrid_bearing_capacitance.py";
const INDEX_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.5/full/";

const BRIDGE_CODE = String.raw`
import json
from hybrid_bearing_capacitance import BearingGeometry, LubricantProperties, OperatingConditions, HybridBearingCapacitanceModel

def calculate_from_json(raw_text):
    payload = json.loads(raw_text)

    geometry = BearingGeometry(
        bearing_code=payload["bearing_code"],
        ball_diameter_mm=float(payload["ball_diameter_mm"]),
        pitch_diameter_mm=float(payload["pitch_diameter_mm"]),
        rolling_elements=int(float(payload["rolling_elements"])),
        radial_clearance_mm=float(payload["radial_clearance_mm"]),
        inner_curvature_coeff=float(payload["inner_curvature_coeff"]),
        outer_curvature_coeff=float(payload["outer_curvature_coeff"]),
        composite_roughness_um=float(payload["composite_roughness_um"]),
        ring_youngs_modulus_mpa=float(payload["ring_youngs_modulus_mpa"]),
        ring_poisson_ratio=float(payload["ring_poisson_ratio"]),
        ceramic_youngs_modulus_mpa=float(payload["ceramic_youngs_modulus_mpa"]),
        ceramic_poisson_ratio=float(payload["ceramic_poisson_ratio"]),
        ceramic_relative_permittivity=float(payload["ceramic_relative_permittivity"]),
    )

    lubricant = LubricantProperties(
        viscosity_40_cst=float(payload["viscosity_40_cst"]),
        viscosity_100_cst=float(payload["viscosity_100_cst"]),
        density_25c_kg_m3=float(payload["density_25c_kg_m3"]),
        relative_permittivity_25c=float(payload["relative_permittivity_25c"]),
        pressure_viscosity_coeff_pa_inv=float(payload["pressure_viscosity_coeff_pa_inv"]),
        background_capacitance_pf=float(payload["background_capacitance_pf"]),
    )

    conditions = OperatingConditions(
        speed_rpm=float(payload["speed_rpm"]),
        radial_load_n=float(payload["radial_load_n"]),
        axial_load_n=float(payload["axial_load_n"]),
        temperature_c=float(payload["temperature_c"]),
        applied_voltage_v=float(payload["applied_voltage_v"]),
    )

    result = HybridBearingCapacitanceModel(geometry=geometry, lubricant=lubricant).calculate(conditions)
    loaded_details = [detail for detail in result.details if detail.load_n > 0]
    summary = {
        "intrinsic_capacitance_pf": result.intrinsic_capacitance_pf,
        "effective_capacitance_pf": result.effective_capacitance_pf,
        "background_capacitance_pf": result.background_capacitance_pf,
        "applied_voltage_v": result.applied_voltage_v,
        "min_inner_film_thickness_um": result.min_inner_film_thickness_um,
        "min_outer_film_thickness_um": result.min_outer_film_thickness_um,
        "loaded_ball_count": result.loaded_ball_count,
        "rolling_elements": geometry.rolling_elements,
        "loaded_ratio_pct": (result.loaded_ball_count / geometry.rolling_elements) * 100.0 if geometry.rolling_elements else 0.0,
        "operating_kinematic_viscosity_cst": result.operating_kinematic_viscosity_cst,
        "operating_dynamic_viscosity_pa_s": result.operating_dynamic_viscosity_pa_s,
        "equivalent_modulus_gpa": geometry.equivalent_modulus_mpa / 1000.0,
        "inner_contact_sum_pf": result.inner_contact_sum_pf,
        "ceramic_body_sum_pf": result.ceramic_body_sum_pf,
        "outer_contact_sum_pf": result.outer_contact_sum_pf,
        "mean_series_ball_pf": (
            sum(detail.series_capacitance_pf for detail in loaded_details) / len(loaded_details)
            if loaded_details else 0.0
        ),
        "max_series_ball_pf": max((detail.series_capacitance_pf for detail in loaded_details), default=0.0),
        "mean_inner_voltage_ratio": result.mean_inner_voltage_ratio,
        "mean_ceramic_voltage_ratio": result.mean_ceramic_voltage_ratio,
        "mean_outer_voltage_ratio": result.mean_outer_voltage_ratio,
        "max_inner_field_mv_m": result.max_inner_field_mv_m,
        "max_ceramic_equivalent_field_mv_m": result.max_ceramic_equivalent_field_mv_m,
        "max_outer_field_mv_m": result.max_outer_field_mv_m,
        "dominant_voltage_segment": result.dominant_voltage_segment,
        "solver_converged": result.solver_converged,
    }

    details = [
        {
            "angle_deg": detail.angle_deg,
            "load_n": detail.load_n,
            "contact_angle_deg": detail.contact_angle_deg,
            "inner_film_thickness_um": detail.inner_film_thickness_um,
            "outer_film_thickness_um": detail.outer_film_thickness_um,
            "inner_contact_capacitance_pf": detail.inner_contact_capacitance_pf,
            "ceramic_body_capacitance_pf": detail.ceramic_body_capacitance_pf,
            "outer_contact_capacitance_pf": detail.outer_contact_capacitance_pf,
            "series_capacitance_pf": detail.series_capacitance_pf,
            "inner_voltage_ratio": detail.inner_voltage_ratio,
            "ceramic_voltage_ratio": detail.ceramic_voltage_ratio,
            "outer_voltage_ratio": detail.outer_voltage_ratio,
            "inner_voltage_v": detail.inner_voltage_v,
            "ceramic_voltage_v": detail.ceramic_voltage_v,
            "outer_voltage_v": detail.outer_voltage_v,
            "inner_field_mv_m": detail.inner_field_mv_m,
            "ceramic_equivalent_field_mv_m": detail.ceramic_equivalent_field_mv_m,
            "outer_field_mv_m": detail.outer_field_mv_m,
            "dominant_voltage_segment": detail.dominant_voltage_segment,
        }
        for detail in loaded_details
    ]
    return json.dumps({"summary": summary, "details": details}, ensure_ascii=False)
`;

let pyodideRuntime = null;

function setStatus(message) {
  document.getElementById("status-pill").textContent = message;
}

function setError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.classList.remove("hidden");
  document.getElementById("result-block").classList.add("hidden");
}

function clearError() {
  const box = document.getElementById("error-box");
  box.textContent = "";
  box.classList.add("hidden");
}

function format(value, digits = 4, suffix = "") {
  return `${Number(value).toFixed(digits)}${suffix}`;
}

function collectPayload() {
  const payload = {};
  for (const element of document.querySelectorAll("#calc-form input")) {
    payload[element.name] = element.value.trim();
  }
  return payload;
}

async function ensureRuntime() {
  if (pyodideRuntime) {
    return pyodideRuntime;
  }

  setStatus("加载 Python 运行时...");
  pyodideRuntime = await loadPyodide({ indexURL: INDEX_URL });
  setStatus("加载 numpy / scipy...");
  await pyodideRuntime.loadPackage(["numpy", "scipy"]);
  setStatus("加载轴承模型...");
  const modelSource = await fetch(MODEL_URL).then((response) => {
    if (!response.ok) {
      throw new Error("无法读取网页内置的 Python 模型文件。");
    }
    return response.text();
  });
  pyodideRuntime.FS.writeFile("hybrid_bearing_capacitance.py", modelSource);
  await pyodideRuntime.runPythonAsync(`
import importlib
import hybrid_bearing_capacitance
importlib.reload(hybrid_bearing_capacitance)
`);
  pyodideRuntime.runPython(BRIDGE_CODE);
  setStatus("模型已就绪");
  return pyodideRuntime;
}

function renderContributionList(summary) {
  const items = [
    ["内圈油膜原始和", `${format(summary.inner_contact_sum_pf)} pF`],
    ["陶瓷球本体原始和", `${format(summary.ceramic_body_sum_pf)} pF`],
    ["外圈油膜原始和", `${format(summary.outer_contact_sum_pf)} pF`],
    ["平均单球串联电容", `${format(summary.mean_series_ball_pf, 5)} pF`],
    ["最大单球串联电容", `${format(summary.max_series_ball_pf, 5)} pF`],
    ["平均内圈油膜分压", `${format(summary.mean_inner_voltage_ratio * 100, 2)}%`],
    ["平均陶瓷球分压", `${format(summary.mean_ceramic_voltage_ratio * 100, 2)}%`],
    ["平均外圈油膜分压", `${format(summary.mean_outer_voltage_ratio * 100, 2)}%`],
    ["内圈油膜最大场强", `${format(summary.max_inner_field_mv_m, 3)} MV/m`],
    ["陶瓷球等效最大场强", `${format(summary.max_ceramic_equivalent_field_mv_m, 3)} MV/m`],
    ["外圈油膜最大场强", `${format(summary.max_outer_field_mv_m, 3)} MV/m`],
    ["求解器状态", summary.solver_converged ? "收敛" : "未完全收敛，结果仅供参考"],
  ];
  const host = document.getElementById("contribution-list");
  host.innerHTML = items
    .map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`)
    .join("");
}

function renderDetails(details) {
  const body = document.getElementById("detail-body");
  body.innerHTML = details
    .map((detail) => `
      <tr>
        <td>${format(detail.angle_deg, 1)}°</td>
        <td>${format(detail.load_n, 2)} N</td>
        <td>${format(detail.contact_angle_deg, 3)}°</td>
        <td>${format(detail.inner_film_thickness_um, 4)} μm</td>
        <td>${format(detail.outer_film_thickness_um, 4)} μm</td>
        <td>${format(detail.inner_contact_capacitance_pf, 5)} pF</td>
        <td>${format(detail.ceramic_body_capacitance_pf, 5)} pF</td>
        <td>${format(detail.outer_contact_capacitance_pf, 5)} pF</td>
        <td><strong>${format(detail.series_capacitance_pf, 5)} pF</strong></td>
        <td>${format(detail.inner_voltage_v, 4)} V / ${format(detail.inner_voltage_ratio * 100, 1)}%</td>
        <td>${format(detail.ceramic_voltage_v, 4)} V / ${format(detail.ceramic_voltage_ratio * 100, 1)}%</td>
        <td>${format(detail.outer_voltage_v, 4)} V / ${format(detail.outer_voltage_ratio * 100, 1)}%</td>
        <td>${format(detail.inner_field_mv_m, 3)} MV/m</td>
        <td>${format(detail.ceramic_equivalent_field_mv_m, 3)} MV/m</td>
        <td>${format(detail.outer_field_mv_m, 3)} MV/m</td>
        <td><strong>${detail.dominant_voltage_segment}</strong></td>
      </tr>
    `)
    .join("");
}

function renderResults(data) {
  const { summary, details } = data;
  document.getElementById("intrinsic-capacitance").textContent = `${format(summary.intrinsic_capacitance_pf)} pF`;
  document.getElementById("effective-capacitance").textContent = `${format(summary.effective_capacitance_pf)} pF`;
  document.getElementById("background-note").textContent = `总电容 = 本体电容 + 背景电容 ${format(summary.background_capacitance_pf, 3)} pF`;
  document.getElementById("applied-voltage").textContent = `${format(summary.applied_voltage_v, 3)} V`;
  document.getElementById("min-film-thickness").textContent = `${format(summary.min_inner_film_thickness_um)} / ${format(summary.min_outer_film_thickness_um)} μm`;
  document.getElementById("loaded-ball-count").textContent = `${summary.loaded_ball_count} / ${summary.rolling_elements}`;
  document.getElementById("loaded-ratio").textContent = `加载区占比 ${format(summary.loaded_ratio_pct, 1)}%`;
  document.getElementById("operating-viscosity").textContent = `${format(summary.operating_kinematic_viscosity_cst, 2)} cSt`;
  document.getElementById("dynamic-viscosity").textContent = `动力粘度 ${format(summary.operating_dynamic_viscosity_pa_s, 5)} Pa·s`;
  document.getElementById("equivalent-modulus").textContent = `${format(summary.equivalent_modulus_gpa, 2)} GPa`;
  document.getElementById("dominant-segment").textContent = summary.dominant_voltage_segment;
  renderContributionList(summary);
  renderDetails(details);
  document.getElementById("result-block").classList.remove("hidden");
}

async function runCalculation(event) {
  event?.preventDefault();
  clearError();

  try {
    const runtime = await ensureRuntime();
    setStatus("计算中...");
    const payload = collectPayload();
    runtime.globals.set("payload_json", JSON.stringify(payload));
    const resultText = await runtime.runPythonAsync("calculate_from_json(payload_json)");
    runtime.globals.delete("payload_json");
    const data = JSON.parse(resultText);
    renderResults(data);
    setStatus("计算完成");
  } catch (error) {
    setError(error.message || String(error));
    setStatus("计算失败");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("calc-form").addEventListener("submit", runCalculation);
  runCalculation();
});
