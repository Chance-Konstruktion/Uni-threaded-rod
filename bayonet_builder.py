import math

import bmesh
from mathutils import Vector

MM_TO_BLENDER_UNITS = 0.001


def _standard_bayonet_params(standard_key, diameter):
    if standard_key == "STORZ":
        return {
            "lug_count": 2,
            "lug_width_angle": math.radians(24.0),
            "lug_length": max(5.0, diameter * 0.10),
            "lug_height": max(2.0, diameter * 0.035),
            "groove_depth": max(1.0, diameter * 0.015),
        }
    if standard_key == "LAMP_B":
        return {
            "lug_count": 2,
            "lug_width_angle": math.radians(28.0),
            "lug_length": max(2.0, diameter * 0.14),
            "lug_height": max(0.8, diameter * 0.045),
            "groove_depth": max(0.4, diameter * 0.018),
        }
    return {
        "lug_count": 2,
        "lug_width_angle": math.radians(24.0),
        "lug_length": max(2.0, diameter * 0.10),
        "lug_height": max(0.8, diameter * 0.035),
        "groove_depth": max(0.4, diameter * 0.015),
    }


def _radius_for_bayonet(angle, z, base_radius, length, params):
    lug_radius = base_radius + params["lug_height"]
    groove_radius = max(base_radius * 0.65, base_radius - params["groove_depth"])
    lug_z0 = length * 0.20
    lug_z1 = min(length * 0.80, lug_z0 + params["lug_length"])
    groove_z0 = length * 0.12
    groove_z1 = length * 0.88

    radius = base_radius
    if groove_z0 <= z <= groove_z1:
        radius = groove_radius

    if lug_z0 <= z <= lug_z1:
        lug_count = params["lug_count"]
        half_width = params["lug_width_angle"] * 0.5
        for lug_index in range(lug_count):
            center = 2.0 * math.pi * lug_index / lug_count
            delta = abs((angle - center + math.pi) % (2.0 * math.pi) - math.pi)
            if delta <= half_width:
                radius = lug_radius
                break

    return radius


def create_bayonet_mesh(standard_key, diameter, length, lod_level="FINAL", segment_override=72):
    if diameter <= 0.0:
        raise ValueError("Durchmesser muss > 0 sein")
    if length <= 0.0:
        raise ValueError("Länge muss > 0 sein")

    params = _standard_bayonet_params(standard_key, diameter)
    bm = bmesh.new()
    lod_factor = 0.75 if lod_level == "PREVIEW" else 1.0
    circumferential_segments = max(32, int(segment_override)) if lod_level == "CUSTOM" else max(48, int(diameter * 1.2 * lod_factor))
    axial_segments = max(8, int(length / max(params["lug_length"] * 0.25, 1.0)))
    base_radius = diameter * 0.5

    rings = []
    for axial_index in range(axial_segments + 1):
        z = length * axial_index / axial_segments
        ring = []
        for radial_index in range(circumferential_segments):
            angle = 2.0 * math.pi * radial_index / circumferential_segments
            radius = _radius_for_bayonet(angle, z, base_radius, length, params)
            ring.append(bm.verts.new(Vector((radius * math.cos(angle), radius * math.sin(angle), z))))
        rings.append(ring)

    for axial_index in range(axial_segments):
        lower_ring = rings[axial_index]
        upper_ring = rings[axial_index + 1]
        for radial_index in range(circumferential_segments):
            next_radial_index = (radial_index + 1) % circumferential_segments
            bm.faces.new((lower_ring[radial_index], lower_ring[next_radial_index], upper_ring[next_radial_index], upper_ring[radial_index]))

    center_bottom = bm.verts.new(Vector((0.0, 0.0, 0.0)))
    bottom_ring = rings[0]
    for radial_index in range(circumferential_segments):
        bm.faces.new((center_bottom, bottom_ring[(radial_index + 1) % circumferential_segments], bottom_ring[radial_index]))

    center_top = bm.verts.new(Vector((0.0, 0.0, length)))
    top_ring = rings[-1]
    for radial_index in range(circumferential_segments):
        bm.faces.new((center_top, top_ring[radial_index], top_ring[(radial_index + 1) % circumferential_segments]))

    bm.normal_update()
    for vert in bm.verts:
        vert.co.x *= MM_TO_BLENDER_UNITS
        vert.co.y *= MM_TO_BLENDER_UNITS
        vert.co.z *= MM_TO_BLENDER_UNITS
    return bm
