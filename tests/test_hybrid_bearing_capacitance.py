from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hybrid_bearing_capacitance import analyze_case_payload, compare_case_payloads


class HybridBearingCapacitanceModelTests(unittest.TestCase):
    def test_default_case_returns_positive_capacitance_and_sweeps(self) -> None:
        result = analyze_case_payload({"bearing_code": "6208"})

        self.assertEqual(result["version"], "2.0.0")
        self.assertGreater(result["summary"]["intrinsic_capacitance_pf"], 0.0)
        self.assertGreater(result["summary"]["effective_capacitance_pf"], result["summary"]["intrinsic_capacitance_pf"])
        self.assertGreater(result["summary"]["loaded_ball_count"], 0)
        self.assertTrue(result["summary"]["solver_converged"])
        self.assertEqual(len(result["frequency_sweep"]["frequency_hz"]), 121)
        self.assertEqual(len(result["condition_sweeps"]["speed"]["x"]), 41)
        self.assertEqual(len(result["condition_sweeps"]["temperature"]["x"]), 41)
        self.assertEqual(len(result["condition_sweeps"]["radial_load"]["x"]), 41)
        self.assertIn("effective_capacitance_pf", result["sensitivity"])

    def test_explicit_parasitics_increase_total_capacitance(self) -> None:
        baseline = analyze_case_payload(
            {
                "bearing_code": "6208",
                "background_capacitance_pf": 0.0,
                "cage_capacitance_pf": 0.0,
                "seal_capacitance_pf": 0.0,
                "mounting_capacitance_pf": 0.0,
            }
        )
        with_parasitics = analyze_case_payload(
            {
                "bearing_code": "6208",
                "background_capacitance_pf": 0.8,
                "cage_capacitance_pf": 0.15,
                "seal_capacitance_pf": 0.05,
                "mounting_capacitance_pf": 0.10,
            }
        )

        self.assertEqual(baseline["summary"]["parasitic_total_pf"], 0.0)
        self.assertAlmostEqual(
            with_parasitics["summary"]["effective_capacitance_pf"],
            with_parasitics["summary"]["intrinsic_capacitance_pf"] + with_parasitics["summary"]["parasitic_total_pf"],
            places=9,
        )
        self.assertGreater(
            with_parasitics["summary"]["effective_capacitance_pf"],
            baseline["summary"]["effective_capacitance_pf"],
        )

    def test_single_frequency_matches_frequency_sweep_at_10khz(self) -> None:
        result = analyze_case_payload({"bearing_code": "6208"})
        frequencies = result["frequency_sweep"]["frequency_hz"]
        index = frequencies.index(10000.0)

        self.assertAlmostEqual(
            result["summary"]["single_frequency_response"]["impedance_magnitude_ohm"],
            result["frequency_sweep"]["impedance_magnitude_ohm"][index],
            places=9,
        )

    def test_dual_temperatures_shift_inner_and_outer_viscosity_independently(self) -> None:
        result = analyze_case_payload(
            {
                "bearing_code": "6208",
                "inner_ring_temp_c": 90.0,
                "outer_ring_temp_c": 40.0,
            }
        )

        self.assertLess(
            result["summary"]["inner_operating_kinematic_viscosity_cst"],
            result["summary"]["outer_operating_kinematic_viscosity_cst"],
        )

    def test_preload_and_clearance_loss_change_loaded_path_and_clearance(self) -> None:
        baseline = analyze_case_payload({"bearing_code": "6208"})
        preloaded = analyze_case_payload({"bearing_code": "6208", "axial_preload_n": 1000.0})
        lost_clearance = analyze_case_payload(
            {
                "bearing_code": "6208",
                "fit_clearance_loss_um": 5.0,
                "thermal_clearance_loss_um": 10.0,
            }
        )

        self.assertGreater(preloaded["summary"]["loaded_ball_count"], baseline["summary"]["loaded_ball_count"])
        self.assertGreater(preloaded["summary"]["effective_capacitance_pf"], baseline["summary"]["effective_capacitance_pf"])
        self.assertLess(lost_clearance["summary"]["operating_clearance_mm"], baseline["summary"]["operating_clearance_mm"])

    def test_roughness_thresholds_raise_risk_level(self) -> None:
        smooth = analyze_case_payload({"bearing_code": "6208", "composite_roughness_um": 0.05})
        medium = analyze_case_payload({"bearing_code": "6208", "composite_roughness_um": 0.2})
        severe = analyze_case_payload({"bearing_code": "6208", "composite_roughness_um": 0.5})

        self.assertEqual(smooth["summary"]["risk_level"], "low")
        self.assertEqual(medium["summary"]["risk_level"], "medium")
        self.assertEqual(severe["summary"]["risk_level"], "critical")

    def test_compare_payloads_return_deltas(self) -> None:
        result = compare_case_payloads(
            {"bearing_code": "6208", "radial_load_n": 2000.0},
            {"bearing_code": "6209", "radial_load_n": 3200.0},
        )

        self.assertIn("case_a", result)
        self.assertIn("case_b", result)
        self.assertIn("comparison", result)
        self.assertNotEqual(
            result["case_a"]["summary"]["effective_capacitance_pf"],
            result["case_b"]["summary"]["effective_capacitance_pf"],
        )
        self.assertNotEqual(result["comparison"]["effective_capacitance_delta_pf"], 0.0)


if __name__ == "__main__":
    unittest.main()
