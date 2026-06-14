"""Simple DE/EN UI text lookup for the Blender panel.

Keeps labels/tooltips centralized so future localization can be extended
without touching panel layout logic.
"""

UI_TEXT = {
    "de": {
        "standard": "Norm",
        "diameter": "Durchmesser",
        "length": "Gewindestangenlänge",
        "handedness": "Drehrichtung",
        "starts": "Gängigkeit",
        "preset": "Preset",
        "material": "Material",
        "surface": "Oberfläche",
        "tolerance": "Toleranz",
        "clearance": "3D-Druck Spiel (mm)",
        "end_type": "Enden",
        "lod": "Mesh-Detail",
        "segment_override": "Segmente/Umdr.",
        "create_thread": "Gewinde erstellen",
        "error_exception": "{message}",
        "error_preset_not_found": "Preset nicht gefunden.",
        "info_created": "Massive M{diameter:g}x{length:g} Gewindestange ({standard}) erfolgreich erzeugt.",
        "info_no_preset": "Kein Preset ausgewählt.",
        "info_preset_applied": "Preset '{name}' angewendet.",
        "warning_multi_start": "Mehrgängiges Gewinde mit {starts} Gängen erzeugt. Bei sehr hohen Gängigkeiten Manifold prüfen.",
    },
    "en": {
        "standard": "Standard",
        "diameter": "Diameter",
        "length": "Threaded rod length",
        "handedness": "Handedness",
        "starts": "Starts",
        "preset": "Preset",
        "material": "Material",
        "surface": "Surface",
        "tolerance": "Tolerance",
        "clearance": "3D print clearance (mm)",
        "end_type": "Ends",
        "lod": "Mesh detail",
        "segment_override": "Segments/turn",
        "create_thread": "Create thread",
        "error_exception": "{message}",
        "error_preset_not_found": "Preset not found.",
        "info_created": "Solid M{diameter:g}x{length:g} threaded rod ({standard}) created successfully.",
        "info_no_preset": "No preset selected.",
        "info_preset_applied": "Preset '{name}' applied.",
        "warning_multi_start": "Multi-start thread with {starts} starts created. Check manifold quality for very high start counts.",
    },
}


def ui_label(key: str, language: str = "de") -> str:
    lang = (language or "de").lower()
    table = UI_TEXT.get(lang, UI_TEXT["de"])
    return table.get(key, UI_TEXT["de"].get(key, key))
