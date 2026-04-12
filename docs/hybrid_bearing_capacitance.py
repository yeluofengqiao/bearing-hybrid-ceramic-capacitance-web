from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import fsolve
from scipy.special import ellipe, ellipk


EPSILON_0 = 8.8541878128e-12
REFERENCE_TEMPERATURE_C = 25.0


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
    def pitch_radius_m(self) -> float:
        return 0.5 * self.pitch_diameter_mm / 1000.0

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


@dataclass(frozen=True, slots=True)
class LubricantProperties:
    viscosity_40_cst: float = 68.0
    viscosity_100_cst: float = 8.8
    density_25c_kg_m3: float = 850.0
    relative_permittivity_25c: float = 2.25
    pressure_viscosity_coeff_pa_inv: float = 1.5e-8
    thermal_expansion_coeff_per_c: float = 6.5e-4
    bulk_modulus_pa: float = 1.6e9
    background_capacitance_pf: float = 0.8

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
        if self.background_capacitance_pf < 0:
            raise ValueError("background_capacitance_pf cannot be negative.")

    def density_at(self, temperature_c: float, pressure_pa: float) -> float:
        density_zero_pressure = self.density_25c_kg_m3 * (
            1.0 - self.thermal_expansion_coeff_per_c * (temperature_c - REFERENCE_TEMPERATURE_C)
        )
        density_zero_pressure = max(density_zero_pressure, self.density_25c_kg_m3 * 0.65)
        pressure_factor = 1.0 + max(pressure_pa, 0.0) / self.bulk_modulus_pa
        return density_zero_pressure * pressure_factor

    def relative_permittivity(self, temperature_c: float, pressure_pa: float) -> float:
        density_ref = self.density_25c_kg_m3
        cm_constant = (
            (self.relative_permittivity_25c - 1.0)
            / ((self.relative_permittivity_25c + 2.0) * density_ref)
        )
        density = self.density_at(temperature_c, pressure_pa)
        product = max(cm_constant * density, 1e-9)
        if product >= 0.98:
            product = 0.98
        permittivity = (1.0 + 2.0 * product) / (1.0 - product)
        return min(max(permittivity, 1.5), 6.0)


@dataclass(frozen=True, slots=True)
class OperatingConditions:
    speed_rpm: float = 3000.0
    radial_load_n: float = 2000.0
    axial_load_n: float = 0.0
    temperature_c: float = 60.0
    applied_voltage_v: float = 1.0

    def validate(self) -> None:
        if self.speed_rpm <= 0:
            raise ValueError("speed_rpm must be greater than 0.")
        if self.radial_load_n < 0:
            raise ValueError("radial_load_n cannot be negative.")
        if self.axial_load_n < 0:
            raise ValueError("axial_load_n cannot be negative.")
        if self.temperature_c <= -273.15:
            raise ValueError("temperature_c must be above absolute zero.")
        if self.applied_voltage_v < 0:
            raise ValueError("applied_voltage_v cannot be negative.")


@dataclass(frozen=True, slots=True)
class BallCapacitanceDetail:
    angle_deg: float
    load_n: float
    contact_angle_deg: float
    inner_hertz_area_mm2: float
    outer_hertz_area_mm2: float
    inner_film_thickness_um: float
    outer_film_thickness_um: float
    inner_contact_capacitance_pf: float
    ceramic_body_capacitance_pf: float
    outer_contact_capacitance_pf: float
    series_capacitance_pf: float
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
    dominant_voltage_segment: str

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
            f"{self.series_capacitance_pf:.5f}",
            f"{self.inner_voltage_ratio:.4f}",
            f"{self.ceramic_voltage_ratio:.4f}",
            f"{self.outer_voltage_ratio:.4f}",
            f"{self.inner_voltage_v:.5f}",
            f"{self.ceramic_voltage_v:.5f}",
            f"{self.outer_voltage_v:.5f}",
            f"{self.inner_field_mv_m:.4f}",
            f"{self.ceramic_equivalent_field_mv_m:.4f}",
            f"{self.outer_field_mv_m:.4f}",
            self.dominant_voltage_segment,
        ]


