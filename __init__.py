import bmesh
import bpy

from .database import get_standard_pitch
from .geometry_engine import generate_profile
from .mesh_builder import apply_boolean_cutter, apply_material, create_thread_mesh
from .ui_panel import THREADFORGE_PT_main, UTG_Properties, register_properties

bl_info = {
    "name": "Universal Thread Generator",
    "author": "Ihr Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > ThreadForge",
    "description": "Erzeugt normgerechte und benutzerdefinierte Gewinde",
    "category": "Mesh",
}


class UTG_OT_create_thread(bpy.types.Operator):
    bl_idname = "utg.create_thread"
    bl_label = "Gewinde erstellen"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props

        if props.standard == "CUSTOM":
            diameter = props.custom_diameter
            pitch = props.custom_pitch
            standard_key = "METRIC_ISO"
        else:
            diameter = float(props.diameter_enum)
            pitch = get_standard_pitch(props.standard, diameter)
            standard_key = props.standard

        if pitch > diameter:
            self.report({"ERROR"}, "Ungültig: Steigung darf nicht größer als Durchmesser sein.")
            return {"CANCELLED"}

        profile = generate_profile(
            standard_key,
            diameter,
            pitch,
            tolerance_class=props.tolerance_class,
            internal=props.negative_mode,
            clearance=props.clearance if props.negative_mode else 0.0,
        )

        bm = create_thread_mesh(
            name="Gewinde",
            profile_points=profile,
            diameter=diameter,
            pitch=pitch,
            length=props.length,
            starts=props.custom_starts if props.standard == "CUSTOM" else 1,
            handedness=props.handedness,
            end_type=props.end_type,
        )

        mesh = bpy.data.meshes.new("Thread")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("Gewindestange", mesh)
        context.collection.objects.link(obj)

        apply_material(obj, props.material)

        if props.negative_mode and context.active_object and context.active_object != obj:
            apply_boolean_cutter(context, obj, context.active_object)

        return {"FINISHED"}


class UTG_OT_create_ball_screw(bpy.types.Operator):
    bl_idname = "utg.create_ball_screw"
    bl_label = "Kugelgewindetrieb erstellen"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.utg_props
        diameter = props.custom_diameter if props.standard == "CUSTOM" else float(props.diameter_enum)
        pitch = props.custom_pitch if props.standard == "CUSTOM" else get_standard_pitch(props.standard, diameter)

        profile = generate_profile("METRIC_ISO", diameter, pitch)
        bm = create_thread_mesh(
            name="KGT",
            profile_points=profile,
            diameter=diameter,
            pitch=pitch,
            length=props.length,
            starts=max(1, props.custom_starts),
            handedness=props.handedness,
            end_type=props.end_type,
        )

        mesh = bpy.data.meshes.new("BallScrew")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("Kugelgewindetrieb", mesh)
        context.collection.objects.link(obj)
        return {"FINISHED"}


classes = [UTG_Properties, THREADFORGE_PT_main, UTG_OT_create_thread, UTG_OT_create_ball_screw]


def register():
    _ = bmesh
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.utg_props


if __name__ == "__main__":
    register()
