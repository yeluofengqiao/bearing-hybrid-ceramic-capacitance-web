from __future__ import annotations

import csv
import io
from dataclasses import asdict
from typing import Any

from flask import Flask, Response, render_template, request

from hybrid_bearing_capacitance import (
    BearingGeometry,
    CapacitanceResult,
    HybridBearingCapacitanceModel,
    LubricantProperties,
    OperatingConditions,
)


INPUT_GROUPS = [
    {
        "title": "工况",
        "description": "转速、载荷和温度直接决定滚动接触区的膜厚与等效电容。",
        "fields": [
            {"name": "speed_rpm", "label": "转速 n", "unit": "rpm", "type": "float", "default": "3000"},
            {"name": "radial_load_n", "label": "径向载荷 Fr", "unit": "N", "type": "float", "default": "2000"},
            {"name": "axial_load_n", "label": "轴向载荷 Fa", "unit": "N", "type": "float", "default": "0"},
            {"name": "temperature_c", "label": "润滑剂温度", "unit": "°C", "type": "float", "default": "60"},
        ],
    },
    {
        "title": "6208 几何默认值",
        "description": "默认按 6208 深沟球轴承近似参数预填，球径与 PCD 已按你的要求设置。",
        "fields": [
            {"name": "bearing_code", "label": "轴承编号", "unit": "-", "type": "text", "default": "6208"},
            {"name": "ball_diameter_mm", "label": "球径 Dw", "unit": "mm", "type": "float", "default": "11.906"},
            {"name": "pitch_diameter_mm", "label": "节圆直径 Dm / PCD", "unit": "mm", "type": "float", "default": "60"},
            {"name": "rolling_elements", "label": "滚动体数量 Z", "unit": "个", "type": "int", "default": "9"},
            {"name": "radial_clearance_mm", "label": "径向游隙", "unit": "mm", "type": "float", "default": "0.015"},
            {"name": "inner_curvature_coeff", "label": "内圈曲率系数 fi", "unit": "-", "type": "float", "default": "0.52"},
            {"name": "outer_curvature_coeff", "label": "外圈曲率系数 fe", "unit": "-", "type": "float", "default": "0.53"},
            {"name": "composite_roughness_um", "label": "综合粗糙度", "unit": "μm", "type": "float", "default": "0.05"},
        ],
    },
    {
        "title": "材料与润滑剂",
        "description": "混合陶瓷球轴承的等效模量、介电常数和温度修正都在这里定义。",
        "fields": [
            {"name": "ring_youngs_modulus_mpa", "label": "钢圈弹性模量", "unit": "MPa", "type": "float", "default": "210000"},
            {"name": "ring_poisson_ratio", "label": "钢圈泊松比", "unit": "-", "type": "float", "default": "0.30"},
            {"name": "ceramic_youngs_modulus_mpa", "label": "陶瓷球弹性模量", "unit": "MPa", "type": "float", "default": "310000"},
            {"name": "ceramic_poisson_ratio", "label": "陶瓷球泊松比", "unit": "-", "type": "float", "default": "0.27"},
            {"name": "ceramic_relative_permittivity", "label": "陶瓷相对介电常数", "unit": "-", "type": "float", "default": "8.2"},
            {"name": "viscosity_40_cst", "label": "40°C 粘度", "unit": "cSt", "type": "float", "default": "68"},
            {"name": "viscosity_100_cst", "label": "100°C 粘度", "unit": "cSt", "type": "float", "default": "8.8"},
            {"name": "density_25c_kg_m3", "label": "25°C 密度", "unit": "kg/m³", "type": "float", "default": "850"},
            {"name": "relative_permittivity_25c", "label": "油品介电常数", "unit": "-", "type": "float", "default": "2.25"},
            {"name": "pressure_viscosity_coeff_pa_inv", "label": "压力-粘度系数", "unit": "Pa⁻¹", "type": "float", "default": "1.5e-8"},
            {"name": "background_capacitance_pf", "label": "背景电容", "unit": "pF", "type": "float", "default": "0.8"},
        ],
    },
]