@dataclass(frozen=True, slots=True)
class CapacitanceResult:
    intrinsic_capacitance_pf: float
    effective_capacitance_pf: float
    background_capacitance_pf: float
    applied_voltage_v: float
    operating_kinematic_viscosity_cst: float
    operating_dynamic_viscosity_pa_s: float
    radial_displacement_um: float
    axial_displacement_um: float
    loaded_ball_count: int
    mean_ball_load_n: float
    max_ball_load_n: float
    min_inner_film_thickness_um: float
    min_outer_film_thickness_um: float
    min_inner_lambda: float
    min_outer_lambda: float
    inner_contact_sum_pf: float
    ceramic_body_sum_pf: float
    outer_contact_sum_pf: float
    mean_inner_voltage_ratio: float
    mean_ceramic_voltage_ratio: float
    mean_outer_voltage_ratio: float
    max_inner_field_mv_m: float
    max_ceramic_equivalent_field_mv_m: float
    max_outer_field_mv_m: float
    dominant_voltage_segment: str
    solver_converged: bool
    details: list[BallCapacitanceDetail]


def astm_d341_kinematic_viscosity_cst(nu_40_cst: float, nu_100_cst: float, temperature_c: float) -> float:
    if nu_40_cst <= 0 or nu_100_cst <= 0:
        raise ValueError("ASTM D341 requires both viscosity inputs to be positive.")

    temperature_k = temperature_c + 273.15
    if temperature_k <= 0:
        raise ValueError("temperature_c must be above absolute zero.")

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


