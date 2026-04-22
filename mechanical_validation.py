import math
from dataclasses import dataclass

from .database import ISO_965_TOLERANCE_RADIAL_OFFSETS, THREAD_STANDARDS, resolve_iso_metric_coarse_row


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class StressResult:
    stress_mpa: float
    safety_factor: float


ISO_898_PROPERTY_CLASS_RM_MPA = {
    "4.6": 400.0,
    "5.8": 500.0,
    "8.8": 800.0,
    "10.9": 1000.0,
    "12.9": 1200.0,
}


ISO_METRIC_NORM_REFERENCES = {
    "METRIC_ISO": "ISO 68-1",
    "METRIC_FINE": "ISO 965-1",
}


def _resolve_core_diameter(standard_key, diameter, pitch):
    std = THREAD_STANDARDS.get(standard_key)
    if std:
        return std["d3_formula"](diameter, pitch)
    # Fallback: konservative V-Gewinde-Näherung.
    return diameter - 1.226869 * pitch


def validate_thread_input(diameter, pitch, length, starts, clearance=0.0, standard_key="METRIC_ISO"):
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
    if length > 1000.0 * diameter:
        return ValidationResult(False, "Ungültig: Länge ist im Verhältnis zum Durchmesser extrem hoch.")
    if pitch < 1e-4:
        return ValidationResult(False, "Ungültig: Steigung ist numerisch zu klein.")

    d3 = _resolve_core_diameter(standard_key, diameter, pitch)
    if d3 <= 0.0 or d3 < 0.2 * diameter:
        return ValidationResult(False, "Ungültig: Kerndurchmesser wäre kritisch klein (Self-Intersection-Risiko).")

    return ValidationResult(True, "")


def validate_norm_binding(standard_key, tolerance_class, internal=False):
    """Sichert die Normbindung (inkl. Toleranzklasse) für den gewählten Standard."""
    std = THREAD_STANDARDS.get(standard_key)
    if not std:
        return ValidationResult(False, f"Unbekannter Standard: {standard_key}")

    norm_ref = ISO_METRIC_NORM_REFERENCES.get(standard_key, std.get("standard", "n/a"))
    if standard_key in ISO_METRIC_NORM_REFERENCES and "ISO" not in str(norm_ref).upper():
        return ValidationResult(False, f"Normreferenz für {standard_key} fehlt oder ist ungültig.")

    tc = str(tolerance_class or "").strip()
    if not tc:
        return ValidationResult(False, "Toleranzklasse muss gesetzt sein.")

    # Präzisierter Standardfall: metrische Regelgewinde vorrangig als 6g/6H-Paarung.
    if standard_key in ISO_METRIC_NORM_REFERENCES and tc.upper() in {"6G", "6H"}:
        if internal and tc.upper() != "6H":
            return ValidationResult(False, "Toleranzklasse nicht zulässig: Für Innengewinde wird in diesem Profil 6H erwartet.")
        if not internal and tc.upper() != "6G":
            return ValidationResult(False, "Toleranzklasse nicht zulässig: Für Außengewinde wird in diesem Profil 6g erwartet.")

    classes = std.get("tolerance_classes", {})
    key = "internal" if internal else "external"
    allowed = {str(v).upper() for v in classes.get(key, [])}
    if allowed and tc.upper() not in allowed:
        return ValidationResult(
            False,
            f"Toleranzklasse {tolerance_class} ist für {standard_key}/{key} nicht zulässig (Norm {norm_ref}).",
        )

    return ValidationResult(True, f"{standard_key} mit Normbezug {norm_ref} und Klasse {tc} ist konsistent.")


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


def estimate_core_area_from_standard(standard_key, diameter, pitch):
    """Kernquerschnitt auf Basis des Kerndurchmessers d3 (mm²)."""
    d3 = _resolve_core_diameter(standard_key, diameter, pitch)
    if d3 <= 0.0:
        raise ValueError("Kerndurchmesser <= 0")
    return math.pi * 0.25 * d3 * d3


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


def validate_thread_engagement_strength(
    force_n,
    standard_key,
    diameter,
    pitch,
    engagement_length,
    nut_allowable_shear_mpa=120.0,
    bolt_allowable_shear_mpa=240.0,
):
    """Vereinfachter Tragfähigkeitscheck der Gewindeflanken (Abstreif-/Scher-Nachweis)."""
    if force_n <= 0.0:
        raise ValueError("Kraft muss > 0 sein")
    if engagement_length <= 0.0:
        raise ValueError("Eingriffslänge muss > 0 sein")

    pitch_diameter = resolve_standard_pitch_diameter(standard_key, diameter, pitch)
    shear_area = estimate_thread_shear_area(pitch_diameter, engagement_length)
    tau = calculate_shear_stress(force_n, shear_area)

    sf_nut = calculate_safety_factor(nut_allowable_shear_mpa, tau)
    sf_bolt = calculate_safety_factor(bolt_allowable_shear_mpa, tau)
    return {
        "shear_stress_mpa": tau,
        "nut_safety_factor": sf_nut,
        "bolt_safety_factor": sf_bolt,
        "min_safety_factor": min(sf_nut, sf_bolt),
        "passes": min(sf_nut, sf_bolt) >= 1.0,
    }


