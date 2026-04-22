import math
from mathutils import Vector

from .database import THREAD_STANDARDS


def generate_profile(standard_key, diameter, pitch, tolerance_class="6g", internal=False, clearance=0.0):
    """Erzeugt 2D-Profilpunkte eines Gewindegangs."""
    _ = tolerance_class
    std = THREAD_STANDARDS[standard_key]
    profile_type = std["profile_type"]

    d2 = std["d2_formula"](diameter, pitch)
    d3 = std["d3_formula"](diameter, pitch)
    r = diameter / 2.0
    r2 = d2 / 2.0
    r3 = d3 / 2.0

    offset = clearance / 2.0 if internal else -clearance / 2.0
    r += offset
    r2 += offset
    r3 += offset

    if profile_type == "V":
        h = (r - r3)
        if standard_key.startswith("METRIC"):
            crest_flat = pitch / 8.0
            root_flat = pitch / 4.0
        elif standard_key in ["UNC", "UNF"]:
            crest_flat = pitch / 8.0
            root_flat = pitch / 8.0
        elif standard_key.startswith("WHITWORTH"):
            crest_flat = pitch / 6.0
            root_flat = pitch / 6.0
        else:
            crest_flat = 0.0
            root_flat = 0.0

        y_crest = crest_flat / 2.0
        y_root = pitch / 2.0 - root_flat / 2.0
        pts = [
            Vector((r, 0.0)),
            Vector((r - h + root_flat, y_root)),
            Vector((r3, pitch / 2.0)),
            Vector((r - h + root_flat, pitch - y_root)),
            Vector((r, pitch - y_crest)),
            Vector((r, pitch)),
        ]

    elif profile_type == "TRAPEZOID":
        crest_width = 0.5 * pitch
        root_width = 0.5 * pitch - 0.25
        y_root = pitch / 2.0 - root_width / 2.0
        pts = [
            Vector((r, 0.0)),
            Vector((r, crest_width)),
            Vector((r3, y_root + root_width)),
            Vector((r3, pitch - y_root)),
            Vector((r, pitch - crest_width)),
            Vector((r, pitch)),
        ]

    elif profile_type == "ROUND":
        radius = pitch / 4.0
        steps = 16
        pts = []
        for i in range(steps + 1):
            ang = math.pi * i / steps
            pts.append(Vector((r - radius + radius * math.cos(ang), radius * math.sin(ang))))
        for i in range(1, steps + 1):
            ang = math.pi * i / steps
            pts.append(Vector((r3 + radius - radius * math.cos(ang), pitch / 2.0 + radius * math.sin(ang))))
        pts.extend([Vector((p.x, pitch - p.y)) for p in reversed(pts[:-1])])

    elif profile_type == "BUTTRESS":
        h = r - r3
        dx_clear = h * math.tan(math.radians(3.0))
        dx_press = h * math.tan(math.radians(30.0))
        crest_width = 0.2 * pitch
        root_width = 0.2 * pitch
        pts = [
            Vector((r, 0.0)),
            Vector((r, crest_width)),
            Vector((r - dx_press, pitch / 2.0 - root_width / 2.0)),
            Vector((r - h, pitch / 2.0)),
            Vector((r - h + dx_clear, pitch / 2.0 + root_width / 2.0)),
            Vector((r, pitch - crest_width)),
            Vector((r, pitch)),
        ]

    elif profile_type == "GOTHIC":
        ball_radius = pitch * 0.6
        contact_angle = math.radians(45.0)
        center_offset = ball_radius * math.sin(contact_angle)
        steps = 12
        pts = []
        center = Vector((r - ball_radius, pitch / 2.0 - center_offset))
        for i in range(steps + 1):
            ang = -math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(Vector((center.x + ball_radius * math.cos(ang), center.y + ball_radius * math.sin(ang))))
        center = Vector((r - ball_radius, pitch / 2.0 + center_offset))
        for i in range(1, steps + 1):
            ang = math.pi / 2 + contact_angle + (math.pi - 2 * contact_angle) * i / steps
            pts.append(Vector((center.x + ball_radius * math.cos(ang), center.y + ball_radius * math.sin(ang))))
        pts.append(Vector((r2, pitch)))

    else:
        pts = [Vector((r, 0.0)), Vector((r3, pitch / 2.0)), Vector((r, pitch))]

    return pts
