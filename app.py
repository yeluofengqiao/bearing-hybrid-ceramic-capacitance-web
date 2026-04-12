from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Mapping

from flask import Flask, Response, jsonify, render_template, request, send_from_directory

from hybrid_bearing_capacitance import MODEL_VERSION, analyze_case_payload, compare_case_payloads


ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"
UI_CONFIG_PATH = DOCS_DIR / "ui-config.json"
MODEL_NOTE = "Pure capacitive impedance model without leakage resistance or conductive oil-film branches."
UI_RESERVED_KEYS = {
    "mode",
    "lang",
    "capacitance_unit",
    "field_unit",
    "load_unit",
    "export_case",
    "case",
}
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
    "Inner Voltage Ratio",
    "Ceramic Voltage Ratio",
    "Outer Voltage Ratio",
    "Inner Voltage (V)",
    "Ceramic Voltage (V)",
    "Outer Voltage (V)",
    "Inner Field (MV/m)",
    "Ceramic Eq Field (MV/m)",
    "Outer Field (MV/m)",
    "Dominant Segment",
]


def load_ui_config() -> dict[str, Any]:
    return json.loads(UI_CONFIG_PATH.read_text(encoding="utf-8"))


def extract_case_payload(query: Mapping[str, Any], *, prefix: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in query.items():
        if prefix:
            if not key.startswith(prefix):
                continue
            clean_key = key[len(prefix) :]
        else:
            if key.startswith("a_") or key.startswith("b_") or key in UI_RESERVED_KEYS:
                continue
            clean_key = key
        if clean_key:
            payload[clean_key] = value
    return payload


def details_to_csv(details: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADERS)
    for detail in details:
        writer.writerow(
            [
                f"{detail['angle_deg']:.1f}",
                f"{detail['load_n']:.2f}",
                f"{detail['contact_angle_deg']:.3f}",
                f"{detail['inner_film_thickness_um']:.4f}",
                f"{detail['outer_film_thickness_um']:.4f}",
                f"{detail['inner_contact_capacitance_pf']:.5f}",
                f"{detail['ceramic_body_capacitance_pf']:.5f}",
                f"{detail['outer_contact_capacitance_pf']:.5f}",
                f"{detail['path_capacitance_pf']:.5f}",
                f"{detail['inner_voltage_ratio']:.4f}",
                f"{detail['ceramic_voltage_ratio']:.4f}",
                f"{detail['outer_voltage_ratio']:.4f}",
                f"{detail['inner_voltage_v']:.5f}",
                f"{detail['ceramic_voltage_v']:.5f}",
                f"{detail['outer_voltage_v']:.5f}",
                f"{detail['inner_field_mv_m']:.4f}",
                f"{detail['ceramic_equivalent_field_mv_m']:.4f}",
                f"{detail['outer_field_mv_m']:.4f}",
                detail["dominant_voltage_segment_label"],
            ]
        )
    return buffer.getvalue()


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        runtime = {
            "kind": "flask",
            "assetBase": "/assets",
            "configUrl": "/api/config",
            "calculateUrl": "/api/calculate",
            "csvUrl": "/download.csv",
            "modelVersion": MODEL_VERSION,
            "modelNote": MODEL_NOTE,
            "initialLang": request.args.get("lang", "zh-CN"),
        }
        return render_template("index.html", runtime=runtime)

    @app.get("/assets/<path:filename>")
    def docs_assets(filename: str):
        return send_from_directory(DOCS_DIR, filename)

    @app.get("/api/config")
    def api_config() -> Response:
        return jsonify(load_ui_config())

    @app.post("/api/calculate")
    def api_calculate() -> tuple[Response, int] | Response:
        try:
            data = request.get_json(silent=True) or {}
            mode = str(data.get("mode", "single"))
            if mode == "compare":
                case_a_payload = data.get("case_a_payload") or {}
                case_b_payload = data.get("case_b_payload") or {}
                result = compare_case_payloads(case_a_payload, case_b_payload, include_extended=False)
            else:
                payload = data.get("payload") or data
                result = analyze_case_payload(payload, include_extended=False)
            return jsonify(result)
        except ValueError as error:
            return jsonify({"error": str(error), "error_type": "validation"}), 400
        except Exception as error:  # pragma: no cover - defensive fallback
            return jsonify({"error": str(error), "error_type": "server"}), 500

    @app.get("/download.csv")
    def download_csv() -> Response:
        try:
            mode = request.args.get("mode", "single")
            requested_case = request.args.get("case", "single")
            if mode == "compare":
                prefix = "b_" if requested_case == "b" else "a_"
                payload = extract_case_payload(request.args, prefix=prefix)
                filename = f"hybrid_bearing_capacitance_case_{requested_case}.csv"
            else:
                payload = extract_case_payload(request.args)
                filename = "hybrid_bearing_capacitance.csv"

            result = analyze_case_payload(payload, include_extended=False)
            csv_text = details_to_csv(result["details"])
            return Response(
                csv_text,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        except ValueError as error:
            return Response(str(error), status=400, mimetype="text/plain")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": MODEL_VERSION}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