CSV_HEADERS = [
    "Angle (deg)",
    "Load (N)",
    "Contact Angle (deg)",
    "Inner Film (um)",
    "Outer Film (um)",
    "Inner Contact (pF)",
    "Ceramic Body (pF)",
    "Outer Contact (pF)",
    "Series Total (pF)",
]


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        form_values = build_form_values(request.args)
        context = build_page_context(form_values)
        return render_template("index.html", input_groups=INPUT_GROUPS, **context)

    @app.get("/download.csv")
    def download_csv() -> Response:
        form_values = build_form_values(request.args)
        context = build_page_context(form_values)
        if context["error"]:
            return Response(context["error"], status=400, mimetype="text/plain")

        result: CapacitanceResult = context["result"]
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(CSV_HEADERS)
        for detail in result.details:
            writer.writerow(detail.as_row())

        return Response(
            buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=hybrid_bearing_capacitance.csv"},
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


def build_form_values(args: Any) -> dict[str, str]:
    values = {}
    for group in INPUT_GROUPS:
        for field in group["fields"]:
            values[field["name"]] = field["default"]
    for key in values:
        if key in args and str(args.get(key)).strip():
            values[key] = str(args.get(key)).strip()
    return values


def build_geometry(values: dict[str, str]) -> BearingGeometry:
    return BearingGeometry(
        bearing_code=values["bearing_code"],
        ball_diameter_mm=float(values["ball_diameter_mm"]),
        pitch_diameter_mm=float(values["pitch_diameter_mm"]),
        rolling_elements=int(values["rolling_elements"]),
        radial_clearance_mm=float(values["radial_clearance_mm"]),
        inner_curvature_coeff=float(values["inner_curvature_coeff"]),
        outer_curvature_coeff=float(values["outer_curvature_coeff"]),
        composite_roughness_um=float(values["composite_roughness_um"]),
        ring_youngs_modulus_mpa=float(values["ring_youngs_modulus_mpa"]),
        ring_poisson_ratio=float(values["ring_poisson_ratio"]),
        ceramic_youngs_modulus_mpa=float(values["ceramic_youngs_modulus_mpa"]),
        ceramic_poisson_ratio=float(values["ceramic_poisson_ratio"]),
        ceramic_relative_permittivity=float(values["ceramic_relative_permittivity"]),
    )


def build_lubricant(values: dict[str, str]) -> LubricantProperties:
    return LubricantProperties(
        viscosity_40_cst=float(values["viscosity_40_cst"]),
        viscosity_100_cst=float(values["viscosity_100_cst"]),
        density_25c_kg_m3=float(values["density_25c_kg_m3"]),
        relative_permittivity_25c=float(values["relative_permittivity_25c"]),
        pressure_viscosity_coeff_pa_inv=float(values["pressure_viscosity_coeff_pa_inv"]),
        background_capacitance_pf=float(values["background_capacitance_pf"]),
    )


def build_conditions(values: dict[str, str]) -> OperatingConditions:
    return OperatingConditions(
        speed_rpm=float(values["speed_rpm"]),
        radial_load_n=float(values["radial_load_n"]),
        axial_load_n=float(values["axial_load_n"]),
        temperature_c=float(values["temperature_c"]),
    )


def build_page_context(form_values: dict[str, str]) -> dict[str, Any]:
    try:
        geometry = build_geometry(form_values)
        lubricant = build_lubricant(form_values)
        conditions = build_conditions(form_values)
        model = HybridBearingCapacitanceModel(geometry=geometry, lubricant=lubricant)
        result = model.calculate(conditions)
        loaded_details = [detail for detail in result.details if detail.load_n > 0]

        return {
            "error": None,
            "form_values": form_values,
            "geometry": geometry,
            "lubricant": lubricant,
            "conditions": conditions,
            "result": result,
            "geometry_snapshot": asdict(geometry),
            "lubricant_snapshot": asdict(lubricant),
            "conditions_snapshot": asdict(conditions),
            "loaded_details": loaded_details,
            "summary": {
                "equivalent_modulus_gpa": geometry.equivalent_modulus_mpa / 1000.0,
                "loaded_ratio_pct": (result.loaded_ball_count / geometry.rolling_elements) * 100.0 if geometry.rolling_elements else 0.0,
                "max_series_ball_pf": max((detail.series_capacitance_pf for detail in loaded_details), default=0.0),
                "mean_series_ball_pf": (
                    sum(detail.series_capacitance_pf for detail in loaded_details) / len(loaded_details)
                    if loaded_details
                    else 0.0
                ),
            },
        }
    except ValueError as error:
        return {
            "error": str(error),
            "form_values": form_values,
            "geometry": None,
            "lubricant": None,
            "conditions": None,
            "result": None,
            "geometry_snapshot": {},
            "lubricant_snapshot": {},
            "conditions_snapshot": {},
            "loaded_details": [],
            "summary": None,
        }


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