def dominant_segment_name(inner_ratio: float, ceramic_ratio: float, outer_ratio: float) -> str:
    segments = {
        "Inner Oil Film": inner_ratio,
        "Ceramic Ball": ceramic_ratio,
        "Outer Oil Film": outer_ratio,
    }
    return max(segments, key=segments.get)


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
        g = self.geometry
        ratio = g.ball_diameter_mm / g.pitch_diameter_mm
        inner_speed = (math.pi * speed_rpm * g.pitch_diameter_mm / 120.0) * (1.0 - ratio**2) / 1000.0
        outer_speed = (math.pi * speed_rpm * g.pitch_diameter_mm / 120.0) * (1.0 + ratio**2) / 1000.0
        return inner_speed, outer_speed

    def _solve_equilibrium(self, radial_load_n: float, axial_load_n: float, total_stiffness: float) -> tuple[float, float, bool]:
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
                delta_mm = distance_mm - g.groove_span_mm - (g.radial_clearance_mm / 2.0)
                if delta_mm > 0.0:
                    load_n = total_stiffness * delta_mm**1.5
                    force_x += load_n * (term_r / distance_mm) * math.cos(psi)
                    force_z += load_n * (term_a / distance_mm)
            return [force_x - radial_load_n, force_z - axial_load_n]

        guesses = [
            np.array([30.0, 0.0]),
            np.array([80.0, 10.0]),
            np.array([150.0, 40.0]),
        ]
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

    def calculate(self, conditions: OperatingConditions) -> CapacitanceResult:
        conditions.validate()
        self.geometry.validate()
        self.lubricant.validate()

        if conditions.radial_load_n == 0.0 and conditions.axial_load_n == 0.0:
            return CapacitanceResult(
                intrinsic_capacitance_pf=0.0,
                effective_capacitance_pf=self.lubricant.background_capacitance_pf,
                background_capacitance_pf=self.lubricant.background_capacitance_pf,
                applied_voltage_v=conditions.applied_voltage_v,
                operating_kinematic_viscosity_cst=astm_d341_kinematic_viscosity_cst(
                    self.lubricant.viscosity_40_cst,
                    self.lubricant.viscosity_100_cst,
                    conditions.temperature_c,
                ),
                operating_dynamic_viscosity_pa_s=0.0,
                radial_displacement_um=0.0,
                axial_displacement_um=0.0,
                loaded_ball_count=0,
                mean_ball_load_n=0.0,
                max_ball_load_n=0.0,
                min_inner_film_thickness_um=0.0,
                min_outer_film_thickness_um=0.0,
                min_inner_lambda=0.0,
                min_outer_lambda=0.0,
                inner_contact_sum_pf=0.0,
                ceramic_body_sum_pf=0.0,
                outer_contact_sum_pf=0.0,
                mean_inner_voltage_ratio=0.0,
                mean_ceramic_voltage_ratio=0.0,
                mean_outer_voltage_ratio=0.0,
                max_inner_field_mv_m=0.0,
                max_ceramic_equivalent_field_mv_m=0.0,
                max_outer_field_mv_m=0.0,
                dominant_voltage_segment="No loaded path",
                solver_converged=True,
                details=[],
            )

        operating_kinematic_viscosity_cst = astm_d341_kinematic_viscosity_cst(
            self.lubricant.viscosity_40_cst,
            self.lubricant.viscosity_100_cst,
            conditions.temperature_c,
        )
        operating_density = self.lubricant.density_at(conditions.temperature_c, 0.0)
        operating_dynamic_viscosity_pa_s = dynamic_viscosity_from_kinematic_cst(
            operating_kinematic_viscosity_cst,
            operating_density,
        )

        inner_stiffness, inner_ellipticity, inner_sum_rho, inner_e_val, inner_rx_mm = self._contact_stiffness(
            is_inner=True
        )
        outer_stiffness, outer_ellipticity, outer_sum_rho, outer_e_val, outer_rx_mm = self._contact_stiffness(
            is_inner=False
        )
        total_stiffness = 1.0 / (((1.0 / inner_stiffness) ** (2.0 / 3.0) + (1.0 / outer_stiffness) ** (2.0 / 3.0)) ** 1.5)
        radial_um, axial_um, solver_converged = self._solve_equilibrium(
            conditions.radial_load_n,
            conditions.axial_load_n,
            total_stiffness,
        )

        entrainment_inner_m_s, entrainment_outer_m_s = self._entrainment_speeds(conditions.speed_rpm)
        inner_rx_m = inner_rx_mm / 1000.0
        outer_rx_m = outer_rx_mm / 1000.0
        angles = np.linspace(0.0, 2.0 * math.pi, self.geometry.rolling_elements, endpoint=False)

        details: list[BallCapacitanceDetail] = []
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
            delta_mm = distance_mm - self.geometry.groove_span_mm - (self.geometry.radial_clearance_mm / 2.0)
            if delta_mm <= 0.0:
                details.append(
                    BallCapacitanceDetail(
                        angle_deg=math.degrees(psi),
                        load_n=0.0,
                        contact_angle_deg=0.0,
                        inner_hertz_area_mm2=0.0,
                        outer_hertz_area_mm2=0.0,
                        inner_film_thickness_um=0.0,
                        outer_film_thickness_um=0.0,
                        inner_contact_capacitance_pf=0.0,
                        ceramic_body_capacitance_pf=0.0,
                        outer_contact_capacitance_pf=0.0,
                        series_capacitance_pf=0.0,
                        inner_mean_pressure_mpa=0.0,
                        outer_mean_pressure_mpa=0.0,
                        inner_relative_permittivity=0.0,
                        outer_relative_permittivity=0.0,
                        inner_lambda=0.0,
                        outer_lambda=0.0,
                        inner_voltage_ratio=0.0,
                        ceramic_voltage_ratio=0.0,
                        outer_voltage_ratio=0.0,
                        inner_voltage_v=0.0,
                        ceramic_voltage_v=0.0,
                        outer_voltage_v=0.0,
                        inner_field_mv_m=0.0,
                        ceramic_equivalent_thickness_um=0.0,
                        ceramic_equivalent_field_mv_m=0.0,
                        outer_field_mv_m=0.0,
                        dominant_voltage_segment="Inactive",
                    )
                )
                continue

            load_n = total_stiffness * delta_mm**1.5
            contact_angle_deg = math.degrees(math.asin(term_a / distance_mm)) if distance_mm > 0 else 0.0

            inner_area_mm2, _, _, inner_pressure_mpa = self._hertz_contact(
                load_n,
                inner_sum_rho,
                inner_ellipticity,
                inner_e_val,
            )
            outer_area_mm2, _, _, outer_pressure_mpa = self._hertz_contact(
                load_n,
                outer_sum_rho,
                outer_ellipticity,
                outer_e_val,
            )

            inner_film_mm = self._central_film_thickness_mm(
                load_n,
                inner_rx_m,
                entrainment_inner_m_s,
                inner_ellipticity,
                operating_dynamic_viscosity_pa_s,
            )
            outer_film_mm = self._central_film_thickness_mm(
                load_n,
                outer_rx_m,
                entrainment_outer_m_s,
                outer_ellipticity,
                operating_dynamic_viscosity_pa_s,
            )

            inner_area_m2 = inner_area_mm2 * 1e-6
            outer_area_m2 = outer_area_mm2 * 1e-6
            inner_film_m = inner_film_mm * 1e-3
            outer_film_m = outer_film_mm * 1e-3

            inner_eps_r = self.lubricant.relative_permittivity(conditions.temperature_c, inner_pressure_mpa * 1e6)
            outer_eps_r = self.lubricant.relative_permittivity(conditions.temperature_c, outer_pressure_mpa * 1e6)

            inner_cap_pf = EPSILON_0 * inner_eps_r * inner_area_m2 / max(inner_film_m, 1e-12) * 1e12
            outer_cap_pf = EPSILON_0 * outer_eps_r * outer_area_m2 / max(outer_film_m, 1e-12) * 1e12
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
            series_cap_pf = 0.0 if inverse_series in {0.0, math.inf} else 1.0 / inverse_series

            inner_lambda = (inner_film_mm * 1000.0) / self.geometry.composite_roughness_um
            outer_lambda = (outer_film_mm * 1000.0) / self.geometry.composite_roughness_um
            inner_voltage_ratio = 0.0 if inner_cap_pf <= 0.0 else series_cap_pf / inner_cap_pf
            ceramic_voltage_ratio = 0.0 if ceramic_cap_pf <= 0.0 else series_cap_pf / ceramic_cap_pf
            outer_voltage_ratio = 0.0 if outer_cap_pf <= 0.0 else series_cap_pf / outer_cap_pf

            inner_voltage_v = conditions.applied_voltage_v * inner_voltage_ratio
            ceramic_voltage_v = conditions.applied_voltage_v * ceramic_voltage_ratio
            outer_voltage_v = conditions.applied_voltage_v * outer_voltage_ratio

            inner_field_mv_m = 0.0 if inner_film_m <= 0.0 else inner_voltage_v / inner_film_m / 1e6
            outer_field_mv_m = 0.0 if outer_film_m <= 0.0 else outer_voltage_v / outer_film_m / 1e6
            ceramic_equivalent_thickness_m = 0.0
            if effective_area_m2 > 0.0 and ceramic_cap_pf > 0.0:
                ceramic_equivalent_thickness_m = (
                    EPSILON_0 * self.geometry.ceramic_relative_permittivity * effective_area_m2 / (ceramic_cap_pf * 1e-12)
                )
            ceramic_equivalent_field_mv_m = (
                0.0 if ceramic_equivalent_thickness_m <= 0.0 else ceramic_voltage_v / ceramic_equivalent_thickness_m / 1e6
            )
            dominant_voltage_segment = dominant_segment_name(
                inner_voltage_ratio,
                ceramic_voltage_ratio,
                outer_voltage_ratio,
            )

            intrinsic_total_pf += series_cap_pf
            inner_sum_pf += inner_cap_pf
            ceramic_sum_pf += ceramic_cap_pf
            outer_sum_pf += outer_cap_pf

            details.append(
                BallCapacitanceDetail(
                    angle_deg=math.degrees(psi),
                    load_n=load_n,
                    contact_angle_deg=contact_angle_deg,
                    inner_hertz_area_mm2=inner_area_mm2,
                    outer_hertz_area_mm2=outer_area_mm2,
                    inner_film_thickness_um=inner_film_mm * 1000.0,
                    outer_film_thickness_um=outer_film_mm * 1000.0,
                    inner_contact_capacitance_pf=inner_cap_pf,
                    ceramic_body_capacitance_pf=ceramic_cap_pf,
                    outer_contact_capacitance_pf=outer_cap_pf,
                    series_capacitance_pf=series_cap_pf,
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
                    dominant_voltage_segment=dominant_voltage_segment,
                )
            )

        active_details = [detail for detail in details if detail.load_n > 0.0]
        effective_total_pf = intrinsic_total_pf + self.lubricant.background_capacitance_pf
        mean_inner_voltage_ratio = (
            sum(detail.inner_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        mean_ceramic_voltage_ratio = (
            sum(detail.ceramic_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        mean_outer_voltage_ratio = (
            sum(detail.outer_voltage_ratio for detail in active_details) / len(active_details) if active_details else 0.0
        )
        dominant_voltage_segment = dominant_segment_name(
            mean_inner_voltage_ratio,
            mean_ceramic_voltage_ratio,
            mean_outer_voltage_ratio,
        ) if active_details else "No loaded path"

        return CapacitanceResult(
            intrinsic_capacitance_pf=intrinsic_total_pf,
            effective_capacitance_pf=effective_total_pf,
            background_capacitance_pf=self.lubricant.background_capacitance_pf,
            applied_voltage_v=conditions.applied_voltage_v,
            operating_kinematic_viscosity_cst=operating_kinematic_viscosity_cst,
            operating_dynamic_viscosity_pa_s=operating_dynamic_viscosity_pa_s,
            radial_displacement_um=radial_um,
            axial_displacement_um=axial_um,
            loaded_ball_count=len(active_details),
            mean_ball_load_n=sum(detail.load_n for detail in active_details) / len(active_details) if active_details else 0.0,
            max_ball_load_n=max((detail.load_n for detail in active_details), default=0.0),
            min_inner_film_thickness_um=min((detail.inner_film_thickness_um for detail in active_details), default=0.0),
            min_outer_film_thickness_um=min((detail.outer_film_thickness_um for detail in active_details), default=0.0),
            min_inner_lambda=min((detail.inner_lambda for detail in active_details), default=0.0),
            min_outer_lambda=min((detail.outer_lambda for detail in active_details), default=0.0),
            inner_contact_sum_pf=inner_sum_pf,
            ceramic_body_sum_pf=ceramic_sum_pf,
            outer_contact_sum_pf=outer_sum_pf,
            mean_inner_voltage_ratio=mean_inner_voltage_ratio,
            mean_ceramic_voltage_ratio=mean_ceramic_voltage_ratio,
            mean_outer_voltage_ratio=mean_outer_voltage_ratio,
            max_inner_field_mv_m=max((detail.inner_field_mv_m for detail in active_details), default=0.0),
            max_ceramic_equivalent_field_mv_m=max(
                (detail.ceramic_equivalent_field_mv_m for detail in active_details),
                default=0.0,
            ),
            max_outer_field_mv_m=max((detail.outer_field_mv_m for detail in active_details), default=0.0),
            dominant_voltage_segment=dominant_voltage_segment,
            solver_converged=solver_converged,
            details=details,
        )
