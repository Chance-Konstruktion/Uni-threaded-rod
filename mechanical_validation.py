import math
from dataclasses import dataclass

from .database import THREAD_STANDARDS


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class StressResult:
    stress_mpa: float
    safety_factor: float


def validate_thread_input(diameter, pitch, length, starts, clearance=0.0):
    """Basis-Parametervalidierung für Geometrie- und Engineering-Checks."""
    if diameter <= 0.0:
        return ValidationResult(False, "Ungültig: Durchmesser muss > 0 sein.")
    if pitch <= 0.0:
        return ValidationResult(False, "Ungültig: Steigung muss > 0 sein.")
    if length <= 0.0:
        return ValidationResult(False, "Ungültig: Länge muss > 0 sein.")
    if starts < 1:
        return ValidationResult(False, "Ungültig: Gängigkeit muss mindestens 1 sein.")
    if starts > 16:
        return ValidationResult(False, "Ungültig: Gängigkeit ist zu hoch (maximal 16).")
    if clearance < 0.0:
        return ValidationResult(False, "Ungültig: Spiel (Clearance) muss >= 0 sein.")
    if pitch > diameter:
        return ValidationResult(False, "Ungültig: Steigung darf nicht größer als Durchmesser sein.")

    d3 = diameter - 1.6 * pitch
    if d3 <= 0.0 or d3 < 0.2 * diameter:
        return ValidationResult(False, "Ungültig: Kerndurchmesser wäre kritisch klein (Self-Intersection-Risiko).")

    return ValidationResult(True, "")


def check_nut_fit(bolt_major_diameter, nut_minor_diameter, radial_clearance=0.0):
    """Prüft, ob Mutter geometrisch über das Außengewinde passt."""
    if radial_clearance < 0:
        raise ValueError("Radiales Spiel muss >= 0 sein")
    required_minor = bolt_major_diameter + 2.0 * radial_clearance
    interference = required_minor - nut_minor_diameter
    return {
        "fits": interference <= 0.0,
        "required_minor_diameter": required_minor,
        "interference_mm": max(interference, 0.0),
    }


def check_pitch_match(bolt_pitch, nut_pitch, tolerance_mm=1e-6):
    """Prüft Steigungsübereinstimmung zwischen Schraube und Mutter."""
    if tolerance_mm < 0.0:
        raise ValueError("Pitch-Toleranz muss >= 0 sein")
    delta = abs(bolt_pitch - nut_pitch)
    return {
        "matches": delta <= tolerance_mm,
        "delta_mm": delta,
    }


def calculate_tensile_stress(force_n, stress_area_mm2):
    """Zugspannung in MPa (N/mm²)."""
    if stress_area_mm2 <= 0.0:
        raise ValueError("Spannungsquerschnitt muss > 0 sein")
    return force_n / stress_area_mm2


def calculate_shear_stress(force_n, shear_area_mm2):
    """Schubspannung in MPa (N/mm²)."""
    if shear_area_mm2 <= 0.0:
        raise ValueError("Scherfläche muss > 0 sein")
    return force_n / shear_area_mm2


def calculate_safety_factor(allowable_stress_mpa, actual_stress_mpa):
    if allowable_stress_mpa <= 0.0:
        raise ValueError("Zulässige Spannung muss > 0 sein")
    if actual_stress_mpa <= 0.0:
        raise ValueError("Ist-Spannung muss > 0 sein")
    return allowable_stress_mpa / actual_stress_mpa


def estimate_tensile_stress_area(diameter, pitch):
    """Näherung für metrische Gewinde nach As ~= π/4*(d-0.9382P)^2 in mm²."""
    d_eff = diameter - 0.9382 * pitch
    if d_eff <= 0:
        raise ValueError("Effektivdurchmesser <= 0")
    return math.pi * 0.25 * d_eff * d_eff


def estimate_thread_shear_area(pitch_diameter, engagement_length):
    """Einfache Scherflächen-Näherung der tragenden Flanke (mm²)."""
    if pitch_diameter <= 0.0 or engagement_length <= 0.0:
        raise ValueError("Mitteldurchmesser und Eingriffslänge müssen > 0 sein")
    return math.pi * pitch_diameter * engagement_length * 0.5


def validate_mechanical_load_case(force_n, allowable_tensile_mpa, allowable_shear_mpa, diameter, pitch, engagement_length):
    """Mechanische Validierung: Zug/Scherung + Sicherheitsfaktor (vereinfachte Näherung)."""
    tensile_area = estimate_tensile_stress_area(diameter, pitch)
    pitch_diameter = diameter - 0.649519 * pitch
    shear_area = estimate_thread_shear_area(pitch_diameter, engagement_length)

    sigma_t = calculate_tensile_stress(force_n, tensile_area)
    tau = calculate_shear_stress(force_n, shear_area)

    sf_tensile = calculate_safety_factor(allowable_tensile_mpa, sigma_t)
    sf_shear = calculate_safety_factor(allowable_shear_mpa, tau)

    return {
        "tensile": StressResult(stress_mpa=sigma_t, safety_factor=sf_tensile),
        "shear": StressResult(stress_mpa=tau, safety_factor=sf_shear),
        "min_safety_factor": min(sf_tensile, sf_shear),
    }


def resolve_standard_pitch_diameter(standard_key, diameter, pitch):
    """Hilfsfunktion für konsistente mechanische Checks pro Standard."""
    if standard_key not in THREAD_STANDARDS:
        raise ValueError(f"Unbekannter Standard: {standard_key}")
    std = THREAD_STANDARDS[standard_key]
    return std["d2_formula"](diameter, pitch)


def fem_placeholder_note():
    return "FEM optional: nicht Teil dieses Moduls, Export in externen Solver vorgesehen."
