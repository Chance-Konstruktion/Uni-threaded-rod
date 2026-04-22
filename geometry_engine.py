import math
from dataclasses import dataclass

from .database import (
    ISO_965_TOLERANCE_RADIAL_OFFSETS,
    THREAD_STANDARDS,
    resolve_iso_metric_coarse_row,
)


@dataclass(frozen=True)
class ProfilePoint:
    """2D-Profilpunkt (x=radial, y=axial).

    Eigenes Datenobjekt statt mathutils.Vector, damit Profilberechnung und
    Regressionstests auch außerhalb von Blender-Interpreter laufen können.
    """

    x: float
    y: float


def _safe_ratio(value, default):
    """Akzeptiert numerische Werte oder einfache P-Ausdrücke (z. B. 'P/8')."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().upper().replace(" ", "")
    if text == "P":
        return 1.0
    if text.startswith("P/"):
        try:
            return 1.0 / float(text[2:])
        except ValueError:
            return default
    if text.endswith("*P"):
        try:
            return float(text[:-2])
        except ValueError:
            return default
    if "*P/" in text:
        try:
            num, den = text.split("*P/")
            return float(num) / float(den)
        except ValueError:
            return default
    return default


def _tolerance_offset_mm(tolerance_class, standard_key=None, diameter=None, pitch=None, internal=False):
    """Grobe radiale Toleranzverschiebung in mm (positiv = größer, negativ = kleiner)."""
    if not tolerance_class:
        return 0.0

    tc = str(tolerance_class).strip().upper()
    if standard_key in {"METRIC_ISO", "METRIC_FINE"} and tc in {"6G", "6H"} and diameter and pitch:
        row = resolve_iso_metric_coarse_row(diameter, pitch)
        key = (row["diameter"], row["pitch"]) if row else (diameter, pitch)
        table_entry = ISO_965_TOLERANCE_RADIAL_OFFSETS.get(key)
        if table_entry:
            if tc == "6G" and not internal:
                return table_entry["6g_external"]
            if tc == "6H" and internal:
                return table_entry["6H_internal"]

    tolerance_map = {
        "4G": -0.02,
        "6G": -0.01,
        "8G": -0.04,
        "4H": 0.00,
        "5H": 0.01,
        "6H": 0.02,
        "7H": 0.03,
        "1A": -0.05,
        "2A": -0.03,
        "3A": -0.01,
        "1B": 0.01,
        "2B": 0.02,
        "3B": 0.03,
    }
    return tolerance_map.get(tc, 0.0)


def _validate_profile_inputs(standard_key, diameter, pitch, tolerance_class, clearance):
    if standard_key not in THREAD_STANDARDS:
        raise ValueError(f"Unbekannter Standard: {standard_key}")
    if diameter <= 0:
        raise ValueError("Durchmesser muss > 0 sein")
    if pitch <= 0:
        raise ValueError("Steigung (Pitch) muss > 0 sein")
    if clearance < 0:
        raise ValueError("Spiel (Clearance) muss >= 0 sein")

    std = THREAD_STANDARDS[standard_key]
    d3 = std["d3_formula"](diameter, pitch)
    if d3 <= 0:
        raise ValueError(
            f"Ungültige Geometrie: Kerndurchmesser <= 0 (d={diameter}, p={pitch}, d3={d3:.6g})"
        )

    tc = str(tolerance_class or "").strip()
    tolerance_def = std.get("tolerance_classes")
    if tc and tolerance_def:
        allowed = set()
        for values in tolerance_def.values():
            allowed.update(str(v).upper() for v in values)
        # Rückwärtskompatibel: viele Aufrufer verlassen sich auf den Default "6g",
        # auch bei Normfamilien ohne 6g-Klasse in dieser vereinfachten Datenbank.
        if tc.upper() not in allowed and tc.upper() != "6G":
            raise ValueError(
                f"Toleranzklasse {tolerance_class} ist für {standard_key} nicht definiert"
            )


def generate_profile(standard_key, diameter, pitch, tolerance_class="6g", internal=False, clearance=0.0):
    """Erzeugt 2D-Profilpunkte eines Gewindegangs (x=radial, y=axial)."""
    _validate_profile_inputs(standard_key, diameter, pitch, tolerance_class, clearance)
    std = THREAD_STANDARDS[standard_key]
    profile_type = std["profile_type"]

    d2 = std["d2_formula"](diameter, pitch)
    d3 = std["d3_formula"](diameter, pitch)
    r = diameter / 2.0
    r2 = d2 / 2.0
    r3 = d3 / 2.0

    tol_offset = _tolerance_offset_mm(
        tolerance_class,
        standard_key=standard_key,
        diameter=diameter,
        pitch=pitch,
        internal=internal,
    )
    offset = (clearance / 2.0 + tol_offset) if internal else (-clearance / 2.0 + tol_offset)
    r += offset
    r2 += offset
    r3 += offset

    if profile_type == "V":
        h = r - r3
        sp = std.get("special_params", {})
        if standard_key.startswith("METRIC"):
            crest_flat = pitch * _safe_ratio(sp.get("crest_flat"), 1.0 / 8.0)
            root_flat = pitch * _safe_ratio(sp.get("root_flat"), 1.0 / 4.0)
        elif standard_key in {"UNC", "UNF"}:
            crest_flat = pitch * _safe_ratio(sp.get("crest_flat"), 1.0 / 8.0)
            root_flat = pitch * _safe_ratio(sp.get("root_flat"), 1.0 / 8.0)
        elif standard_key.startswith("WHITWORTH") or standard_key in {"PIPE_G"}:
            # Vereinfachte Rundungs-Ersatzgeometrie: kürzere Flats bei 55°-Profilen.
            crest_flat = pitch * _safe_ratio(sp.get("crest_flat"), 1.0 / 12.0)
            root_flat = pitch * _safe_ratio(sp.get("root_flat"), 1.0 / 6.0)
        else:
            crest_flat = pitch * _safe_ratio(sp.get("crest_flat"), 0.05)
            root_flat = pitch * _safe_ratio(sp.get("root_flat"), 0.10)

        crest_flat = max(0.0, min(crest_flat, pitch * 0.45))
        root_flat = max(0.0, min(root_flat, pitch * 0.45))

        y_crest = crest_flat / 2.0
        y_root = pitch / 2.0 - root_flat / 2.0
        pts = [
            ProfilePoint(r, 0.0),
            ProfilePoint(r - h + root_flat * 0.5, y_root),
            ProfilePoint(r3, pitch / 2.0),
            ProfilePoint(r - h + root_flat * 0.5, pitch - y_root),
            ProfilePoint(r, pitch - y_crest),
            ProfilePoint(r, pitch),
        ]

    elif profile_type == "TRAPEZOID":
        crest_width = 0.5 * pitch
        root_width = max(0.25, 0.5 * pitch - 0.25)
        y_crest = crest_width / 2.0
        y_root = pitch / 2.0 - root_width / 2.0
        pts = [
            ProfilePoint(r, 0.0),
            ProfilePoint(r, y_crest),
            ProfilePoint(r3, y_root),
            ProfilePoint(r3, y_root + root_width),
            ProfilePoint(r, pitch - y_crest),
            ProfilePoint(r, pitch),
        ]

    elif profile_type == "ROUND":
        radius = pitch / 4.0
        steps = 14
        pts = []
        for i in range(steps + 1):
            ang = math.pi * i / steps
            pts.append(ProfilePoint(r - radius + radius * math.cos(ang), radius * math.sin(ang)))
        for i in range(1, steps + 1):
            ang = math.pi * i / steps
            pts.append(ProfilePoint(r3 + radius - radius * math.cos(ang), pitch / 2.0 + radius * math.sin(ang)))
        pts.extend(ProfilePoint(p.x, pitch - p.y) for p in reversed(pts[:-1]))

    elif profile_type == "BUTTRESS":
        h = r - r3
        dx_clear = h * math.tan(math.radians(std.get("special_params", {}).get("clearance_flank", 3.0)))
        dx_press = h * math.tan(math.radians(std.get("special_params", {}).get("pressure_flank", 30.0)))
        crest_width = 0.2 * pitch
        root_width = 0.2 * pitch
        pts = [
            ProfilePoint(r, 0.0),
            ProfilePoint(r, crest_width),
            ProfilePoint(r - dx_press, pitch / 2.0 - root_width / 2.0),
            ProfilePoint(r3, pitch / 2.0),
            ProfilePoint(r3 + dx_clear, pitch / 2.0 + root_width / 2.0),
            ProfilePoint(r, pitch - crest_width),
            ProfilePoint(r, pitch),
        ]

    elif profile_type == "GOTHIC":
        sp = std.get("special_params", {})
        ball_radius = pitch * _safe_ratio(sp.get("ball_radius_ratio"), 0.60)
        contact_angle = math.radians(std.get("special_params", {}).get("contact_angle", 45.0))
        center_offset = ball_radius * _safe_ratio(sp.get("center_offset_ratio"), math.sin(contact_angle))
        steps = 16
        pts = []

        center_a = ProfilePoint(r2 - ball_radius, pitch / 2.0 - center_offset)
        for i in range(steps + 1):
            ang = -math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(ProfilePoint(center_a.x + ball_radius * math.cos(ang), center_a.y + ball_radius * math.sin(ang)))

        center_b = ProfilePoint(r2 - ball_radius, pitch / 2.0 + center_offset)
        for i in range(1, steps + 1):
            ang = math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(ProfilePoint(center_b.x + ball_radius * math.cos(ang), center_b.y + ball_radius * math.sin(ang)))

        # Normnähere KGT-Ausprägung: Abschluss sauber an Crest-Radius anbinden.
        pts.append(ProfilePoint(r, pitch))

    else:
        pts = [ProfilePoint(r, 0.0), ProfilePoint(r3, pitch / 2.0), ProfilePoint(r, pitch)]

    return pts
