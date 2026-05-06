import importlib.util

bl_info = {
    "name": "Uni-threaded-rod",
    "author": "Ihr Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Uni-threaded-rod",
    "description": "Erzeugt normgerechte und benutzerdefinierte Gewinde",
    "category": "Mesh",
}

HAS_BPY = importlib.util.find_spec("bpy") is not None

if HAS_BPY:
    import bpy

    from .database import THREAD_PRESETS, THREAD_STANDARDS, resolve_thread_parameters
    from .geometry_engine import generate_profile
    from .mechanical_validation import validate_thread_input
    from .mesh_builder import (
        apply_boolean_cutter,
        apply_material,
        create_thread_mesh,
    )
    from .ui_panel import THREADFORGE_PT_main, UTG_Properties, register_properties

    def _create_standard_from_custom(props):
        return {
            "profile_type": props.custom_profile_type,
            "flank_angle": props.custom_flank_angle,
            "d2_formula": lambda d, p: d - 0.5 * p,
            "d3_formula": lambda d, p: d - p,
        }


    def _report_ratio_warnings(operator, ratio_warnings):
        for msg in dict.fromkeys(ratio_warnings):
            operator.report({"WARNING"}, msg)


    def _validate_parameters(diameter, pitch, length, starts, clearance=0.0, standard_key="METRIC_ISO"):
        result = validate_thread_input(
            diameter,
            pitch,
            length,
            starts,
            clearance=clearance,
            standard_key=standard_key,
        )
        return None if result.ok else result.message


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
                standard_key = "CUSTOM"
            else:
                custom_std = None
                standard_key = props.standard
                try:
                    diameter, pitch = resolve_thread_parameters(standard_key, props.diameter_enum)
                except Exception as exc:
                    self.report({"ERROR"}, str(exc))
                    return {"CANCELLED"}

            validation_error = _validate_parameters(
                diameter,
                pitch,
                props.length,
                props.starts,
                props.clearance,
                standard_key=standard_key,
            )
            if validation_error:
                self.report({"ERROR"}, validation_error)
                return {"CANCELLED"}

            negative_mode_active = bool(props.negative_mode and target_for_boolean)
            if props.negative_mode and not negative_mode_active:
                self.report({"INFO"}, "Negativ-Modus deaktiviert: Kein aktives Zielobjekt gefunden, erzeuge stattdessen Gewindestab.")

            if props.starts > 2:
                self.report(
                    {"WARNING"},
                    f"Mehrgängiges Gewinde mit {props.starts} Gängen erzeugt. Bei sehr hohen Gängigkeiten Manifold prüfen.",
                )

            standard = custom_std if custom_std is not None else THREAD_STANDARDS.get(standard_key, {})
            std_tol = standard.get("tolerance_classes", {})
            internal_classes = {str(v).upper() for v in std_tol.get("internal", [])}
            tolerance_is_internal = str(props.tolerance_class).upper() in internal_classes

            if props.tolerance_class == "N_A":
                self.report({"ERROR"}, "Für diese Norm sind keine Innengewinde-Toleranzklassen definiert.")
                return {"CANCELLED"}

            if tolerance_is_internal and not negative_mode_active:
                self.report(
                    {"ERROR"},
                    "Innengewinde-Toleranzen sind nur im aktiven Negativ-Modus als Bohrungs-Cutter erlaubt.",
                )
                return {"CANCELLED"}

            # Harte Kernregel: Das Primärobjekt ist immer eine massive
            # Außengewindestange. Ein internes/aufgeweitetes Profil ist nur als
            # temporärer Boolean-Difference-Cutter erlaubt, niemals als Default.
            profile_internal = bool(negative_mode_active)

            try:
                profile, ratio_warnings = generate_profile(
                    standard_key,
                    diameter,
                    pitch,
                    tolerance_class=props.tolerance_class,
                    internal=profile_internal,
                    clearance=props.clearance,
                    return_warnings=True,
                    standard=custom_std,
                )
                _report_ratio_warnings(self, ratio_warnings)

                bm = create_thread_mesh(
                    profile_points=profile,
                    diameter=diameter,
                    pitch=pitch,
                    length=props.length,
                    starts=props.starts,
                    handedness=props.handedness,
                    end_type=props.end_type,
                    taper_ratio=standard.get("special_params", {}).get("taper_ratio", 0.0),
                    lod_level=props.lod_level,
                    segment_override=props.segment_override,
                )
            except ValueError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}

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

            report_standard = props.standard if custom_std is not None else standard_key

            if negative_mode_active:
                self.report(
                    {"INFO"},
                    f"Bohrungs-Cutter M{diameter:g}x{props.length:g} ({report_standard}) erfolgreich angewendet.",
                )
            else:
                self.report(
                    {"INFO"},
                    f"Massive M{diameter:g}x{props.length:g} Gewindestange ({report_standard}) erfolgreich erzeugt.",
                )

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
else:
    def register():
        return None

    def unregister():
        return None
