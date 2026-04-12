from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

import numpy as np
from scipy.optimize import fsolve
from scipy.special import ellipe, ellipk


EPSILON_0 = 8.8541878128e-12
REFERENCE_TEMPERATURE_C = 25.0
MODEL_VERSION = "2.0.0"

RISK_LEVEL_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SEGMENT_LABELS = {
    "inner_oil_film": "Inner Oil Film",
    "ceramic_ball": "Ceramic Ball",
    "outer_oil_film": "Outer Oil Film",
    "parasitic_total": "Parasitic Network",
    "no_loaded_path": "No Loaded Path",
}

LUBRICATION_STATE_FACTORS = {
    "clean_oil": {"viscosity": 1.00, "permittivity": 1.00, "roughness": 1.00},
    "grease": {"viscosity": 1.15, "permittivity": 1.03, "roughness": 1.10},
    "moisture_contaminated": {"viscosity": 0.90, "permittivity": 1.30, "roughness": 1.15},
    "particle_contaminated": {"viscosity": 1.00, "permittivity": 1.02, "roughness": 1.35},
    "aged_lubricant": {"viscosity": 1.20, "permittivity": 1.08, "roughness": 1.20},
}

BEARING_PRESETS = {
    "6208": {"ball_diameter_mm": 11.906, "pitch_diameter_mm": 60.0, "rolling_elements": 9},
    "6209": {"ball_diameter_mm": 12.700, "pitch_diameter_mm": 68.0, "rolling_elements": 9},
    "6210": {"ball_diameter_mm": 15.081, "pitch_diameter_mm": 76.0, "rolling_elements": 8},
    "6308": {"ball_diameter_mm": 15.081, "pitch_diameter_mm": 73.0, "rolling_elements": 8},
}

SENSITIVITY_TARGETS = (
    "ball_diameter_mm",
    "pitch_diameter_mm",
    "composite_roughness_um",
    "ceramic_relative_permittivity",
    "relative_permittivity_25c",
    "background_capacitance_pf",
    "radial_load_n",
    "inner_ring_temp_c",
)


@dataclass(frozen=True, slots=True)
class BearingGeometry:
    bearing_code: str = "6208"
    ball_diameter_mm: float = 11.906
    pitch_diameter_mm: float = 60.0
    rolling_elements: int = 9
    radial_clearance_mm: float = 0.015
    inner_curvature_coeff: float = 0.52
    outer_curvature_coeff: float = 0.53
    composite_roughness_um: float = 0.05
    ring_youngs_modulus_mpa: float = 210000.0
    ring_poisson_ratio: float = 0.30
    ceramic_youngs_modulus_mpa: float = 310000.0
    ceramic_poisson_ratio: float = 0.27
    ceramic_relative_permittivity: float = 8.2

    def validate(self) -> None:
        positive_fields = {
            "ball_diameter_mm": self.ball_diameter_mm,
            "pitch_diameter_mm": self.pitch_diameter_mm,
            "inner_curvature_coeff": self.inner_curvature_coeff,
            "outer_curvature_coeff": self.outer_curvature_coeff,
            "composite_roughness_um": self.composite_roughness_um,
            "ring_youngs_modulus_mpa": self.ring_youngs_modulus_mpa,
            "ceramic_youngs_modulus_mpa": self.ceramic_youngs_modulus_mpa,
            "ceramic_relative_permittivity": self.ceramic_relative_permittivity,
        }
        for name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than 0.")

        if self.rolling_elements < 3:
            raise ValueError("rolling_elements must be at least 3.")
        if self.radial_clearance_mm < 0:
            raise ValueError("radial_clearance_mm cannot be negative.")
        if self.pitch_diameter_mm <= self.ball_diameter_mm:
            raise ValueError("pitch_diameter_mm must be greater than ball_diameter_mm.")
        if not 0 < self.ring_poisson_ratio < 0.5:
            raise ValueError("ring_poisson_ratio must be between 0 and 0.5.")
        if not 0 < self.ceramic_poisson_ratio < 0.5:
            raise ValueError("ceramic_poisson_ratio must be between 0 and 0.5.")
        if self.inner_curvature_coeff <= 0.5 or self.outer_curvature_coeff <= 0.5:
            raise ValueError("Curvature coefficients must be greater than 0.5 for groove contacts.")

    @property
    def groove_span_mm(self) -> float:
        return self.ball_diameter_mm * (self.inner_curvature_coeff + self.outer_curvature_coeff - 1.0)

    @property
    def equivalent_modulus_mpa(self) -> float:
        denominator = (
            (1.0 - self.ring_poisson_ratio**2) / self.ring_youngs_modulus_mpa
            + (1.0 - self.ceramic_poisson_ratio**2) / self.ceramic_youngs_modulus_mpa
        )
        return 2.0 / denominator

    def operating_clearance_mm(self, fit_clearance_loss_um: float, thermal_clearance_loss_um: float) -> float:
        return self.radial_clearance_mm - (fit_clearance_loss_um + thermal_clearance_loss_um) / 1000.0


@dataclass(frozen=True, slots=True)
class LubricantProperties:
    viscosity_40_cst: float = 68.0
    viscosity_100_cst: float = 8.8
    density_25c_kg_m3: float = 850.0
    relative_permittivity_25c: float = 2.25
    pressure_viscosity_coeff_pa_inv: float = 1.5e-8
    thermal_expansion_coeff_per_c: float = 6.5e-4
    bulk_modulus_pa: float = 1.6e9
    lubrication_state: str = "clean_oil"

    def validate(self) -> None:
        positive_fields = {
            "viscosity_40_cst": self.viscosity_40_cst,
            "viscosity_100_cst": self.viscosity_100_cst,
            "density_25c_kg_m3": self.density_25c_kg_m3,
            "relative_permittivity_25c": self.relative_permittivity_25c,
            "pressure_viscosity_coeff_pa_inv": self.pressure_viscosity_coeff_pa_inv,
            "thermal_expansion_coeff_per_c": self.thermal_expansion_coeff_per_c,
            "bulk_modulus_pa": self.bulk_modulus_pa,
        }
        for name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than 0.")
        if self.lubrication_state not in LUBRICATION_STATE_FACTORS:
            raise ValueError(f"Unsupported lubrication_state: {self.lubrication_state}")

    @property
    def state_factors(self) -> dict[str, float]:
        return LUBRICATION_STATE_FACTORS[self.lubrication_state]

    def effective_viscosity_pair(self) -> tuple[float, float]:
        multiplier = self.state_factors["viscosity"]
        return self.viscosity_40_cst * multiplier, self.viscosity_100_cst * multiplier

    def effective_relative_permittivity_25c(self) -> float:
        return self.relative_permittivity_25c * self.state_factors["permittivity"]

    def density_at(self, temperature_c: float, pressure_pa: float) -> float:
        density_zero_pressure = self.density_25c_kg_m3 * (
            1.0 - self.thermal_expansion_coeff_per_c * (temperature_c - REFERENCE_TEMPERATURE_C)
        )
        density_zero_pressure = max(density_zero_pressure, self.density_25c_kg_m3 * 0.65)
        pressure_factor = 1.0 + max(pressure_pa, 0.0) / self.bulk_modulus_pa
        return density_zero_pressure * pressure_factor

    def relative_permittivity(self, temperature_c: float, pressure_pa: float) -> float:
        density_ref = self.density_25c_kg_m3
        effective_eps = self.effective_relative_permittivity_25c()
        cm_constant = ((effective_eps - 1.0) / ((effective_eps + 2.0) * density_ref))
        density = self.density_at(temperature_c, pressure_pa)
        product = max(cm_constant * density, 1e-9)
        if product >= 0.98:
            product = 0.98
        permittivity = (1.0 + 2.0 * product) / (1.0 - product)
        return min(max(permittivity, 1.5), 8.0)


