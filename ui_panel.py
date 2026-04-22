import bpy

from .database import MATERIAL_PRESETS, THREAD_STANDARDS, get_diameter_items_for_standard


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
    all_items = ext + inner
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
    length: bpy.props.FloatProperty(name="Länge", default=50.0, min=0.1, max=1000.0, unit="LENGTH")
    handedness: bpy.props.EnumProperty(name="Drehrichtung", items=[("RIGHT", "Rechtsgewinde", ""), ("LEFT", "Linksgewinde", "")], default="RIGHT")
    starts: bpy.props.IntProperty(name="Gängigkeit", default=1, min=1, max=8)

    material: bpy.props.EnumProperty(name="Material", items=[(k, MATERIAL_PRESETS[k]["name"], "") for k in MATERIAL_PRESETS.keys()], default="STEEL_8.8")
    surface: bpy.props.EnumProperty(name="Oberfläche", items=[("NONE", "Unbehandelt", ""), ("ZINC", "Verzinkt", ""), ("HOT_DIP", "Feuerverzinkt", "")], default="NONE")

    tolerance_class: bpy.props.EnumProperty(name="Toleranzklasse", items=get_tolerance_items)
    clearance: bpy.props.FloatProperty(name="Spiel", default=0.1, min=0.0, max=1.0, step=0.05, unit="LENGTH")

    end_type: bpy.props.EnumProperty(name="Enden", items=[("FLAT", "Flach", ""), ("CHAMFER", "Fase 45°", ""), ("RUNOUT", "Auslauf", "")], default="CHAMFER")
    negative_mode: bpy.props.BoolProperty(name="Negativ-Modus", description="Erzeugt Bohrung statt Stange (Boolesche Differenz)", default=False)

    custom_diameter: bpy.props.FloatProperty(name="Durchmesser", default=10.0, min=0.1)
    custom_pitch: bpy.props.FloatProperty(name="Steigung", default=1.5, min=0.1)
    custom_flank_angle: bpy.props.FloatProperty(name="Flankenwinkel", default=60.0, min=0.0, max=120.0)
    custom_profile_type: bpy.props.EnumProperty(name="Profil", items=[("V", "Spitz", ""), ("TRAPEZOID", "Trapez", ""), ("ROUND", "Rund", ""), ("BUTTRESS", "Säge", ""), ("GOTHIC", "Gothic/KGT", "")], default="V")


class THREADFORGE_PT_main(bpy.types.Panel):
    bl_label = "Uni-threaded-rod"
    bl_idname = "THREADFORGE_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Uni-threaded-rod"

    def draw(self, context):
        layout = self.layout
        props = context.scene.utg_props

        layout.prop(props, "standard", text="Norm")

        if props.standard in THREAD_STANDARDS:
            layout.prop(props, "diameter_enum", text="Durchmesser")
            layout.prop(props, "length", text="Länge")
            layout.prop(props, "handedness", text="Drehrichtung")
            layout.prop(props, "starts", text="Gängigkeit")

        if props.standard == "CUSTOM":
            layout.prop(props, "custom_diameter")
            layout.prop(props, "custom_pitch")
            layout.prop(props, "custom_flank_angle")
            layout.prop(props, "custom_profile_type")
            layout.prop(props, "starts")
            layout.prop(props, "length")
            layout.prop(props, "handedness")

        layout.separator()
        layout.prop(props, "material", text="Material")
        layout.prop(props, "surface", text="Oberfläche")

        layout.separator()
        layout.prop(props, "tolerance_class", text="Toleranz")
        layout.prop(props, "clearance", text="3D-Druck Spiel (mm)")
        layout.prop(props, "end_type", text="Enden")
        layout.prop(props, "negative_mode", text="Negativ-Modus (Bohrung)")

        layout.separator()
        layout.operator("utg.create_thread", text="Gewinde erstellen", icon="MOD_SCREW")
        layout.operator("utg.create_ball_screw", text="Kugelgewindetrieb", icon="CON_ROTLIKE")


def register_properties():
    bpy.types.Scene.utg_props = bpy.props.PointerProperty(type=UTG_Properties)
