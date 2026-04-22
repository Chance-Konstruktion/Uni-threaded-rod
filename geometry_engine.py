import math
from mathutils import Vector

from .database import THREAD_STANDARDS


def _tolerance_offset_mm(tolerance_class):
    """Grobe radiale Toleranzverschiebung in mm (positiv = größer, negativ = kleiner)."""
    if not tolerance_class:
        return 0.0

    tc = str(tolerance_class).strip().upper()
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


def generate_profile(standard_key, diameter, pitch, tolerance_class="6g", internal=False, clearance=0.0):
    """Erzeugt 2D-Profilpunkte eines Gewindegangs (x=radial, y=axial)."""
    std = THREAD_STANDARDS[standard_key]
    profile_type = std["profile_type"]

    d2 = std["d2_formula"](diameter, pitch)
    d3 = std["d3_formula"](diameter, pitch)
    r = diameter / 2.0
    r2 = d2 / 2.0
    r3 = d3 / 2.0

    tol_offset = _tolerance_offset_mm(tolerance_class)
    offset = (clearance / 2.0 + tol_offset) if internal else (-clearance / 2.0 + tol_offset)
    r += offset
    r2 += offset
    r3 += offset

    if profile_type == "V":
        h = r - r3
        if standard_key.startswith("METRIC"):
            crest_flat = pitch / 8.0
            root_flat = pitch / 4.0
        elif standard_key in {"UNC", "UNF"}:
            crest_flat = pitch / 8.0
            root_flat = pitch / 8.0
        elif standard_key.startswith("WHITWORTH"):
            crest_flat = pitch / 6.0
            root_flat = pitch / 6.0
        else:
            crest_flat = 0.05 * pitch
            root_flat = 0.10 * pitch

        y_crest = crest_flat / 2.0
        y_root = pitch / 2.0 - root_flat / 2.0
        pts = [
            Vector((r, 0.0)),
            Vector((r - h + root_flat * 0.5, y_root)),
            Vector((r3, pitch / 2.0)),
            Vector((r - h + root_flat * 0.5, pitch - y_root)),
            Vector((r, pitch - y_crest)),
            Vector((r, pitch)),
        ]

    elif profile_type == "TRAPEZOID":
        crest_width = 0.5 * pitch
        root_width = max(0.25, 0.5 * pitch - 0.25)
        y_crest = crest_width / 2.0
        y_root = pitch / 2.0 - root_width / 2.0
        pts = [
            Vector((r, 0.0)),
            Vector((r, y_crest)),
            Vector((r3, y_root)),
            Vector((r3, y_root + root_width)),
            Vector((r, pitch - y_crest)),
            Vector((r, pitch)),
        ]

    elif profile_type == "ROUND":
        radius = pitch / 4.0
        steps = 14
        pts = []
        for i in range(steps + 1):
            ang = math.pi * i / steps
            pts.append(Vector((r - radius + radius * math.cos(ang), radius * math.sin(ang))))
        for i in range(1, steps + 1):
            ang = math.pi * i / steps
            pts.append(Vector((r3 + radius - radius * math.cos(ang), pitch / 2.0 + radius * math.sin(ang))))
        pts.extend(Vector((p.x, pitch - p.y)) for p in reversed(pts[:-1]))

    elif profile_type == "BUTTRESS":
        h = r - r3
        dx_clear = h * math.tan(math.radians(std.get("special_params", {}).get("clearance_flank", 3.0)))
        dx_press = h * math.tan(math.radians(std.get("special_params", {}).get("pressure_flank", 30.0)))
        crest_width = 0.2 * pitch
        root_width = 0.2 * pitch
        pts = [
            Vector((r, 0.0)),
            Vector((r, crest_width)),
            Vector((r - dx_press, pitch / 2.0 - root_width / 2.0)),
            Vector((r3, pitch / 2.0)),
            Vector((r3 + dx_clear, pitch / 2.0 + root_width / 2.0)),
            Vector((r, pitch - crest_width)),
            Vector((r, pitch)),
        ]

    elif profile_type == "GOTHIC":
        ball_radius = pitch * 0.60
        contact_angle = math.radians(std.get("special_params", {}).get("contact_angle", 45.0))
        center_offset = ball_radius * math.sin(contact_angle)
        steps = 16
        pts = []

        center_a = Vector((r2 - ball_radius, pitch / 2.0 - center_offset))
        for i in range(steps + 1):
            ang = -math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(Vector((center_a.x + ball_radius * math.cos(ang), center_a.y + ball_radius * math.sin(ang))))

        center_b = Vector((r2 - ball_radius, pitch / 2.0 + center_offset))
        for i in range(1, steps + 1):
            ang = math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(Vector((center_b.x + ball_radius * math.cos(ang), center_b.y + ball_radius * math.sin(ang))))

        pts.append(Vector((r, pitch)))

    else:
        pts = [Vector((r, 0.0)), Vector((r3, pitch / 2.0)), Vector((r, pitch))]

    return pts
