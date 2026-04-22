import bpy

from .database import THREAD_STANDARDS, resolve_thread_parameters
from .geometry_engine import generate_profile
from .mesh_builder import apply_boolean_cutter, apply_material, create_thread_mesh
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

        profile = generate_profile(
            standard_key,
            diameter,
            pitch,
            tolerance_class=props.tolerance_class,
            internal=props.negative_mode,
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
        )

        mesh = bpy.data.meshes.new("UTG_Thread")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Gewinde", mesh)
        context.collection.objects.link(obj)

        apply_material(obj, props.material, props.surface)

        if props.negative_mode:
            target = context.active_object
            if target and target != obj:
                apply_boolean_cutter(context, obj, target)
            else:
                self.report({"WARNING"}, "Negativ-Modus aktiv, aber kein gültiges Zielobjekt aktiv.")

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
        )

        mesh = bpy.data.meshes.new("UTG_BallScrew")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Kugelgewindetrieb", mesh)
        context.collection.objects.link(obj)
        apply_material(obj, props.material, props.surface)
        return {"FINISHED"}


classes = [
    UTG_Properties,
    THREADFORGE_PT_main,
    UTG_OT_create_thread,
    UTG_OT_create_ball_screw,
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
