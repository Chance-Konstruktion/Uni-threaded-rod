import ast
import logging
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


def _safe_ratio(value, default, ratio_warnings=None):
    """Akzeptiert numerische Werte oder P-Ausdrücke mit +,-,*,/ (z. B. '0.5*P-0.5')."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)

    expr = str(value).strip().upper().replace(" ", "")
    if not expr:
        return default
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError:
        message = f"Ungültiger Ratio-Ausdruck '{value}'; Default {default} verwendet."
        logging.getLogger(__name__).warning(message)
        if ratio_warnings is not None:
            ratio_warnings.append(message)
        return default

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.BinOp) and type(n.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
            left, right = _eval(n.left), _eval(n.right)
            return {ast.Add: left + right, ast.Sub: left - right, ast.Mult: left * right, ast.Div: left / right}[type(n.op)]
        if isinstance(n, ast.UnaryOp) and type(n.op) in (ast.UAdd, ast.USub):
            val = _eval(n.operand)
            return val if isinstance(n.op, ast.UAdd) else -val
        if isinstance(n, ast.Name) and n.id == "P":
            return 1.0
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        raise ValueError

    try:
        return float(_eval(node))
    except Exception:
        message = f"Ratio-Ausdruck '{value}' konnte nicht ausgewertet werden; Default {default} verwendet."
        logging.getLogger(__name__).warning(message)
        if ratio_warnings is not None:
            ratio_warnings.append(message)
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


def _check_profile_inputs(standard_key, diameter, pitch, tolerance_class, clearance, standard=None):
    if standard is None:
        if standard_key not in THREAD_STANDARDS:
            raise ValueError(f"Unbekannter Standard: {standard_key}")
        standard = THREAD_STANDARDS[standard_key]
    if diameter <= 0:
        raise ValueError("Durchmesser muss > 0 sein")
    if pitch <= 0:
        raise ValueError("Steigung (Pitch) muss > 0 sein")
    if clearance < 0:
        raise ValueError("Spiel (Clearance) muss >= 0 sein")

    std = standard
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
        if tc.upper() not in allowed:
            raise ValueError(
                f"Toleranzklasse {tolerance_class} ist für {standard_key} nicht definiert"
            )


def _validate_external_profile_points(points, major_radius, core_radius, pitch):
    """Harte Schutzschicht für massive Außengewindeprofile.

    Ein Primärprofil für eine Gewindestange muss am Außendurchmesser starten,
    in Richtung Kernradius laufen und am Außendurchmesser enden. Dadurch kann
    der Mesh-Builder das Profil als Material-Außenkontur interpretieren, statt
    versehentlich eine Innengewinde- oder Hohlkörperkontur zu sweepen.
    """
    if len(points) < 3:
        raise ValueError("Außengewindeprofil benötigt mindestens drei Profilpunkte")

    if not all(math.isfinite(p.x) and math.isfinite(p.y) for p in points):
        raise ValueError("Außengewindeprofil enthält nicht-finite Koordinaten")

    if min(p.x for p in points) <= 0.0:
        raise ValueError("Außengewindeprofil enthält radiale Koordinaten <= 0")

    radial_tolerance = max(1e-6, major_radius * 1e-6)
    axial_tolerance = max(1e-6, pitch * 1e-6)
    maximum_radius = max(p.x for p in points)
    minimum_radius = min(p.x for p in points)

    if abs(maximum_radius - major_radius) > radial_tolerance:
        raise ValueError(
            f"Außengewindeprofil erreicht den Major-Radius nicht exakt "
            f"(max={maximum_radius:.6g}, major={major_radius:.6g})"
        )

    if points[0].x < major_radius - radial_tolerance:
        raise ValueError("Außengewindeprofil muss außen am Major-Radius beginnen")

    if points[-1].x < major_radius - radial_tolerance:
        raise ValueError("Außengewindeprofil muss außen am Major-Radius enden")

    core_tolerance = max(radial_tolerance, pitch * 0.007)
    if minimum_radius > core_radius + core_tolerance:
        raise ValueError(
            f"Außengewindeprofil erreicht den Kernradius nicht "
            f"(min={minimum_radius:.6g}, core={core_radius:.6g})"
        )

    if len(points) <= 8 and any(abs(p.x - core_radius) <= core_tolerance for p in points[1:-1]):
        left_shoulder = next(
            (p for p in points[1:-1] if p.x < major_radius - radial_tolerance),
            None,
        )
        right_shoulder = next(
            (p for p in reversed(points[1:-1]) if p.x < major_radius - radial_tolerance),
            None,
        )
        if left_shoulder is not None and right_shoulder is not None:
            left_outside_core = left_shoulder.x > core_radius + core_tolerance
            right_outside_core = right_shoulder.x > core_radius + core_tolerance
            if (left_outside_core != right_outside_core) or (
                left_outside_core
                and right_outside_core
                and abs(left_shoulder.x - right_shoulder.x) <= radial_tolerance
            ):
                raise ValueError(
                    f"Außengewindeprofil setzt Kernradius-Schulterpunkte zu weit außen "
                    f"(left={left_shoulder.x:.6g}, right={right_shoulder.x:.6g}, core={core_radius:.6g})"
                )

    if abs(points[0].y) > axial_tolerance:
        raise ValueError("Außengewindeprofil muss bei y=0 beginnen")

    if abs(points[-1].y - pitch) > axial_tolerance:
        raise ValueError("Außengewindeprofil muss bei y=pitch enden")


def generate_profile(
    standard_key,
    diameter,
    pitch,
    tolerance_class=None,
    internal=False,
    clearance=0.0,
    return_warnings=False,
    standard=None,
):
    """Erzeugt 2D-Profilpunkte eines Gewindegangs (x=radial, y=axial).

    internal=True bleibt für das Schwesterprojekt Uni-threaded-sleeve erhalten.
    """
    _check_profile_inputs(standard_key, diameter, pitch, tolerance_class, clearance, standard=standard)
    ratio_warnings = []
    std = standard if standard is not None else THREAD_STANDARDS[standard_key]
    profile_type = std["profile_type"]

    def ratio(value, default):
        return _safe_ratio(value, default, ratio_warnings)

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
        iso_row = resolve_iso_metric_coarse_row(diameter, pitch) if standard_key.startswith("METRIC") else None

        if standard_key.startswith("METRIC"):
            crest_flat = iso_row["crest_flat"] if iso_row else pitch * ratio(sp.get("crest_flat"), 1.0 / 8.0)
            root_flat = pitch * ratio(sp.get("root_flat"), 1.0 / 4.0)
            root_radius = iso_row["root_radius"] if iso_row else pitch * 0.14434
        elif standard_key in {"UNC", "UNF", "UNEF", "UNS"}:
            crest_flat = pitch * ratio(sp.get("crest_flat"), 1.0 / 8.0)
            root_flat = pitch * ratio(sp.get("root_flat"), 1.0 / 8.0)
            root_radius = 0.0
        elif standard_key.startswith("WHITWORTH") or standard_key == "BSF" or standard_key in {"PIPE_G", "PIPE_R"}:
            # Vereinfachte Rundungs-Ersatzgeometrie: kürzere Flats bei 55°-Profilen.
            crest_flat = pitch * ratio(sp.get("crest_flat"), 1.0 / 12.0)
            root_flat = pitch * ratio(sp.get("root_flat"), 1.0 / 6.0)
            root_radius = pitch * 0.137329
        elif standard_key in {"NPT"}:
            crest_flat = pitch * ratio(sp.get("crest_flat"), 1.0 / 8.0)
            root_flat = pitch * ratio(sp.get("root_flat"), 1.0 / 8.0)
            root_radius = pitch * ratio(sp.get("root_radius"), 0.0714)
        else:
            crest_flat = pitch * ratio(sp.get("crest_flat"), 0.05)
            root_flat = pitch * ratio(sp.get("root_flat"), 0.10)
            root_radius = 0.0

        crest_flat = max(0.0, min(crest_flat, pitch * 0.45))
        root_flat = max(0.0, min(root_flat, pitch * 0.45))

        y_crest = crest_flat / 2.0
        y_root = pitch / 2.0 - root_flat / 2.0
        if root_radius > 0.0:
            # Lokaler Kerbradius als zusätzlicher Stützpunkt beidseitig der Talsohle.
            radius_control = min(root_radius * 0.4, (pitch / 2.0 - y_root) * 0.95)
            pts = [
                ProfilePoint(r, 0.0),
                ProfilePoint(r3, y_root),
                ProfilePoint(r3 + root_radius * 0.5, pitch / 2.0 - radius_control),
                ProfilePoint(r3, pitch / 2.0),
                ProfilePoint(r3 + root_radius * 0.5, pitch / 2.0 + radius_control),
                ProfilePoint(r3, pitch - y_root),
                ProfilePoint(r, pitch - y_crest),
                ProfilePoint(r, pitch),
            ]
        else:
            pts = [
                ProfilePoint(r, 0.0),
                ProfilePoint(r3, y_root),
                ProfilePoint(r3, pitch / 2.0),
                ProfilePoint(r3, pitch - y_root),
                ProfilePoint(r, pitch - y_crest),
                ProfilePoint(r, pitch),
            ]

    elif profile_type == "TRAPEZOID":
        sp = std.get("special_params", {})
        height_factor = max(0.0, ratio(sp.get("height_factor"), 1.0))
        r3 = r - (r - r3) * height_factor
        crest_width = pitch * ratio(sp.get("crest_width"), 0.5)
        root_width = max(0.25, pitch * ratio(sp.get("root_width"), 0.5) if "root_width" in sp else 0.5 * pitch - 0.25)
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

    elif profile_type == "EDISON":
        # IEC 60061-1: weiche Sinuskontur zwischen Außenradius r und Kernradius r3.
        # Eine volle Welle pro Steigung; keine Flachstellen an Krone/Talsohle.
        sp = std.get("special_params", {})
        radius_ratio = ratio(sp.get("radius_ratio"), 1.0 / 3.0)
        amplitude = (r - r3) / 2.0
        center = (r + r3) / 2.0
        steps = max(16, int(round(pitch / max(radius_ratio * pitch, 1e-3) * 8)))
        pts = []
        for i in range(steps + 1):
            y = pitch * i / steps
            x = center + amplitude * math.cos(2.0 * math.pi * y / pitch)
            pts.append(ProfilePoint(x, y))

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

    else:
        pts = [ProfilePoint(r, 0.0), ProfilePoint(r3, pitch / 2.0), ProfilePoint(r, pitch)]

    if not internal:
        _validate_external_profile_points(pts, r, r3, pitch)

    if return_warnings:
        return pts, ratio_warnings
    return pts