def collect_validation_warnings(diameter, pitch, length, engagement_length=None):
    """Nicht-blockierende Hinweise für physikalisch kritische Parameterkombinationen."""
    warnings = []
    slenderness = length / diameter if diameter > 0 else float("inf")
    if slenderness > 25.0:
        warnings.append("Hoher Schlankheitsgrad: Knicknachweis empfohlen.")
    if pitch / diameter > 0.2:
        warnings.append("Sehr große Steigung relativ zu d: Traganteil pro Gang reduziert.")
    if engagement_length is not None and engagement_length < diameter:
        warnings.append("Kurze Eingriffslänge: Abstreif-/Scherprüfung der Mutterflanken empfohlen.")
    return warnings


def get_iso965_tolerance_offset_info(diameter, pitch):
    """Liefert hinterlegte 6g/6H-Radialoffsets für Normpaarung, falls verfügbar."""
    row = resolve_iso_metric_coarse_row(diameter, pitch)
    if row:
        return ISO_965_TOLERANCE_RADIAL_OFFSETS.get((row["diameter"], row["pitch"]))
    return ISO_965_TOLERANCE_RADIAL_OFFSETS.get((diameter, pitch))


def validate_property_class_tensile(
    force_n,
    standard_key,
    diameter,
    pitch,
    property_class="8.8",
    required_safety_factor=1.5,
):
    """ISO-898-nahe Zugprüfung über Kernquerschnitt und Materialklasse."""
    if required_safety_factor <= 0.0:
        raise ValueError("Erforderlicher Sicherheitsfaktor muss > 0 sein")
    if property_class not in ISO_898_PROPERTY_CLASS_RM_MPA:
        raise ValueError(f"Unbekannte Festigkeitsklasse: {property_class}")

    core_area = estimate_core_area_from_standard(standard_key, diameter, pitch)
    stress = calculate_tensile_stress(force_n, core_area)
    rm = ISO_898_PROPERTY_CLASS_RM_MPA[property_class]
    allowable = rm / required_safety_factor
    sf = calculate_safety_factor(allowable, stress)
    return {
        "property_class": property_class,
        "core_area_mm2": core_area,
        "stress_mpa": stress,
        "allowable_mpa": allowable,
        "safety_factor": sf,
        "passes": sf >= 1.0,
    }


def euler_buckling_critical_load(e_modulus_mpa, inertia_mm4, unsupported_length_mm, k_factor=1.0):
    """Euler-Knicklast in N (vereinfachtes Stabmodell, MPa-mm-Einheitensystem)."""
    if e_modulus_mpa <= 0.0:
        raise ValueError("E-Modul muss > 0 sein")
    if inertia_mm4 <= 0.0:
        raise ValueError("Flächenträgheitsmoment muss > 0 sein")
    if unsupported_length_mm <= 0.0:
        raise ValueError("Knicklänge muss > 0 sein")
    if k_factor <= 0.0:
        raise ValueError("K-Faktor muss > 0 sein")
    effective_length = k_factor * unsupported_length_mm
    return (math.pi ** 2) * e_modulus_mpa * inertia_mm4 / (effective_length ** 2)


def validate_buckling(force_n, core_diameter_mm, unsupported_length_mm, e_modulus_mpa=210000.0, k_factor=1.0):
    """Knickprüfung auf Basis des Kerndurchmessers (vollrunder Querschnitt)."""
    if core_diameter_mm <= 0.0:
        raise ValueError("Kerndurchmesser muss > 0 sein")
    radius = core_diameter_mm * 0.5
    inertia = math.pi * (radius ** 4) / 4.0
    critical = euler_buckling_critical_load(e_modulus_mpa, inertia, unsupported_length_mm, k_factor=k_factor)
    if force_n <= 0.0:
        raise ValueError("Kraft muss > 0 sein")
    sf = critical / force_n
    return {
        "critical_load_n": critical,
        "applied_load_n": force_n,
        "safety_factor": sf,
        "passes": sf >= 1.0,
    }


def resolve_standard_pitch_diameter(standard_key, diameter, pitch):
    """Hilfsfunktion für konsistente mechanische Checks pro Standard."""
    if standard_key not in THREAD_STANDARDS:
        raise ValueError(f"Unbekannter Standard: {standard_key}")
    std = THREAD_STANDARDS[standard_key]
    return std["d2_formula"](diameter, pitch)


def fem_placeholder_note():
    return "FEM optional: nicht Teil dieses Moduls, Export in externen Solver vorgesehen."