@dataclass(frozen=True, slots=True)
class ParasiticCapacitances:
    background_capacitance_pf: float = 0.8
    cage_capacitance_pf: float = 0.15
    seal_capacitance_pf: float = 0.05
    mounting_capacitance_pf: float = 0.10

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

    @property
    def total_pf(self) -> float:
        return sum(asdict(self).values())


@dataclass(frozen=True, slots=True)
class OperatingConditions:
    speed_rpm: float = 3000.0
    radial_load_n: float = 2000.0
    axial_load_n: float = 0.0
    axial_preload_n: float = 0.0
    inner_ring_temp_c: float = 60.0
    outer_ring_temp_c: float = 60.0
    applied_voltage_v: float = 1.0
    single_frequency_hz: float = 10000.0
    fit_clearance_loss_um: float = 0.0
    thermal_clearance_loss_um: float = 0.0

    def validate(self) -> None:
        if self.speed_rpm <= 0:
            raise ValueError("speed_rpm must be greater than 0.")
        if self.radial_load_n < 0:
            raise ValueError("radial_load_n cannot be negative.")
        if self.axial_load_n < 0:
            raise ValueError("axial_load_n cannot be negative.")
        if self.axial_preload_n < 0:
            raise ValueError("axial_preload_n cannot be negative.")
        if self.inner_ring_temp_c <= -273.15 or self.outer_ring_temp_c <= -273.15:
            raise ValueError("Ring temperatures must be above absolute zero.")
        if self.applied_voltage_v < 0:
            raise ValueError("applied_voltage_v cannot be negative.")
        if self.single_frequency_hz <= 0:
            raise ValueError("single_frequency_hz must be greater than 0.")
        if self.fit_clearance_loss_um < 0 or self.thermal_clearance_loss_um < 0:
            raise ValueError("Clearance losses cannot be negative.")


@dataclass(frozen=True, slots=True)
class SweepSettings:
    frequency_start_hz: float = 1000.0
    frequency_end_hz: float = 1.0e7
    frequency_point_count: int = 121
    speed_start_rpm: float = 500.0
    speed_end_rpm: float = 12000.0
    temperature_start_c: float = 20.0
    temperature_end_c: float = 120.0
    radial_load_start_n: float = 500.0
    radial_load_end_n: float = 5000.0
    condition_point_count: int = 41

    def validate(self) -> None:
        if self.frequency_start_hz <= 0 or self.frequency_end_hz <= self.frequency_start_hz:
            raise ValueError("Frequency sweep range is invalid.")
        if self.speed_start_rpm <= 0 or self.speed_end_rpm <= self.speed_start_rpm:
            raise ValueError("Speed sweep range is invalid.")
        if self.temperature_end_c <= self.temperature_start_c:
            raise ValueError("Temperature sweep range is invalid.")
        if self.radial_load_start_n < 0 or self.radial_load_end_n <= self.radial_load_start_n:
            raise ValueError("Radial load sweep range is invalid.")
        if self.frequency_point_count < 5 or self.condition_point_count < 5:
            raise ValueError("Sweep point counts are too small.")


@dataclass(frozen=True, slots=True)
class BallPathDetail:
    angle_deg: float
    load_n: float
    contact_angle_deg: float
    inner_hertz_area_mm2: float
    outer_hertz_area_mm2: float
    inner_film_thickness_um: float
    outer_film_thickness_um: float
    inner_effective_gap_um: float
    outer_effective_gap_um: float
    inner_contact_capacitance_pf: float
    ceramic_body_capacitance_pf: float
    outer_contact_capacitance_pf: float
    path_capacitance_pf: float
    inner_mean_pressure_mpa: float
    outer_mean_pressure_mpa: float
    inner_relative_permittivity: float
    outer_relative_permittivity: float
    inner_lambda: float
    outer_lambda: float
    inner_voltage_ratio: float
    ceramic_voltage_ratio: float
    outer_voltage_ratio: float
    inner_voltage_v: float
    ceramic_voltage_v: float
    outer_voltage_v: float
    inner_field_mv_m: float
    ceramic_equivalent_thickness_um: float
    ceramic_equivalent_field_mv_m: float
    outer_field_mv_m: float
    dominant_voltage_segment_code: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["dominant_voltage_segment_label"] = SEGMENT_LABELS[self.dominant_voltage_segment_code]
        return data

    def as_row(self) -> list[str]:
        return [
            f"{self.angle_deg:.1f}",
            f"{self.load_n:.2f}",
            f"{self.contact_angle_deg:.3f}",
            f"{self.inner_film_thickness_um:.4f}",
            f"{self.outer_film_thickness_um:.4f}",
            f"{self.inner_contact_capacitance_pf:.5f}",
            f"{self.ceramic_body_capacitance_pf:.5f}",
            f"{self.outer_contact_capacitance_pf:.5f}",
            f"{self.path_capacitance_pf:.5f}",
            f"{self.inner_voltage_ratio:.4f}",
            f"{self.ceramic_voltage_ratio:.4f}",
            f"{self.outer_voltage_ratio:.4f}",
            f"{self.inner_voltage_v:.5f}",
            f"{self.ceramic_voltage_v:.5f}",
            f"{self.outer_voltage_v:.5f}",
            f"{self.inner_field_mv_m:.4f}",
            f"{self.ceramic_equivalent_field_mv_m:.4f}",
            f"{self.outer_field_mv_m:.4f}",
            SEGMENT_LABELS[self.dominant_voltage_segment_code],
        ]


def astm_d341_kinematic_viscosity_cst(nu_40_cst: float, nu_100_cst: float, temperature_c: float) -> float:
    if nu_40_cst <= 0 or nu_100_cst <= 0:
        raise ValueError("ASTM D341 requires both viscosity inputs to be positive.")

    temperature_k = temperature_c + 273.15
    if temperature_k <= 0:
        raise ValueError("temperature must be above absolute zero.")

    x_40 = math.log10(40.0 + 273.15)
    x_100 = math.log10(100.0 + 273.15)
    y_40 = math.log10(math.log10(nu_40_cst + 0.7))
    y_100 = math.log10(math.log10(nu_100_cst + 0.7))
    slope = (y_40 - y_100) / (x_100 - x_40)
    intercept = y_40 + slope * x_40
    y_temp = intercept - slope * math.log10(temperature_k)
    return (10.0 ** (10.0**y_temp)) - 0.7


