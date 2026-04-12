from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


class HybridBearingCapacitanceWebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        self.query = {
            "bearing_code": "6208",
            "speed_rpm": "3000",
            "radial_load_n": "2000",
            "axial_load_n": "0",
            "temperature_c": "60",
            "ball_diameter_mm": "11.906",
            "pitch_diameter_mm": "60",
            "rolling_elements": "9",
            "radial_clearance_mm": "0.015",
            "inner_curvature_coeff": "0.52",
            "outer_curvature_coeff": "0.53",
            "composite_roughness_um": "0.05",
            "ring_youngs_modulus_mpa": "210000",
            "ring_poisson_ratio": "0.30",
            "ceramic_youngs_modulus_mpa": "310000",
            "ceramic_poisson_ratio": "0.27",
            "ceramic_relative_permittivity": "8.2",
            "viscosity_40_cst": "68",
            "viscosity_100_cst": "8.8",
            "density_25c_kg_m3": "850",
            "relative_permittivity_25c": "2.25",
            "pressure_viscosity_coeff_pa_inv": "1.5e-8",
            "background_capacitance_pf": "0.8",
        }

    def test_index_renders_results(self) -> None:
        response = self.client.get("/", query_string=self.query)

        self.assertEqual(response.status_code, 200)
        self.assertIn("混合陶瓷球轴承电容计算器".encode("utf-8"), response.data)
        self.assertIn("轴承本体电容".encode("utf-8"), response.data)
        self.assertIn("单球明细".encode("utf-8"), response.data)

    def test_download_route_returns_csv(self) -> None:
        response = self.client.get("/download.csv", query_string=self.query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn("attachment; filename=hybrid_bearing_capacitance.csv", response.headers["Content-Disposition"])
        self.assertIn(b"Angle (deg),Load (N)", response.data)

    def test_invalid_speed_returns_error_message(self) -> None:
        bad_query = dict(self.query)
        bad_query["speed_rpm"] = "0"

        response = self.client.get("/", query_string=bad_query)

        self.assertEqual(response.status_code, 200)
        self.assertIn("输入有误".encode("utf-8"), response.data)
        self.assertIn("speed_rpm must be greater than 0.".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
