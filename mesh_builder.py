import math
from bisect import bisect_left

import bmesh
import bpy
from mathutils import Vector

from .database import MATERIAL_PRESETS


MM_TO_BLENDER_UNITS = 0.001


def _apply_end_profile(loop_verts, end_type):
    if end_type == "FLAT" or not loop_verts:
        return

    zs = [v.co.z for v in loop_verts]
    z_min, z_max = min(zs), max(zs)
    span = max(1e-6, z_max - z_min)

    for v in loop_verts:
        rel = (v.co.z - z_min) / span
        if end_type == "CHAMFER":
            # lineare 45°-ähnliche Verjüngung
            shrink = 1.0 - 0.12 * rel
        else:  # RUNOUT
            # weichere S-Kurve
            shrink = 1.0 - 0.16 * (rel * rel * (3.0 - 2.0 * rel))
        v.co.x *= shrink
        v.co.y *= shrink


def _flip_caps_to_outside(bm, length):
    """Stellt sicher, dass Stirnflächen unten nach -Z und oben nach +Z zeigen."""
    for face in bm.faces:
        center = face.calc_center_median()
        if abs(center.z) <= 1e-5 and face.normal.z > 0.0:
            face.normal_flip()
        elif abs(center.z - length) <= 1e-5 and face.normal.z < 0.0:
            face.normal_flip()


def _enforce_external_normals(bm, length):
    """Korrigiert die Normalen der erzeugten Stange auf Außenorientierung."""
    bm.normal_update()
    _flip_caps_to_outside(bm, length)
    bm.normal_update()



def create_thread_mesh(
    profile_points,
    diameter,
    pitch,
    length,
    starts=1,
    handedness="RIGHT",
    end_type="CHAMFER",
    taper_ratio=0.0,
    lod_level="FINAL",
    segment_override=48,
):
    """Dieser Builder erzeugt ausschließlich massive Vollkörper mit Außengewinde. Er ist nicht dafür gedacht, dünnwandige Hüllen oder primäre Innengewinde zu erzeugen.

    Erzeugt immer einen soliden Vollkörper mit Außengewinde.

    Dieser Mesh-Builder ist ausschließlich für massive Außengewindestangen
    gedacht: Jede axiale Station wird als voller Ring um die Z-Achse aufgebaut
    und die Stirnflächen werden mit Zentrumspunkten geschlossen. Er ist nicht
    für Innengewinde-Cutter gedacht; solche Cutter müssen nur über den
    expliziten Negativ-/Boolean-Workflow entstehen.
    """
    if diameter <= 0.0:
        raise ValueError("Durchmesser muss > 0 sein")
    if pitch <= 0.0:
        raise ValueError("Steigung (Pitch) muss > 0 sein")
    if length <= 0.0:
        raise ValueError("Länge muss > 0 sein")
    if len(profile_points) < 3:
        raise ValueError("Gewindeprofil benötigt mindestens drei Punkte")

    axial_tolerance = max(1e-9, pitch * 1e-9)
    profile_samples = []
    for point in profile_points:
        if not math.isfinite(point.x) or not math.isfinite(point.y):
            raise ValueError("Gewindeprofil enthält nicht-finite Koordinaten")
        if point.x <= 0.0:
            raise ValueError("Gewindeprofil enthält radiale Koordinaten <= 0")

        if -axial_tolerance <= point.y <= pitch + axial_tolerance:
            clamped_y = min(max(point.y, 0.0), pitch)
            profile_samples.append((clamped_y, point.x))

    if len(profile_samples) < 2:
        raise ValueError("Gewindeprofil enthält keine nutzbare Profilperiode")

    # Profilperiode direkt als sortierte Stützstellen ablegen. Fallen mehrere
    # Punkte numerisch auf dieselbe y-Position, bleibt der größere Radius als
    # sichere Außenkontur erhalten.
    profile_samples.sort(key=lambda sample: sample[0])
    period_samples = []
    for y, radius in profile_samples:
        if period_samples and abs(y - period_samples[-1][0]) <= axial_tolerance:
            previous_y, previous_radius = period_samples[-1]
            period_samples[-1] = (previous_y, max(previous_radius, radius))
        else:
            period_samples.append((y, radius))

    if abs(period_samples[0][0]) > axial_tolerance:
        raise ValueError("Gewindeprofil muss bei y=0 beginnen")
    if abs(period_samples[-1][0] - pitch) > axial_tolerance:
        raise ValueError("Gewindeprofil muss bei y=pitch enden")

    sample_y = [sample[0] for sample in period_samples]
    sample_radius = [sample[1] for sample in period_samples]
    def radius_at_profile_y(local_y):
        y = local_y % pitch
        upper_index = bisect_left(sample_y, y)
        if upper_index <= 0:
            return sample_radius[0]
        if upper_index >= len(sample_y):
            return sample_radius[-1]

        y0 = sample_y[upper_index - 1]
        y1 = sample_y[upper_index]
        r0 = sample_radius[upper_index - 1]
        r1 = sample_radius[upper_index]
        blend = (y - y0) / max(y1 - y0, 1e-12)
        return r0 + (r1 - r0) * blend

    bm = bmesh.new()

    if lod_level == "PREVIEW":
        lod_factor = 0.70
    elif lod_level == "CUSTOM":
        lod_factor = 1.0
    else:
        lod_factor = 1.15

    auto_segments = max(24, int((36 * (pitch / 5.0) + diameter * 0.6) * lod_factor))
    circumferential_segments = max(12, int(segment_override)) if lod_level == "CUSTOM" else auto_segments
    if length > 250.0:
        circumferential_segments = max(18, int(circumferential_segments * 0.85))

    start_count = max(1, int(starts))
    direction = 1.0 if handedness == "RIGHT" else -1.0
    lead = pitch * start_count
    segments_per_lead = max(circumferential_segments * start_count, circumferential_segments)
    # math.ceil verhindert ein zu kurzes Mesh. Die tatsächliche Z-Koordinate
    # wird pro Ring hart mit z = min(t * lead, length) begrenzt.
    axial_segments = max(1, math.ceil((length / lead) * segments_per_lead))

    rings = []
    for axial_index in range(axial_segments + 1):
        t = axial_index / segments_per_lead
        z = min(t * lead, length)
        ring = []
        for radial_index in range(circumferential_segments):
            angle = 2.0 * math.pi * radial_index / circumferential_segments
            helical_y = z - direction * angle * lead / (2.0 * math.pi)
            radius = radius_at_profile_y(helical_y)

            if taper_ratio > 0.0:
                diameter_delta = z * taper_ratio
                taper_scale = max(0.2, 1.0 - diameter_delta / max(diameter, 1e-6))
                radius *= taper_scale

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            ring.append(bm.verts.new(Vector((x, y, z))))
        rings.append(ring)

    # Mantel-Quads: Umfangsrichtung zuerst, dann +Z. Diese Reihenfolge erzeugt
    # bereits bei der Konstruktion radial nach außen zeigende Normalen.
    for axial_index in range(axial_segments):
        lower_ring = rings[axial_index]
        upper_ring = rings[axial_index + 1]
        for radial_index in range(circumferential_segments):
            next_radial_index = (radial_index + 1) % circumferential_segments
            v00 = lower_ring[radial_index]
            v01 = lower_ring[next_radial_index]
            v11 = upper_ring[next_radial_index]
            v10 = upper_ring[radial_index]
            try:
                bm.faces.new((v00, v01, v11, v10))
            except ValueError:
                pass

    # Saubere planare Caps nur aus den echten Ring-Vertices auf exakt z=0 und
    # z=length; keine verzerrten oder geclippten Profil-Loops als Stirnflächen.
    center_bottom = bm.verts.new(Vector((0.0, 0.0, 0.0)))
    bottom_ring = rings[0]
    for radial_index in range(circumferential_segments):
        v1 = bottom_ring[radial_index]
        v2 = bottom_ring[(radial_index + 1) % circumferential_segments]
        try:
            bm.faces.new((center_bottom, v2, v1))
        except ValueError:
            pass

    center_top = bm.verts.new(Vector((0.0, 0.0, length)))
    top_ring = rings[-1]
    for radial_index in range(circumferential_segments):
        v1 = top_ring[radial_index]
        v2 = top_ring[(radial_index + 1) % circumferential_segments]
        try:
            bm.faces.new((center_top, v1, v2))
        except ValueError:
            pass

    _apply_end_profile([vert for ring in rings for vert in ring], end_type)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.000001)
    bm.normal_update()
    _enforce_external_normals(bm, length)

    non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
    if non_manifold_edges:
        bmesh.ops.holes_fill(bm, edges=non_manifold_edges, sides=0)
        bm.normal_update()
        _enforce_external_normals(bm, length)

        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        if non_manifold_edges:
            bm.free()
            raise ValueError(f"Gewindestange ist nicht manifold ({len(non_manifold_edges)} offene Kanten)")

    for vert in bm.verts:
        vert.co.x *= MM_TO_BLENDER_UNITS
        vert.co.y *= MM_TO_BLENDER_UNITS
        vert.co.z *= MM_TO_BLENDER_UNITS

    return bm