def dynamic_viscosity_from_kinematic_cst(nu_cst: float, density_kg_m3: float) -> float:
    if nu_cst <= 0 or density_kg_m3 <= 0:
        raise ValueError("Both viscosity and density must be positive.")
    return nu_cst * 1e-6 * density_kg_m3


def risk_level_numeric(level: str) -> int:
    return RISK_LEVEL_ORDER[level]


def voltage_segment_code(inner_ratio: float, ceramic_ratio: float, outer_ratio: float) -> str:
    segments = {
        "inner_oil_film": inner_ratio,
        "ceramic_ball": ceramic_ratio,
        "outer_oil_film": outer_ratio,
    }
    return max(segments, key=segments.get)


def roughness_gap_factor(lambda_value: float) -> float:
    if lambda_value >= 3.0:
        return 1.0
    if lambda_value >= 1.0:
        return lambda_value / 3.0
    return 0.25


def apply_bearing_preset(values: dict[str, Any]) -> dict[str, Any]:
    preset_name = str(values.get("bearing_code", "6208") or "6208")
    preset = BEARING_PRESETS.get(preset_name, BEARING_PRESETS["6208"]).copy()
    merged = {"bearing_code": preset_name, **preset}
    merged.update(values)
    return merged


class HybridBearingCapacitanceModel:
    def __init__(self, geometry: BearingGeometry | None = None, lubricant: LubricantProperties | None = None) -> None:
        self.geometry = geometry or BearingGeometry()
        self.lubricant = lubricant or LubricantProperties()
        self.geometry.validate()
        self.lubricant.validate()

    def _solve_elliptical_param(self, cos_tau: float) -> tuple[float, float, float]:
        cos_tau = float(np.clip(cos_tau, 1e-6, 0.9999))

        def objective(eccentricity: float) -> float:
            if eccentricity <= 0.0 or eccentricity >= 1.0:
                return 1.0
            k_val = ellipk(eccentricity**2)
            e_val = ellipe(eccentricity**2)
            return (
                ((2.0 - eccentricity**2) * e_val - 2.0 * (1.0 - eccentricity**2) * k_val)
                / (eccentricity**2 * e_val)
                - cos_tau
            )

        eccentricity = float(fsolve(objective, 0.9)[0])
        k_val = float(ellipk(eccentricity**2))
        e_val = float(ellipe(eccentricity**2))
        ellipticity = float(1.0 / math.sqrt(1.0 - eccentricity**2))
        return k_val, e_val, ellipticity

    def _contact_stiffness(self, *, is_inner: bool) -> tuple[float, float, float, float, float]:
        g = self.geometry
        rho11 = rho12 = 2.0 / g.ball_diameter_mm
        if is_inner:
            rho21 = -1.0 / (g.inner_curvature_coeff * g.ball_diameter_mm)
            rho22 = -2.0 / (g.pitch_diameter_mm - g.ball_diameter_mm)
        else:
            rho21 = -1.0 / (g.outer_curvature_coeff * g.ball_diameter_mm)
            rho22 = 2.0 / (g.pitch_diameter_mm + g.ball_diameter_mm)

        sum_rho = rho11 + rho12 + rho21 + rho22
        diff_rho = (rho11 - rho12) + (rho21 - rho22)
        cos_tau = abs(diff_rho) / sum_rho
        k_el, e_el, ellipticity = self._solve_elliptical_param(cos_tau)

        q_test = 1.0
        term_common = (3.0 * q_test) / (2.0 * sum_rho * g.equivalent_modulus_mpa)
        a_star = (2.0 * (ellipticity**2) * e_el / math.pi) ** (1.0 / 3.0)
        delta_star = (2.0 * k_el) / (math.pi * a_star)
        delta_1n = delta_star * (sum_rho / 2.0) * (term_common ** (2.0 / 3.0))
        stiffness = 1.0 / (delta_1n**1.5)
        equivalent_radius_mm = 1.0 / (rho12 + rho22)
        return stiffness, ellipticity, sum_rho, e_el, equivalent_radius_mm

    def _hertz_contact(self, load_n: float, sum_rho: float, ellipticity: float, e_val: float) -> tuple[float, float, float, float]:
        if load_n <= 1e-9:
            return 0.0, 0.0, 0.0, 0.0

        term_common = (3.0 * load_n) / (2.0 * sum_rho * self.geometry.equivalent_modulus_mpa)
        a_star = (2.0 * (ellipticity**2) * e_val / math.pi) ** (1.0 / 3.0)
        b_star = (2.0 * e_val / (math.pi * ellipticity)) ** (1.0 / 3.0)
        semi_major_mm = a_star * (term_common ** (1.0 / 3.0))
        semi_minor_mm = b_star * (term_common ** (1.0 / 3.0))
        area_mm2 = math.pi * semi_major_mm * semi_minor_mm
        max_pressure_mpa = (1.5 * load_n) / area_mm2
        return area_mm2, semi_major_mm, semi_minor_mm, max_pressure_mpa

    def _central_film_thickness_mm(
        self,
        load_n: float,
        equivalent_radius_m: float,
        entrainment_speed_m_s: float,
        ellipticity: float,
        dynamic_viscosity_pa_s: float,
    ) -> float:
        if load_n <= 1e-9 or equivalent_radius_m <= 0.0 or entrainment_speed_m_s <= 0.0:
            return 0.0

        e_prime_pa = self.geometry.equivalent_modulus_mpa * 1e6
        u_dimless = (dynamic_viscosity_pa_s * entrainment_speed_m_s) / (e_prime_pa * equivalent_radius_m)
        g_dimless = self.lubricant.pressure_viscosity_coeff_pa_inv * e_prime_pa
        w_dimless = load_n / (e_prime_pa * equivalent_radius_m**2)
        k_effect = 1.0 - 0.61 * math.exp(-0.73 * ellipticity)
        h_dimless = 2.69 * (u_dimless**0.67) * (g_dimless**0.53) * (w_dimless**-0.067) * k_effect
        return h_dimless * equivalent_radius_m * 1000.0

    def _entrainment_speeds(self, speed_rpm: float) -> tuple[float, float]:
        ratio = self.geometry.ball_diameter_mm / self.geometry.pitch_diameter_mm
        inner_speed = (math.pi * speed_rpm * self.geometry.pitch_diameter_mm / 120.0) * (1.0 - ratio**2) / 1000.0
        outer_speed = (math.pi * speed_rpm * self.geometry.pitch_diameter_mm / 120.0) * (1.0 + ratio**2) / 1000.0
        return inner_speed, outer_speed

    def _solve_equilibrium(
        self,
        radial_load_n: float,
        axial_load_n: float,
        total_stiffness: float,
        operating_clearance_mm: float,
        initial_guess_um: tuple[float, float] | None = None,
    ) -> tuple[float, float, bool]:
        g = self.geometry
        angles = np.linspace(0.0, 2.0 * math.pi, g.rolling_elements, endpoint=False)

        def equilibrium_equations(vars_um: np.ndarray) -> list[float]:
            radial_deflection_mm = vars_um[0] * 1e-3
            axial_deflection_mm = vars_um[1] * 1e-3
            force_x = 0.0
            force_z = 0.0
            for psi in angles:
                term_r = g.groove_span_mm + radial_deflection_mm * math.cos(psi)
                term_a = axial_deflection_mm
                distance_mm = math.sqrt(term_r**2 + term_a**2)
                delta_mm = distance_mm - g.groove_span_mm - (operating_clearance_mm / 2.0)
                if delta_mm > 0.0:
                    load_n = total_stiffness * delta_mm**1.5
                    force_x += load_n * (term_r / distance_mm) * math.cos(psi)
                    force_z += load_n * (term_a / distance_mm)
            return [force_x - radial_load_n, force_z - axial_load_n]

        guesses = []
        if initial_guess_um is not None:
            guesses.append(np.array(initial_guess_um))
        guesses.extend([np.array([30.0, 0.0]), np.array([80.0, 10.0]), np.array([150.0, 40.0])])

        best_solution = (0.0, 0.0, False)
        best_residual = float("inf")

        for guess in guesses:
            solution, _, ier, _ = fsolve(equilibrium_equations, guess, full_output=True, xtol=1e-9, maxfev=400)
            residual = equilibrium_equations(solution)
            residual_norm = float(abs(residual[0]) + abs(residual[1]))
            if residual_norm < best_residual:
                best_solution = (float(solution[0]), float(solution[1]), ier == 1)
                best_residual = residual_norm
            if ier == 1 and residual_norm < 1e-4:
                return float(solution[0]), float(solution[1]), True

        return best_solution

    def _single_case(
        self,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        initial_guess_um: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
        conditions.validate()
        self.geometry.validate()
        self.lubricant.validate()
        parasitics.validate()

        inner_viscosity_40, inner_viscosity_100 = self.lubricant.effective_viscosity_pair()
        inner_kinematic_cst = astm_d341_kinematic_viscosity_cst(
            inner_viscosity_40,
            inner_viscosity_100,
            conditions.inner_ring_temp_c,
        )
        outer_kinematic_cst = astm_d341_kinematic_viscosity_cst(
            inner_viscosity_40,
            inner_viscosity_100,
            conditions.outer_ring_temp_c,
        )
        inner_density = self.lubricant.density_at(conditions.inner_ring_temp_c, 0.0)
        outer_density = self.lubricant.density_at(conditions.outer_ring_temp_c, 0.0)
        inner_dynamic_viscosity = dynamic_viscosity_from_kinematic_cst(inner_kinematic_cst, inner_density)
        outer_dynamic_viscosity = dynamic_viscosity_from_kinematic_cst(outer_kinematic_cst, outer_density)

        inner_stiffness, inner_ellipticity, inner_sum_rho, inner_e_val, inner_rx_mm = self._contact_stiffness(is_inner=True)
        outer_stiffness, outer_ellipticity, outer_sum_rho, outer_e_val, outer_rx_mm = self._contact_stiffness(is_inner=False)
        total_stiffness = 1.0 / (((1.0 / inner_stiffness) ** (2.0 / 3.0) + (1.0 / outer_stiffness) ** (2.0 / 3.0)) ** 1.5)
        operating_clearance_mm = self.geometry.operating_clearance_mm(
            conditions.fit_clearance_loss_um,
            conditions.thermal_clearance_loss_um,
        )
        total_axial_load = conditions.axial_load_n + conditions.axial_preload_n
        radial_um, axial_um, solver_converged = self._solve_equilibrium(
            conditions.radial_load_n,
            total_axial_load,
            total_stiffness,
            operating_clearance_mm,
            initial_guess_um=initial_guess_um,
        )

        entrainment_inner_m_s, entrainment_outer_m_s = self._entrainment_speeds(conditions.speed_rpm)
        inner_rx_m = inner_rx_mm / 1000.0
        outer_rx_m = outer_rx_mm / 1000.0
        angles = np.linspace(0.0, 2.0 * math.pi, self.geometry.rolling_elements, endpoint=False)
        roughness_um = self.geometry.composite_roughness_um * self.lubricant.state_factors["roughness"]

        details: list[BallPathDetail] = []
        intrinsic_total_pf = 0.0
        inner_sum_pf = 0.0
        ceramic_sum_pf = 0.0
        outer_sum_pf = 0.0

        radial_deflection_mm = radial_um * 1e-3
        axial_deflection_mm = axial_um * 1e-3

        for psi in angles:
            term_r = self.geometry.groove_span_mm + radial_deflection_mm * math.cos(psi)
            term_a = axial_deflection_mm
            distance_mm = math.sqrt(term_r**2 + term_a**2)
            delta_mm = distance_mm - self.geometry.groove_span_mm - (operating_clearance_mm / 2.0)
            if delta_mm <= 0.0:
                continue

            load_n = total_stiffness * delta_mm**1.5
            contact_angle_deg = math.degrees(math.asin(term_a / distance_mm)) if distance_mm > 0 else 0.0

            inner_area_mm2, _, _, inner_pressure_mpa = self._hertz_contact(load_n, inner_sum_rho, inner_ellipticity, inner_e_val)
            outer_area_mm2, _, _, outer_pressure_mpa = self._hertz_contact(load_n, outer_sum_rho, outer_ellipticity, outer_e_val)

            inner_film_mm = self._central_film_thickness_mm(
                load_n,
                inner_rx_m,
                entrainment_inner_m_s,
                inner_ellipticity,
                inner_dynamic_viscosity,
            )
            outer_film_mm = self._central_film_thickness_mm(
                load_n,
                outer_rx_m,
                entrainment_outer_m_s,
                outer_ellipticity,
                outer_dynamic_viscosity,
            )

            inner_lambda = (inner_film_mm * 1000.0) / roughness_um if roughness_um > 0 else 0.0
            outer_lambda = (outer_film_mm * 1000.0) / roughness_um if roughness_um > 0 else 0.0
            inner_effective_gap_m = inner_film_mm * 1e-3 * roughness_gap_factor(inner_lambda)
            outer_effective_gap_m = outer_film_mm * 1e-3 * roughness_gap_factor(outer_lambda)

            inner_area_m2 = inner_area_mm2 * 1e-6
            outer_area_m2 = outer_area_mm2 * 1e-6
            inner_eps_r = self.lubricant.relative_permittivity(conditions.inner_ring_temp_c, inner_pressure_mpa * 1e6)
            outer_eps_r = self.lubricant.relative_permittivity(conditions.outer_ring_temp_c, outer_pressure_mpa * 1e6)

            inner_cap_pf = EPSILON_0 * inner_eps_r * inner_area_m2 / max(inner_effective_gap_m, 1e-12) * 1e12
            outer_cap_pf = EPSILON_0 * outer_eps_r * outer_area_m2 / max(outer_effective_gap_m, 1e-12) * 1e12

            effective_area_m2 = 0.0
            if inner_area_m2 > 0.0 and outer_area_m2 > 0.0:
                effective_area_m2 = 2.0 * inner_area_m2 * outer_area_m2 / (inner_area_m2 + outer_area_m2)
            effective_radius_m = math.sqrt(effective_area_m2 / math.pi) if effective_area_m2 > 0.0 else 0.0
            ceramic_cap_pf = 4.0 * EPSILON_0 * self.geometry.ceramic_relative_permittivity * effective_radius_m * 1e12

            inverse_series = 0.0
            for cap_pf in (inner_cap_pf, ceramic_cap_pf, outer_cap_pf):
                if cap_pf <= 0.0:
                    inverse_series = math.inf
                    break
                inverse_series += 1.0 / cap_pf
            path_capacitance_pf = 0.0 if inverse_series in {0.0, math.inf} else 1.0 / inverse_series

            inner_voltage_ratio = path_capacitance_pf / inner_cap_pf if inner_cap_pf > 0 else 0.0
            ceramic_voltage_ratio = path_capacitance_pf / ceramic_cap_pf if ceramic_cap_pf > 0 else 0.0
            outer_voltage_ratio = path_capacitance_pf / outer_cap_pf if outer_cap_pf > 0 else 0.0

            inner_voltage_v = conditions.applied_voltage_v * inner_voltage_ratio
            ceramic_voltage_v = conditions.applied_voltage_v * ceramic_voltage_ratio
            outer_voltage_v = conditions.applied_voltage_v * outer_voltage_ratio

            inner_field_mv_m = 0.0 if inner_effective_gap_m <= 0.0 else inner_voltage_v / inner_effective_gap_m / 1e6
            outer_field_mv_m = 0.0 if outer_effective_gap_m <= 0.0 else outer_voltage_v / outer_effective_gap_m / 1e6
            ceramic_equivalent_thickness_m = 0.0
            if effective_area_m2 > 0.0 and ceramic_cap_pf > 0.0:
                ceramic_equivalent_thickness_m = (
                    EPSILON_0 * self.geometry.ceramic_relative_permittivity * effective_area_m2 / (ceramic_cap_pf * 1e-12)
                )
            ceramic_equivalent_field_mv_m = (
                0.0 if ceramic_equivalent_thickness_m <= 0.0 else ceramic_voltage_v / ceramic_equivalent_thickness_m / 1e6
            )
            dominant_voltage_segment_code = voltage_segment_code(
                inner_voltage_ratio,
                ceramic_voltage_ratio,
                outer_voltage_ratio,
            )

            intrinsic_total_pf += path_capacitance_pf
            inner_sum_pf += inner_cap_pf
            ceramic_sum_pf += ceramic_cap_pf
            outer_sum_pf += outer_cap_pf

            details.append(
                BallPathDetail(
                    angle_deg=math.degrees(psi),
                    load_n=load_n,
                    contact_angle_deg=contact_angle_deg,
                    inner_hertz_area_mm2=inner_area_mm2,
                    outer_hertz_area_mm2=outer_area_mm2,
                    inner_film_thickness_um=inner_film_mm * 1000.0,
                    outer_film_thickness_um=outer_film_mm * 1000.0,
                    inner_effective_gap_um=inner_effective_gap_m * 1e6,
                    outer_effective_gap_um=outer_effective_gap_m * 1e6,
                    inner_contact_capacitance_pf=inner_cap_pf,
                    ceramic_body_capacitance_pf=ceramic_cap_pf,
                    outer_contact_capacitance_pf=outer_cap_pf,
                    path_capacitance_pf=path_capacitance_pf,
                    inner_mean_pressure_mpa=inner_pressure_mpa,
                    outer_mean_pressure_mpa=outer_pressure_mpa,
                    inner_relative_permittivity=inner_eps_r,
                    outer_relative_permittivity=outer_eps_r,
                    inner_lambda=inner_lambda,
                    outer_lambda=outer_lambda,
                    inner_voltage_ratio=inner_voltage_ratio,
                    ceramic_voltage_ratio=ceramic_voltage_ratio,
                    outer_voltage_ratio=outer_voltage_ratio,
                    inner_voltage_v=inner_voltage_v,
                    ceramic_voltage_v=ceramic_voltage_v,
                    outer_voltage_v=outer_voltage_v,
                    inner_field_mv_m=inner_field_mv_m,
                    ceramic_equivalent_thickness_um=ceramic_equivalent_thickness_m * 1e6,
                    ceramic_equivalent_field_mv_m=ceramic_equivalent_field_mv_m,
                    outer_field_mv_m=outer_field_mv_m,
                    dominant_voltage_segment_code=dominant_voltage_segment_code,
                )
            )

        active_details = [detail for detail in details if detail.load_n > 0.0]
        intrinsic_total_pf = sum(detail.path_capacitance_pf for detail in active_details)
        measured_total_pf = intrinsic_total_pf + parasitics.total_pf

        mean_inner_voltage_ratio = (
            sum(detail.inner_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        mean_ceramic_voltage_ratio = (
            sum(detail.ceramic_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        mean_outer_voltage_ratio = (
            sum(detail.outer_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        dominant_voltage_segment_code = (
            voltage_segment_code(mean_inner_voltage_ratio, mean_ceramic_voltage_ratio, mean_outer_voltage_ratio)
            if active_details
            else "no_loaded_path"
        )

        max_oil_film_field_mv_m = max(
            [detail.inner_field_mv_m for detail in active_details] + [detail.outer_field_mv_m for detail in active_details],
            default=0.0,
        )
        min_lambda = min(
            [detail.inner_lambda for detail in active_details] + [detail.outer_lambda for detail in active_details],
            default=0.0,
        )
        risk_level = self._classify_risk(max_oil_film_field_mv_m, min_lambda)
        risk_segment_code = self._risk_segment(active_details)
        parasitic_mode = "intrinsic_dominant" if intrinsic_total_pf >= parasitics.total_pf else "parasitic_dominant"

        single_frequency = self._single_frequency_response(measured_total_pf, conditions.single_frequency_hz)

        return {
            "summary": {
                "intrinsic_capacitance_pf": intrinsic_total_pf,
                "effective_capacitance_pf": measured_total_pf,
                "parasitic_total_pf": parasitics.total_pf,
                "parasitics_pf": asdict(parasitics),
                "applied_voltage_v": conditions.applied_voltage_v,
                "single_frequency_hz": conditions.single_frequency_hz,
                "single_frequency_response": single_frequency,
                "inner_operating_kinematic_viscosity_cst": inner_kinematic_cst,
                "outer_operating_kinematic_viscosity_cst": outer_kinematic_cst,
                "inner_operating_dynamic_viscosity_pa_s": inner_dynamic_viscosity,
                "outer_operating_dynamic_viscosity_pa_s": outer_dynamic_viscosity,
                "radial_displacement_um": radial_um,
                "axial_displacement_um": axial_um,
                "loaded_ball_count": len(active_details),
                "mean_ball_load_n": (
                    sum(detail.load_n for detail in active_details) / len(active_details) if active_details else 0.0
                ),
                "max_ball_load_n": max((detail.load_n for detail in active_details), default=0.0),
                "min_inner_film_thickness_um": min((detail.inner_film_thickness_um for detail in active_details), default=0.0),
                "min_outer_film_thickness_um": min((detail.outer_film_thickness_um for detail in active_details), default=0.0),
                "min_inner_lambda": min((detail.inner_lambda for detail in active_details), default=0.0),
                "min_outer_lambda": min((detail.outer_lambda for detail in active_details), default=0.0),
                "max_inner_field_mv_m": max((detail.inner_field_mv_m for detail in active_details), default=0.0),
                "max_outer_field_mv_m": max((detail.outer_field_mv_m for detail in active_details), default=0.0),
                "max_ceramic_equivalent_field_mv_m": max(
                    (detail.ceramic_equivalent_field_mv_m for detail in active_details),
                    default=0.0,
                ),
                "max_oil_film_field_mv_m": max_oil_film_field_mv_m,
                "inner_contact_sum_pf": inner_sum_pf,
                "ceramic_body_sum_pf": ceramic_sum_pf,
                "outer_contact_sum_pf": outer_sum_pf,
                "mean_inner_voltage_ratio": mean_inner_voltage_ratio,
                "mean_ceramic_voltage_ratio": mean_ceramic_voltage_ratio,
                "mean_outer_voltage_ratio": mean_outer_voltage_ratio,
                "dominant_voltage_segment_code": dominant_voltage_segment_code,
                "dominant_voltage_segment_label": SEGMENT_LABELS[dominant_voltage_segment_code],
                "risk_level": risk_level,
                "risk_level_numeric": risk_level_numeric(risk_level),
                "risk_segment_code": risk_segment_code,
                "risk_segment_label": SEGMENT_LABELS.get(risk_segment_code, SEGMENT_LABELS["no_loaded_path"]),
                "risk_trigger_reason_code": self._risk_reason_code(max_oil_film_field_mv_m, min_lambda),
                "parasitic_mode": parasitic_mode,
                "operating_clearance_mm": operating_clearance_mm,
                "equivalent_modulus_gpa": self.geometry.equivalent_modulus_mpa / 1000.0,
                "solver_converged": solver_converged,
                "roughness_um": roughness_um,
            },
            "details": [detail.to_dict() for detail in active_details],
            "equilibrium_guess_um": [radial_um, axial_um],
        }

    @staticmethod
    def _single_frequency_response(capacitance_pf: float, frequency_hz: float) -> dict[str, float]:
        capacitance_f = capacitance_pf * 1e-12
        if capacitance_f <= 0.0:
            return {
                "capacitance_pf": capacitance_pf,
                "frequency_hz": frequency_hz,
                "reactance_ohm": math.inf,
                "impedance_magnitude_ohm": math.inf,
                "phase_deg": -90.0,
            }
        reactance_ohm = 1.0 / (2.0 * math.pi * frequency_hz * capacitance_f)
        return {
            "capacitance_pf": capacitance_pf,
            "frequency_hz": frequency_hz,
            "reactance_ohm": reactance_ohm,
            "impedance_magnitude_ohm": reactance_ohm,
            "phase_deg": -90.0,
        }

    @staticmethod
    def _classify_risk(max_field_mv_m: float, min_lambda: float) -> str:
        if max_field_mv_m > 10.0 or min_lambda < 1.0:
            return "critical"
        if 5.0 <= max_field_mv_m <= 10.0 or 1.0 <= min_lambda < 1.5:
            return "high"
        if 2.0 <= max_field_mv_m < 5.0 or 1.5 <= min_lambda < 3.0:
            return "medium"
        return "low"

    @staticmethod
    def _risk_reason_code(max_field_mv_m: float, min_lambda: float) -> str:
        if max_field_mv_m > 10.0:
            return "field_above_10"
        if min_lambda < 1.0:
            return "lambda_below_1"
        if max_field_mv_m >= 5.0:
            return "field_above_5"
        if min_lambda < 1.5:
            return "lambda_below_1_5"
        if max_field_mv_m >= 2.0:
            return "field_above_2"
        if min_lambda < 3.0:
            return "lambda_below_3"
        return "stable_ehl"

    @staticmethod
    def _risk_segment(details: list[BallPathDetail]) -> str:
        if not details:
            return "no_loaded_path"
        candidates = []
        for detail in details:
            candidates.extend(
                [
                    (detail.inner_field_mv_m, "inner_oil_film"),
                    (detail.outer_field_mv_m, "outer_oil_film"),
                ]
            )
        return max(candidates, key=lambda item: item[0])[1]

    def analyze_case(
        self,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        sweep_settings: SweepSettings,
        include_extended: bool = True,
    ) -> dict[str, Any]:
        base = self._single_case(conditions, parasitics)
        result = {
            "version": MODEL_VERSION,
            "inputs": {
                "geometry": asdict(self.geometry),
                "lubricant": asdict(self.lubricant),
                "conditions": asdict(conditions),
                "parasitics": asdict(parasitics),
                "sweep_settings": asdict(sweep_settings),
            },
            "summary": base["summary"],
            "details": base["details"],
            "explanations": self._explanation_flags(base["summary"]),
            "model_note": "Pure capacitive impedance model without leakage resistance or conductive oil-film branches.",
        }

        if not include_extended:
            return result

        sweep_settings.validate()
        base_guess = tuple(base["equilibrium_guess_um"])

        frequency_sweep = self.frequency_sweep(base["summary"]["effective_capacitance_pf"], sweep_settings)
        speed_sweep = self._condition_sweep(
            conditions,
            parasitics,
            sweep_settings,
            variable="speed_rpm",
            points=np.linspace(sweep_settings.speed_start_rpm, sweep_settings.speed_end_rpm, sweep_settings.condition_point_count),
            guess=base_guess,
        )
        temperature_sweep = self._temperature_sweep(conditions, parasitics, sweep_settings, base_guess)
        radial_load_sweep = self._condition_sweep(
            conditions,
            parasitics,
            sweep_settings,
            variable="radial_load_n",
            points=np.linspace(
                sweep_settings.radial_load_start_n,
                sweep_settings.radial_load_end_n,
                sweep_settings.condition_point_count,
            ),
            guess=base_guess,
        )
        sensitivity = self.sensitivity_analysis(conditions, parasitics, sweep_settings)

        result["frequency_sweep"] = frequency_sweep
        result["condition_sweeps"] = {
            "speed": speed_sweep,
            "temperature": temperature_sweep,
            "radial_load": radial_load_sweep,
        }
        result["sensitivity"] = sensitivity
        return result

    @staticmethod
    def frequency_sweep(effective_capacitance_pf: float, sweep_settings: SweepSettings) -> dict[str, list[float]]:
        frequencies = np.logspace(
            math.log10(sweep_settings.frequency_start_hz),
            math.log10(sweep_settings.frequency_end_hz),
            sweep_settings.frequency_point_count,
        )
        reactances = []
        for frequency_hz in frequencies:
            response = HybridBearingCapacitanceModel._single_frequency_response(effective_capacitance_pf, float(frequency_hz))
            reactances.append(response["reactance_ohm"])
        return {
            "frequency_hz": [float(value) for value in frequencies],
            "reactance_ohm": reactances,
            "impedance_magnitude_ohm": reactances,
        }

    def _condition_sweep(
        self,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        sweep_settings: SweepSettings,
        variable: str,
        points: np.ndarray,
        guess: tuple[float, float],
    ) -> dict[str, list[float]]:
        x_values: list[float] = []
        effective_capacitance_pf: list[float] = []
        max_field_mv_m: list[float] = []
        risk_level_numeric_values: list[int] = []
        dominant_segment_codes: list[str] = []
        current_guess = guess

        for value in points:
            case_conditions = replace(conditions, **{variable: float(value)})
            result = self._single_case(case_conditions, parasitics, initial_guess_um=current_guess)
            current_guess = tuple(result["equilibrium_guess_um"])
            summary = result["summary"]
            x_values.append(float(value))
            effective_capacitance_pf.append(summary["effective_capacitance_pf"])
            max_field_mv_m.append(summary["max_oil_film_field_mv_m"])
            risk_level_numeric_values.append(summary["risk_level_numeric"])
            dominant_segment_codes.append(summary["dominant_voltage_segment_code"])

        return {
            "x": x_values,
            "effective_capacitance_pf": effective_capacitance_pf,
            "max_oil_film_field_mv_m": max_field_mv_m,
            "risk_level_numeric": risk_level_numeric_values,
            "dominant_segment_code": dominant_segment_codes,
            "variable": variable,
        }

    def _temperature_sweep(
        self,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        sweep_settings: SweepSettings,
        guess: tuple[float, float],
    ) -> dict[str, list[float]]:
        temperatures = np.linspace(
            sweep_settings.temperature_start_c,
            sweep_settings.temperature_end_c,
            sweep_settings.condition_point_count,
        )
        x_values: list[float] = []
        effective_capacitance_pf: list[float] = []
        max_field_mv_m: list[float] = []
        risk_level_numeric_values: list[int] = []
        dominant_segment_codes: list[str] = []
        current_guess = guess

        for value in temperatures:
            case_conditions = replace(conditions, inner_ring_temp_c=float(value), outer_ring_temp_c=float(value))
            result = self._single_case(case_conditions, parasitics, initial_guess_um=current_guess)
            current_guess = tuple(result["equilibrium_guess_um"])
            summary = result["summary"]
            x_values.append(float(value))
            effective_capacitance_pf.append(summary["effective_capacitance_pf"])
            max_field_mv_m.append(summary["max_oil_film_field_mv_m"])
            risk_level_numeric_values.append(summary["risk_level_numeric"])
            dominant_segment_codes.append(summary["dominant_voltage_segment_code"])

        return {
            "x": x_values,
            "effective_capacitance_pf": effective_capacitance_pf,
            "max_oil_film_field_mv_m": max_field_mv_m,
            "risk_level_numeric": risk_level_numeric_values,
            "dominant_segment_code": dominant_segment_codes,
            "variable": "ring_temperature_c",
        }

    def sensitivity_analysis(
        self,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        sweep_settings: SweepSettings,
    ) -> dict[str, list[dict[str, Any]]]:
        baseline = self._single_case(conditions, parasitics)
        baseline_summary = baseline["summary"]
        metric_rankings = {
            "effective_capacitance_pf": [],
            "max_oil_film_field": [],
            "risk_level": [],
        }

        for target in SENSITIVITY_TARGETS:
            lower_inputs = self._perturb(target, conditions, parasitics, -0.10)
            upper_inputs = self._perturb(target, conditions, parasitics, 0.10)
            lower_result = lower_inputs["model"]._single_case(lower_inputs["conditions"], lower_inputs["parasitics"])
            upper_result = upper_inputs["model"]._single_case(upper_inputs["conditions"], upper_inputs["parasitics"])

            cap_delta = max(
                abs(lower_result["summary"]["effective_capacitance_pf"] - baseline_summary["effective_capacitance_pf"]),
                abs(upper_result["summary"]["effective_capacitance_pf"] - baseline_summary["effective_capacitance_pf"]),
            )
            field_delta = max(
                abs(lower_result["summary"]["max_oil_film_field_mv_m"] - baseline_summary["max_oil_film_field_mv_m"]),
                abs(upper_result["summary"]["max_oil_film_field_mv_m"] - baseline_summary["max_oil_film_field_mv_m"]),
            )
            risk_delta = max(
                abs(lower_result["summary"]["risk_level_numeric"] - baseline_summary["risk_level_numeric"]),
                abs(upper_result["summary"]["risk_level_numeric"] - baseline_summary["risk_level_numeric"]),
            )

            entry = {
                "parameter": target,
                "minus_10": self._sensitivity_snapshot(lower_result["summary"]),
                "plus_10": self._sensitivity_snapshot(upper_result["summary"]),
                "baseline": self._sensitivity_snapshot(baseline_summary),
            }
            metric_rankings["effective_capacitance_pf"].append((cap_delta, entry))
            metric_rankings["max_oil_film_field"].append((field_delta, entry))
            metric_rankings["risk_level"].append((risk_delta, entry))

        return {
            metric: [entry for _, entry in sorted(entries, key=lambda item: item[0], reverse=True)]
            for metric, entries in metric_rankings.items()
        }

    @staticmethod
    def _sensitivity_snapshot(summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "effective_capacitance_pf": summary["effective_capacitance_pf"],
            "max_oil_film_field_mv_m": summary["max_oil_film_field_mv_m"],
            "risk_level": summary["risk_level"],
            "risk_level_numeric": summary["risk_level_numeric"],
        }

    def _perturb(
        self,
        target: str,
        conditions: OperatingConditions,
        parasitics: ParasiticCapacitances,
        factor: float,
    ) -> dict[str, Any]:
        geometry = self.geometry
        lubricant = self.lubricant

        if target in {"ball_diameter_mm", "pitch_diameter_mm", "composite_roughness_um", "ceramic_relative_permittivity"}:
            base_value = getattr(geometry, target)
            new_geometry = replace(geometry, **{target: max(base_value * (1.0 + factor), 1e-9)})
            model = HybridBearingCapacitanceModel(new_geometry, lubricant)
            return {"conditions": conditions, "parasitics": parasitics, "model": model}
        if target == "relative_permittivity_25c":
            new_lubricant = replace(lubricant, relative_permittivity_25c=max(lubricant.relative_permittivity_25c * (1.0 + factor), 1.01))
            model = HybridBearingCapacitanceModel(geometry, new_lubricant)
            return {"conditions": conditions, "parasitics": parasitics, "model": model}
        if target == "background_capacitance_pf":
            new_parasitics = replace(parasitics, background_capacitance_pf=max(parasitics.background_capacitance_pf * (1.0 + factor), 0.0))
            return {"conditions": conditions, "parasitics": new_parasitics, "model": self}
        if target == "radial_load_n":
            new_conditions = replace(conditions, radial_load_n=max(conditions.radial_load_n * (1.0 + factor), 0.0))
            return {"conditions": new_conditions, "parasitics": parasitics, "model": self}
        if target == "inner_ring_temp_c":
            new_conditions = replace(conditions, inner_ring_temp_c=conditions.inner_ring_temp_c * (1.0 + factor))
            return {"conditions": new_conditions, "parasitics": parasitics, "model": self}
        raise ValueError(f"Unsupported sensitivity target: {target}")

    def _explanation_flags(self, summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "dominant_segment_code": summary["dominant_voltage_segment_code"],
            "risk_segment_code": summary["risk_segment_code"],
            "parasitic_mode": summary["parasitic_mode"],
            "risk_level": summary["risk_level"],
            "risk_trigger_reason_code": summary["risk_trigger_reason_code"],
        }


def build_case_inputs(
    payload: Mapping[str, Any],
    include_extended: bool = True,
) -> tuple[BearingGeometry, LubricantProperties, ParasiticCapacitances, OperatingConditions, SweepSettings]:
    merged = apply_bearing_preset(dict(payload))
    temperature_legacy = merged.get("temperature_c")
    inner_ring_temp_c = merged.get("inner_ring_temp_c", temperature_legacy if temperature_legacy is not None else 60.0)
    outer_ring_temp_c = merged.get("outer_ring_temp_c", temperature_legacy if temperature_legacy is not None else 60.0)

    geometry = BearingGeometry(
        bearing_code=str(merged.get("bearing_code", "6208")),
        ball_diameter_mm=float(merged.get("ball_diameter_mm", 11.906)),
        pitch_diameter_mm=float(merged.get("pitch_diameter_mm", 60.0)),
        rolling_elements=int(float(merged.get("rolling_elements", 9))),
        radial_clearance_mm=float(merged.get("radial_clearance_mm", 0.015)),
        inner_curvature_coeff=float(merged.get("inner_curvature_coeff", 0.52)),
        outer_curvature_coeff=float(merged.get("outer_curvature_coeff", 0.53)),
        composite_roughness_um=float(merged.get("composite_roughness_um", 0.05)),
        ring_youngs_modulus_mpa=float(merged.get("ring_youngs_modulus_mpa", 210000.0)),
        ring_poisson_ratio=float(merged.get("ring_poisson_ratio", 0.30)),
        ceramic_youngs_modulus_mpa=float(merged.get("ceramic_youngs_modulus_mpa", 310000.0)),
        ceramic_poisson_ratio=float(merged.get("ceramic_poisson_ratio", 0.27)),
        ceramic_relative_permittivity=float(merged.get("ceramic_relative_permittivity", 8.2)),
    )
    lubricant = LubricantProperties(
        viscosity_40_cst=float(merged.get("viscosity_40_cst", 68.0)),
        viscosity_100_cst=float(merged.get("viscosity_100_cst", 8.8)),
        density_25c_kg_m3=float(merged.get("density_25c_kg_m3", 850.0)),
        relative_permittivity_25c=float(merged.get("relative_permittivity_25c", 2.25)),
        pressure_viscosity_coeff_pa_inv=float(merged.get("pressure_viscosity_coeff_pa_inv", 1.5e-8)),
        thermal_expansion_coeff_per_c=float(merged.get("thermal_expansion_coeff_per_c", 6.5e-4)),
        bulk_modulus_pa=float(merged.get("bulk_modulus_pa", 1.6e9)),
        lubrication_state=str(merged.get("lubrication_state", "clean_oil")),
    )
    parasitics = ParasiticCapacitances(
        background_capacitance_pf=float(merged.get("background_capacitance_pf", 0.8)),
        cage_capacitance_pf=float(merged.get("cage_capacitance_pf", 0.15)),
        seal_capacitance_pf=float(merged.get("seal_capacitance_pf", 0.05)),
        mounting_capacitance_pf=float(merged.get("mounting_capacitance_pf", 0.10)),
    )
    conditions = OperatingConditions(
        speed_rpm=float(merged.get("speed_rpm", 3000.0)),
        radial_load_n=float(merged.get("radial_load_n", 2000.0)),
        axial_load_n=float(merged.get("axial_load_n", 0.0)),
        axial_preload_n=float(merged.get("axial_preload_n", 0.0)),
        inner_ring_temp_c=float(inner_ring_temp_c),
        outer_ring_temp_c=float(outer_ring_temp_c),
        applied_voltage_v=float(merged.get("applied_voltage_v", 1.0)),
        single_frequency_hz=float(merged.get("single_frequency_hz", 10000.0)),
        fit_clearance_loss_um=float(merged.get("fit_clearance_loss_um", 0.0)),
        thermal_clearance_loss_um=float(merged.get("thermal_clearance_loss_um", 0.0)),
    )
    sweep_settings = SweepSettings(
        frequency_start_hz=float(merged.get("frequency_start_hz", 1000.0)),
        frequency_end_hz=float(merged.get("frequency_end_hz", 1.0e7)),
        frequency_point_count=int(float(merged.get("frequency_point_count", 121))),
        speed_start_rpm=float(merged.get("speed_start_rpm", 500.0)),
        speed_end_rpm=float(merged.get("speed_end_rpm", 12000.0)),
        temperature_start_c=float(merged.get("temperature_start_c", 20.0)),
        temperature_end_c=float(merged.get("temperature_end_c", 120.0)),
        radial_load_start_n=float(merged.get("radial_load_start_n", 500.0)),
        radial_load_end_n=float(merged.get("radial_load_end_n", 5000.0)),
        condition_point_count=int(float(merged.get("condition_point_count", 41))),
    )

    geometry.validate()
    lubricant.validate()
    parasitics.validate()
    conditions.validate()
    if include_extended:
        sweep_settings.validate()
    return geometry, lubricant, parasitics, conditions, sweep_settings


def analyze_case_payload(payload: Mapping[str, Any], include_extended: bool = True) -> dict[str, Any]:
    geometry, lubricant, parasitics, conditions, sweep_settings = build_case_inputs(payload, include_extended=include_extended)
    model = HybridBearingCapacitanceModel(geometry=geometry, lubricant=lubricant)
    return model.analyze_case(conditions, parasitics, sweep_settings, include_extended=include_extended)


def compare_case_payloads(
    case_a_payload: Mapping[str, Any],
    case_b_payload: Mapping[str, Any],
    include_extended: bool = True,
) -> dict[str, Any]:
    case_a = analyze_case_payload(case_a_payload, include_extended=include_extended)
    case_b = analyze_case_payload(case_b_payload, include_extended=include_extended)
    summary_a = case_a["summary"]
    summary_b = case_b["summary"]
    return {
        "case_a": case_a,
        "case_b": case_b,
        "comparison": {
            "effective_capacitance_delta_pf": summary_b["effective_capacitance_pf"] - summary_a["effective_capacitance_pf"],
            "max_oil_film_field_delta_mv_m": summary_b["max_oil_film_field_mv_m"] - summary_a["max_oil_film_field_mv_m"],
            "risk_level_delta": summary_b["risk_level_numeric"] - summary_a["risk_level_numeric"],
            "dominant_segment_changed": summary_a["dominant_voltage_segment_code"] != summary_b["dominant_voltage_segment_code"],
            "risk_segment_changed": summary_a["risk_segment_code"] != summary_b["risk_segment_code"],
        },
        "version": MODEL_VERSION,
        "model_note": case_a["model_note"],
    }
