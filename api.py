from .database import MATERIAL_PRESETS, THREAD_STANDARDS, get_default_tolerance_class, resolve_thread_parameters
from .geometry_engine import generate_profile
from .mechanical_validation import (
    ISO_898_PROPERTY_CLASS_RM_MPA,
    allowables_from_property_class,
    validate_combined_load_case,
)


def _split_fit(fit: str, internal: bool) -> str:
    if "/" in fit:
        ext, intl = fit.split("/", 1)
        return intl.strip() if internal else ext.strip()
    return fit.strip()


def _resolve_property_class(material_or_preset):
    token = str(material_or_preset).strip()
    if token in ISO_898_PROPERTY_CLASS_RM_MPA:
        return token

    if token in MATERIAL_PRESETS:
        _, _, suffix = token.partition("_")
        if suffix in ISO_898_PROPERTY_CLASS_RM_MPA:
            return suffix

    allowed = sorted(ISO_898_PROPERTY_CLASS_RM_MPA)
    allowed.extend(sorted(key for key in MATERIAL_PRESETS if key.partition("_")[2] in ISO_898_PROPERTY_CLASS_RM_MPA))
    raise ValueError(f"Unbekannte Festigkeitsklasse oder Materialvorgabe: {token}. Erlaubt: {', '.join(allowed)}")


def _resolve_tolerance_class(standard_key, fit, internal):
    tolerance_class = _split_fit(fit, internal=internal)
    if fit == "6g/6H":
        # Default-Fit: an die tatsächlich für die Norm definierten Klassen
        # anpassen. Viele Nicht-ISO-Normen (TRAPEZOIDAL, ACME, STUB_ACME,
        # WHITWORTH_BSW, BSF, PIPE_G) führen nur externe Toleranzklassen; für
        # die interne Sleeve-Nutzung muss dann auf eine definierte Klasse
        # zurückgefallen werden, statt "6H" durchzureichen und an der
        # Profil-Validierung zu scheitern.
        classes = THREAD_STANDARDS.get(standard_key, {}).get("tolerance_classes", {})
        key = "internal" if internal else "external"
        allowed = {str(value).upper() for value in classes.get(key, [])}
        if tolerance_class.upper() not in allowed:
            return get_default_tolerance_class(standard_key, internal=internal)
    return tolerance_class


def _resolve_spec(standard, spec):
    """Löst eine Nenngrößen-Eingabe robust gegen Norm-Tokens auf.

    Die Tokens der Normen-Datenbank sind case-sensitiv und teils mit ``M``/``Pg``
    o.ä. präfigiert (z. B. ``"Pg7"``, ``"M8x1"``, ``"M12x1.5"``). Frühere Versionen
    haben den Spec pauschal großgeschrieben und ein führendes ``M`` abgeschnitten;
    dadurch waren genau diese Normen über die High-Level-API (und damit im
    Schwesterprojekt Uni-threaded-sleeve) nicht auflösbar. Wir probieren deshalb
    den Token unverändert und – nur als Komfort-Fallback für metrische
    Nenngrößen wie ``"M10"`` – zusätzlich ohne führendes ``M``.
    """
    token = str(spec).strip()
    candidates = [token]
    if token[:1] in ("M", "m") and len(token) > 1:
        candidates.append(token[1:])
    last_error = None
    for candidate in candidates:
        try:
            return resolve_thread_parameters(standard, candidate)
        except ValueError as exc:
            last_error = exc
    raise last_error


def thread(spec, fit="6g/6H", material="8.8", length=50.0, standard="METRIC_ISO", internal=False, starts=1):
    """High-level API ähnlich CAD-Aufruf.

    Beispiel:
        thread("M10", fit="6g/6H", material="8.8", length=50)
    """
    token = str(spec).strip()
    diameter, pitch = _resolve_spec(standard, token)
    tolerance_class = _resolve_tolerance_class(standard, fit, internal=internal)

    profile, ratio_warnings = generate_profile(
        standard,
        diameter,
        pitch,
        tolerance_class=tolerance_class,
        internal=internal,
        clearance=0.0,
        return_warnings=True,
    )

    property_class = _resolve_property_class(material)
    allowables = allowables_from_property_class(property_class)
    mechanics = validate_combined_load_case(
        axial_force_n=0.0,
        transverse_force_n=0.0,
        torsion_moment_nmm=0.0,
        diameter=diameter,
        pitch=pitch,
        engagement_length=min(length, max(diameter, pitch * 2.0)),
        allowable_tensile_mpa=allowables["allowable_tensile_mpa"],
        allowable_shear_mpa=allowables["allowable_shear_mpa"],
        standard_key=standard,
    )

    return {
        "standard": standard,
        "spec": token,
        "fit": fit,
        "material": material,
        "property_class": property_class,
        "length_mm": float(length),
        "starts": int(starts),
        "diameter_mm": diameter,
        "pitch_mm": pitch,
        "tolerance_class": tolerance_class,
        "profile_points": profile,
        "ratio_warnings": ratio_warnings,
        "mechanics": mechanics,
    }
