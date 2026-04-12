from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


class HybridBearingCapacitanceWebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        self.single_payload = {"bearing_code": "6208"}
        self.compare_payload = {
            "mode": "compare",
            "case_a_payload": {"bearing_code": "6208", "radial_load_n": 2000.0},
            "case_b_payload": {"bearing_code": "6209", "radial_load_n": 3200.0},
        }

    def test_index_renders_shared_frontend_shell(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("混合陶瓷球轴承电容分析平台".encode("utf-8"), response.data)
        self.assertIn(b'id="compare-mode-button"', response.data)
        self.assertNotIn(b'id="voltage-chart"', response.data)
        self.assertIn(b'id="comparison-panel"', response.data)
        self.assertIn(b"/assets/app.js", response.data)

    def test_config_endpoint_exposes_presets_and_groups(self) -> None:
        response = self.client.get("/api/config")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("defaults", data)
        self.assertIn("groups", data)
        self.assertIn("6208", data["presets"])
        self.assertEqual(len(data["groups"]), 4)

    def test_single_case_api_returns_new_result_structure(self) -> None:
        response = self.client.post("/api/calculate", json={"mode": "single", "payload": self.single_payload})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("summary", data)
        self.assertIn("details", data)
        self.assertNotIn("frequency_sweep", data)
        self.assertNotIn("condition_sweeps", data)
        self.assertNotIn("sensitivity", data)
        self.assertGreater(data["summary"]["effective_capacitance_pf"], 0.0)

    def test_compare_api_returns_case_delta_block(self) -> None:
        response = self.client.post("/api/calculate", json=self.compare_payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("case_a", data)
        self.assertIn("case_b", data)
        self.assertIn("comparison", data)
        self.assertNotEqual(data["comparison"]["effective_capacitance_delta_pf"], 0.0)

    def test_download_route_returns_csv(self) -> None:
        response = self.client.get("/download.csv", query_string=self.single_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn("attachment; filename=hybrid_bearing_capacitance.csv", response.headers["Content-Disposition"])
        self.assertIn(b"Angle (deg),Load (N)", response.data)

    def test_invalid_speed_returns_validation_json(self) -> None:
        response = self.client.post("/api/calculate", json={"mode": "single", "payload": {"bearing_code": "6208", "speed_rpm": 0}})

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error_type"], "validation")
        self.assertIn("speed_rpm must be greater than 0", data["error"])


if __name__ == "__main__":
    unittest.main()
