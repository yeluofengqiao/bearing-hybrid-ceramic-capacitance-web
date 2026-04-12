from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hybrid_bearing_capacitance import HybridBearingCapacitanceModel, OperatingConditions


class HybridBearingCapacitanceModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = HybridBearingCapacitanceModel()

    def test_default_case_returns_positive_capacitance(self) -> None:
        result = self.model.calculate(OperatingConditions())

        self.assertGreater(result.intrinsic_capacitance_pf, 0.0)
        self.assertGreater(result.effective_capacitance_pf, result.intrinsic_capacitance_pf)
        self.assertGreater(result.loaded_ball_count, 0)
        self.assertTrue(result.solver_converged)

    def test_higher_radial_load_increases_intrinsic_capacitance(self) -> None:
        low = self.model.calculate(OperatingConditions(radial_load_n=1000.0))
        high = self.model.calculate(OperatingConditions(radial_load_n=4000.0))

        self.assertGreater(high.intrinsic_capacitance_pf, low.intrinsic_capacitance_pf)
        self.assertGreater(high.max_ball_load_n, low.max_ball_load_n)

    def test_higher_speed_reduces_intrinsic_capacitance(self) -> None:
        slow = self.model.calculate(OperatingConditions(speed_rpm=1000.0))
        fast = self.model.calculate(OperatingConditions(speed_rpm=8000.0))

        self.assertLess(fast.intrinsic_capacitance_pf, slow.intrinsic_capacitance_pf)
        self.assertGreater(fast.min_inner_film_thickness_um, slow.min_inner_film_thickness_um)

    def test_higher_temperature_raises_intrinsic_capacitance(self) -> None:
        cool = self.model.calculate(OperatingConditions(temperature_c=40.0))
        hot = self.model.calculate(OperatingConditions(temperature_c=100.0))

        self.assertGreater(hot.intrinsic_capacitance_pf, cool.intrinsic_capacitance_pf)
        self.assertLess(hot.operating_kinematic_viscosity_cst, cool.operating_kinematic_viscosity_cst)

    def test_ceramic_segment_takes_largest_voltage_share(self) -> None:
        result = self.model.calculate(OperatingConditions(applied_voltage_v=1.0))
        loaded = [detail for detail in result.details if detail.load_n > 0.0]

        self.assertTrue(loaded)
        for detail in loaded:
            self.assertGreater(detail.ceramic_voltage_ratio, detail.inner_voltage_ratio)
            self.assertGreater(detail.ceramic_voltage_ratio, detail.outer_voltage_ratio)
            self.assertEqual(detail.dominant_voltage_segment, "Ceramic Ball")
        self.assertEqual(result.dominant_voltage_segment, "Ceramic Ball")


if __name__ == "__main__":
    unittest.main()
