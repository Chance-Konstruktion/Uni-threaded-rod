import bpy

from .database import MATERIAL_PRESETS, THREAD_STANDARDS


def get_diameter_items(self, context):
    std = context.scene.utg_props.standard
    if std == "CUSTOM" or std not in THREAD_STANDARDS:
        return [("0", "---", "")]
    diam_map = THREAD_STANDARDS[std]["diam_pitch_map"]
    return [(str(d), str(d), "") for d in diam_map.keys()]


class UTG_Properties(bpy.types.PropertyGroup):
    standard: bpy.props.EnumProperty(
        name="Norm",
        items=[(k, THREAD_STANDARDS[k]["name"], "") for k in THREAD_STANDARDS.keys()] + [("CUSTOM", "Benutzerdefiniert", "Freie Parameter")],
        default="METRIC_ISO",
    )
    diameter_enum: bpy.props.EnumProperty(name="Durchmesser", items=get_diameter_items)
    length: bpy.props.FloatProperty(name="Länge", default=50.0, min=0.1, max=1000.0, unit="LENGTH")
    handedness: bpy.props.EnumProperty(name="Drehrichtung", items=[("RIGHT", "Rechtsgewinde", ""), ("LEFT", "Linksgewinde", "")])
    material: bpy.props.EnumProperty(name="Material", items=[(k, MATERIAL_PRESETS[k]["name"], "") for k in MATERIAL_PRESETS.keys()])
    surface: bpy.props.EnumProperty(
        name="Oberfläche",
        items=[("NONE", "Unbehandelt", ""), ("ZINC", "Verzinkt", ""), ("HOT_DIP", "Feuerverzinkt", "")],
    )
    tolerance_class: bpy.props.EnumProperty(
        name="Toleranzklasse",
        items=[("6g", "6g (Standard)", ""), ("4g", "4g (fein)", ""), ("8g", "8g (grob)", "")],
    )
    clearance: bpy.props.FloatProperty(name="Spiel", default=0.1, min=0.0, max=1.0, step=0.05, unit="LENGTH")
    end_type: bpy.props.EnumProperty(name="Enden", items=[("FLAT", "Flach", ""), ("CHAMFER", "Fase 45°", ""), ("RUNOUT", "Auslauf", "")])
    negative_mode: bpy.props.BoolProperty(name="Negativ-Modus", description="Erzeugt Bohrung statt Stange (Boolesche Differenz)")

    custom_diameter: bpy.props.FloatProperty(name="Durchmesser", default=10.0, min=0.1)
    custom_pitch: bpy.props.FloatProperty(name="Steigung", default=1.5, min=0.1)
    custom_flank_angle: bpy.props.FloatProperty(name="Flankenwinkel", default=60.0, min=0.0, max=120.0)
    custom_profile_type: bpy.props.EnumProperty(name="Profil", items=[("V", "Spitz", ""), ("TRAPEZOID", "Trapez", ""), ("ROUND", "Rund", "")])
    custom_starts: bpy.props.IntProperty(name="Gängigkeit", default=1, min=1, max=4)


class THREADFORGE_PT_main(bpy.types.Panel):
    bl_label = "Universal Thread Generator"
    bl_idname = "THREADFORGE_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ThreadForge"

    def draw(self, context):
        layout = self.layout
        props = context.scene.utg_props

        layout.prop(props, "standard", text="Norm")
        std = props.standard

        if std in THREAD_STANDARDS:
            layout.prop(props, "diameter_enum", text="Durchmesser")
            layout.prop(props, "length", text="Länge")
            layout.prop(props, "handedness", text="Drehrichtung")

        if std == "CUSTOM":
            layout.prop(props, "custom_diameter")
            layout.prop(props, "custom_pitch")
            layout.prop(props, "custom_flank_angle")
            layout.prop(props, "custom_profile_type")
            layout.prop(props, "custom_starts")

        layout.prop(props, "material", text="Material")
        layout.prop(props, "surface", text="Oberfläche")
        layout.prop(props, "tolerance_class", text="Toleranz")
        layout.prop(props, "clearance", text="3D-Druck Spiel (mm)")
        layout.prop(props, "end_type", text="Enden")
        layout.prop(props, "negative_mode", text="Negativ-Modus (Bohrung)")

        layout.operator("utg.create_thread", text="Gewinde erstellen")
        layout.operator("utg.create_ball_screw", text="Kugelgewindetrieb")


def register_properties():
    bpy.types.Scene.utg_props = bpy.props.PointerProperty(type=UTG_Properties)
