import bpy

from .database import THREAD_PRESETS, THREAD_STANDARDS, resolve_thread_parameters
from .geometry_engine import generate_profile
from .mesh_builder import (
    apply_boolean_cutter,
    apply_material,
    create_nut_body_mesh,
    create_return_tube_mesh,
    create_thread_mesh,
)
from .ui_panel import THREADFORGE_PT_main, UTG_Properties, register_properties

bl_info = {
    "name": "Uni-threaded-rod",
    "author": "Ihr Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Uni-threaded-rod",
    "description": "Erzeugt normgerechte und benutzerdefinierte Gewinde",
    "category": "Mesh",
}


def _create_standard_from_custom(props):
    return {
        "profile_type": props.custom_profile_type,
        "flank_angle": props.custom_flank_angle,
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p,
    }


def _validate_parameters(diameter, pitch, length, starts):
    if diameter <= 0.0:
        return "Ungültig: Durchmesser muss > 0 sein."
    if pitch <= 0.0:
        return "Ungültig: Steigung muss > 0 sein."
    if length <= 0.0:
        return "Ungültig: Länge muss > 0 sein."
    if starts < 1:
        return "Ungültig: Gängigkeit muss mindestens 1 sein."
    if starts > 16:
        return "Ungültig: Gängigkeit ist zu hoch (maximal 16)."
    if pitch > diameter:
        return "Ungültig: Steigung darf nicht größer als Durchmesser sein."
    d3 = diameter - 1.6 * pitch
    if d3 <= 0.0 or d3 < 0.2 * diameter:
        return "Ungültig: Kerndurchmesser wäre kritisch klein (Self-Intersection-Risiko)."
    return None


class UTG_OT_create_thread(bpy.types.Operator):
    bl_idname = "utg.create_thread"
    bl_label = "Gewinde erstellen"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props
        target_for_boolean = context.active_object if props.negative_mode else None

        if props.standard == "CUSTOM":
            diameter = props.custom_diameter
            pitch = props.custom_pitch
            custom_std = _create_standard_from_custom(props)
            THREAD_STANDARDS["_UTG_CUSTOM"] = custom_std
            standard_key = "_UTG_CUSTOM"
        else:
            standard_key = props.standard
            try:
                diameter, pitch = resolve_thread_parameters(standard_key, props.diameter_enum)
            except Exception as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}

        validation_error = _validate_parameters(diameter, pitch, props.length, props.starts)
        if validation_error:
            self.report({"ERROR"}, validation_error)
            return {"CANCELLED"}

        negative_mode_active = bool(props.negative_mode and target_for_boolean)
        if props.negative_mode and not negative_mode_active:
            self.report({"INFO"}, "Negativ-Modus deaktiviert: Kein aktives Zielobjekt gefunden, erzeuge stattdessen Gewindestab.")

        profile = generate_profile(
            standard_key,
            diameter,
            pitch,
            tolerance_class=props.tolerance_class,
            internal=negative_mode_active,
            clearance=props.clearance,
        )

        bm = create_thread_mesh(
            name="Gewinde",
            profile_points=profile,
            diameter=diameter,
            pitch=pitch,
            length=props.length,
            starts=props.starts,
            handedness=props.handedness,
            end_type=props.end_type,
            taper_ratio=THREAD_STANDARDS.get(standard_key, {}).get("special_params", {}).get("taper_ratio", 0.0),
            lod_level=props.lod_level,
            segment_override=props.segment_override,
        )

        mesh = bpy.data.meshes.new("UTG_Thread")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Gewinde", mesh)
        context.collection.objects.link(obj)

        apply_material(obj, props.material, props.surface)

        if negative_mode_active:
            if target_for_boolean != obj:
                apply_boolean_cutter(context, obj, target_for_boolean)
            else:
                self.report({"WARNING"}, "Negativ-Modus aktiv, aber Zielobjekt ist ungültig.")

        if standard_key == "_UTG_CUSTOM":
            THREAD_STANDARDS.pop("_UTG_CUSTOM", None)

        return {"FINISHED"}


class UTG_OT_create_ball_screw(bpy.types.Operator):
    bl_idname = "utg.create_ball_screw"
    bl_label = "Kugelgewindetrieb erstellen"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props

        if props.standard == "CUSTOM":
            diameter = props.custom_diameter
            pitch = props.custom_pitch
        elif props.standard == "BALL_SCREW":
            diameter, pitch = resolve_thread_parameters("BALL_SCREW", props.diameter_enum)
        else:
            diameter, pitch = resolve_thread_parameters(props.standard, props.diameter_enum)

        validation_error = _validate_parameters(diameter, pitch, props.length, props.starts)
        if validation_error:
            self.report({"ERROR"}, validation_error)
            return {"CANCELLED"}

        profile = generate_profile("BALL_SCREW", diameter, pitch, internal=False, clearance=props.clearance)

        bm = create_thread_mesh(
            name="KGT",
            profile_points=profile,
            diameter=diameter,
            pitch=pitch,
            length=props.length,
            starts=max(1, props.starts),
            handedness=props.handedness,
            end_type=props.end_type,
            lod_level=props.lod_level,
            segment_override=props.segment_override,
        )

        mesh = bpy.data.meshes.new("UTG_BallScrew")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Kugelgewindetrieb", mesh)
        context.collection.objects.link(obj)
        apply_material(obj, props.material, props.surface)
        return {"FINISHED"}