def apply_material(obj, material_key, surface_key="NONE"):
    """Weist dem Objekt ein Material aus MATERIAL_PRESETS zu."""
    resolved_key = material_key
    if surface_key in {"ZINC", "HOT_DIP"}:
        resolved_key = surface_key

    mat_name = f"UTG_{resolved_key}"
    if mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        preset = MATERIAL_PRESETS[resolved_key]
        bsdf.inputs["Base Color"].default_value = preset["color"]
        bsdf.inputs["Metallic"].default_value = preset["metallic"]
        bsdf.inputs["Roughness"].default_value = preset["roughness"]
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = preset["ior"]
    else:
        mat = bpy.data.materials[mat_name]

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def apply_boolean_cutter(context, cutter_obj, target_obj):
    """Führt Boolesche Differenz aus und löscht Cutter.

    Sichert und restauriert den Objekt-/Selektionszustand, damit der Workflow
    auch in komplexeren Szenen stabil bleibt.
    """
    prev_active = context.view_layer.objects.active
    prev_selected = [obj for obj in context.selected_objects]

    try:
        for obj in prev_selected:
            obj.select_set(False)

        context.view_layer.objects.active = target_obj
        target_obj.select_set(True)
        cutter_obj.select_set(True)

        mod = target_obj.modifiers.new(name="UTG_Boolean", type="BOOLEAN")
        mod.object = cutter_obj
        mod.operation = "DIFFERENCE"

        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter_obj, do_unlink=True)
    finally:
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in prev_selected:
            if obj.name in bpy.data.objects:
                obj.select_set(True)
        if prev_active and prev_active.name in bpy.data.objects:
            context.view_layer.objects.active = prev_active
