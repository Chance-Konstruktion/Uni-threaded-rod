import bpy

from .database import MATERIAL_PRESETS, THREAD_PRESETS, THREAD_STANDARDS, get_diameter_items_for_standard
from .ui_i18n import ui_label


def get_diameter_items(self, context):
    props = context.scene.utg_props
    std = props.standard
    if std == "CUSTOM" or std not in THREAD_STANDARDS:
        return [("0", "---", "")]
    return get_diameter_items_for_standard(std)


def get_tolerance_items(self, context):
    props = context.scene.utg_props
    std_key = props.standard
    if std_key == "CUSTOM" or std_key not in THREAD_STANDARDS:
        return [("6g", "6g", "Standard")]

    std = THREAD_STANDARDS[std_key]
    tol = std.get("tolerance_classes", {})
    ext = tol.get("external", [])
    inner = tol.get("internal", [])
    all_items = ext or (ext + inner)
    if not all_items:
        all_items = ["6g"]
    return [(v, v, "Toleranz") for v in all_items]


class UTG_Properties(bpy.types.PropertyGroup):
    standard: bpy.props.EnumProperty(
        name="Norm",
        items=[(k, THREAD_STANDARDS[k]["name"], THREAD_STANDARDS[k]["standard"]) for k in THREAD_STANDARDS.keys()] + [("CUSTOM", "Benutzerdefiniert", "Freie Parameter")],
        default="METRIC_ISO",
    )

    diameter_enum: bpy.props.EnumProperty(name="Durchmesser", items=get_diameter_items)
    length: bpy.props.FloatProperty(name="Gewindestangenlänge (mm)", default=100.0, min=0.1, max=1000.0)
    handedness: bpy.props.EnumProperty(name="Drehrichtung", items=[("RIGHT", "Rechtsgewinde", ""), ("LEFT", "Linksgewinde", "")], default="RIGHT")
    starts: bpy.props.IntProperty(name="Gängigkeit", default=1, min=1, max=8)

    material: bpy.props.EnumProperty(name="Material", items=[(k, MATERIAL_PRESETS[k]["name"], "") for k in MATERIAL_PRESETS.keys()], default="STEEL_8.8")
    surface: bpy.props.EnumProperty(name="Oberfläche", items=[("NONE", "Unbehandelt", ""), ("ZINC", "Verzinkt", ""), ("HOT_DIP", "Feuerverzinkt", "")], default="NONE")

    tolerance_class: bpy.props.EnumProperty(name="Toleranzklasse", items=get_tolerance_items)
    clearance: bpy.props.FloatProperty(name="Spiel (mm)", default=0.1, min=0.0, max=1.0, step=0.05)

    end_type: bpy.props.EnumProperty(name="Enden", items=[("FLAT", "Flach", ""), ("CHAMFER", "Fase 45°", ""), ("RUNOUT", "Auslauf", "")], default="CHAMFER")
    lod_level: bpy.props.EnumProperty(
        name="LOD",
        items=[("PREVIEW", "Preview", "Schnelle Vorschau"), ("FINAL", "Final", "Höhere Qualität"), ("CUSTOM", "Benutzerdefiniert", "Eigene Segmentanzahl")],
        default="FINAL",
    )
    segment_override: bpy.props.IntProperty(name="Segmente/Umdr.", default=48, min=12, max=256)
    preset_key: bpy.props.EnumProperty(
        name="Preset",
        items=[("NONE", "Kein Preset", "")] + [(k, THREAD_PRESETS[k]["name"], "") for k in THREAD_PRESETS.keys()],
        default="NONE",
    )

    ui_language: bpy.props.EnumProperty(name="UI Sprache", items=[("de", "Deutsch", ""), ("en", "English", "")], default="de")

    custom_diameter: bpy.props.FloatProperty(name="Durchmesser (mm)", default=8.0, min=0.1)
    custom_pitch: bpy.props.FloatProperty(name="Steigung (mm)", default=1.5, min=0.1)
    custom_flank_angle: bpy.props.FloatProperty(name="Flankenwinkel", default=60.0, min=0.0, max=120.0)
    custom_profile_type: bpy.props.EnumProperty(name="Profil", items=[("V", "Spitz", ""), ("TRAPEZOID", "Trapez", ""), ("ROUND", "Rund", ""), ("BUTTRESS", "Säge", ""), ("EDISON", "Edison", "")], default="V")


class THREADFORGE_PT_main(bpy.types.Panel):
    bl_label = "Uni-threaded-rod"
    bl_idname = "THREADFORGE_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Uni-threaded-rod"

    def draw(self, context):
        layout = self.layout
        props = context.scene.utg_props

        layout.prop(props, "ui_language", text="UI")
        layout.prop(props, "standard", text=ui_label("standard", props.ui_language))

        if props.standard in THREAD_STANDARDS:
            layout.prop(props, "diameter_enum", text=ui_label("diameter", props.ui_language))
            layout.prop(props, "length", text=ui_label("length", props.ui_language))
            layout.prop(props, "handedness", text=ui_label("handedness", props.ui_language))
            layout.prop(props, "starts", text=ui_label("starts", props.ui_language))

        if props.standard == "CUSTOM":
            layout.prop(props, "custom_diameter")
            layout.prop(props, "custom_pitch")
            layout.prop(props, "custom_flank_angle")
            layout.prop(props, "custom_profile_type")
            layout.prop(props, "starts")
            layout.prop(props, "length")
            layout.prop(props, "handedness")

        layout.separator()
        row = layout.row(align=True)
        row.prop(props, "preset_key", text=ui_label("preset", props.ui_language))
        row.operator("utg.apply_preset", text="", icon="IMPORT")

        layout.prop(props, "material", text=ui_label("material", props.ui_language))
        layout.prop(props, "surface", text=ui_label("surface", props.ui_language))

        layout.separator()
        std_cfg = THREAD_STANDARDS.get(props.standard)
        if props.standard == "CUSTOM" or (std_cfg and std_cfg.get("tolerance_classes")):
            layout.prop(props, "tolerance_class", text=ui_label("tolerance", props.ui_language))
        layout.prop(props, "clearance", text=ui_label("clearance", props.ui_language))
        layout.prop(props, "end_type", text=ui_label("end_type", props.ui_language))
        layout.prop(props, "lod_level", text=ui_label("lod", props.ui_language))
        if props.lod_level == "CUSTOM":
            layout.prop(props, "segment_override", text=ui_label("segment_override", props.ui_language))

        layout.separator()
        layout.operator("utg.create_thread", text=ui_label("create_thread", props.ui_language), icon="MOD_SCREW")


def register_properties():
    bpy.types.Scene.utg_props = bpy.props.PointerProperty(type=UTG_Properties)