class UTG_OT_create_ball_nut(bpy.types.Operator):
    bl_idname = "utg.create_ball_nut"
    bl_label = "KGT-Mutter erstellen"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props

        if props.standard == "CUSTOM":
            diameter = props.custom_diameter
            pitch = props.custom_pitch
        else:
            source_standard = "BALL_SCREW" if props.standard == "BALL_SCREW" else props.standard
            diameter, pitch = resolve_thread_parameters(source_standard, props.diameter_enum)

        validation_error = _validate_parameters(diameter, pitch, props.length, props.starts)
        if validation_error:
            self.report({"ERROR"}, validation_error)
            return {"CANCELLED"}

        body_bm = create_nut_body_mesh(
            name="KGT_Mutter_Rohling",
            outer_diameter=max(props.nut_outer_diameter, diameter + 2.0),
            length=max(props.nut_length, pitch * 2.0),
            segments=max(props.segment_override, 32),
        )
        body_mesh = bpy.data.meshes.new("UTG_BallNutBody")
        body_bm.to_mesh(body_mesh)
        body_bm.free()

        nut_obj = bpy.data.objects.new("KGT_Mutter", body_mesh)
        context.collection.objects.link(nut_obj)

        inner_profile = generate_profile(
            "BALL_SCREW",
            diameter,
            pitch,
            tolerance_class=props.tolerance_class,
            internal=True,
            clearance=props.clearance + props.nut_internal_clearance,
        )
        cutter_bm = create_thread_mesh(
            name="KGT_Innenprofil",
            profile_points=inner_profile,
            diameter=diameter,
            pitch=pitch,
            length=max(props.nut_length, pitch * 2.0),
            starts=max(1, props.starts),
            handedness=props.handedness,
            end_type="FLAT",
            lod_level=props.lod_level,
            segment_override=props.segment_override,
        )
        cutter_mesh = bpy.data.meshes.new("UTG_BallNutCutter")
        cutter_bm.to_mesh(cutter_mesh)
        cutter_bm.free()
        cutter_obj = bpy.data.objects.new("KGT_Mutter_Cutter", cutter_mesh)
        context.collection.objects.link(cutter_obj)

        apply_boolean_cutter(context, cutter_obj, nut_obj)

        if props.ball_return_enabled:
            tube_bm = create_return_tube_mesh(
                name="KGT_Rueckfuehrung",
                major_radius=max(props.nut_outer_diameter * 0.55, 0.5),
                minor_radius=max(pitch * 0.25, 0.2),
                location=(0.0, max(props.nut_outer_diameter * 0.52, 0.5), max(props.nut_length * 0.5, 0.2)),
            )
            tube_mesh = bpy.data.meshes.new("UTG_BallNutReturn")
            tube_bm.to_mesh(tube_mesh)
            tube_bm.free()
            tube_obj = bpy.data.objects.new("KGT_Rueckfuehrung", tube_mesh)
            context.collection.objects.link(tube_obj)
            apply_material(tube_obj, props.material, props.surface)

        apply_material(nut_obj, props.material, props.surface)
        return {"FINISHED"}


class UTG_OT_apply_preset(bpy.types.Operator):
    bl_idname = "utg.apply_preset"
    bl_label = "Preset anwenden"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props
        if props.preset_key == "NONE":
            self.report({"INFO"}, "Kein Preset ausgewählt.")
            return {"CANCELLED"}

        preset = THREAD_PRESETS.get(props.preset_key)
        if not preset:
            self.report({"ERROR"}, "Preset nicht gefunden.")
            return {"CANCELLED"}

        props.standard = preset["standard"]
        props.diameter_enum = preset["diameter_token"]
        props.material = preset["material"]
        props.surface = preset["surface"]
        props.tolerance_class = preset["tolerance_class"]
        props.clearance = preset["clearance"]
        props.starts = preset["starts"]
        self.report({"INFO"}, f"Preset '{preset['name']}' angewendet.")
        return {"FINISHED"}


classes = [
    UTG_Properties,
    THREADFORGE_PT_main,
    UTG_OT_create_thread,
    UTG_OT_create_ball_screw,
    UTG_OT_create_ball_nut,
    UTG_OT_apply_preset,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "utg_props"):
        del bpy.types.Scene.utg_props


if __name__ == "__main__":
    register()
