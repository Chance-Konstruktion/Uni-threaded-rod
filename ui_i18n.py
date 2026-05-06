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
        "negative_mode": "Negativ-Modus (Bohrung)",
        "lod": "Mesh-Detail",
        "segment_override": "Segmente/Umdr.",
        "create_thread": "Gewinde erstellen",
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
        "negative_mode": "Negative mode (bore)",
        "lod": "Mesh detail",
        "segment_override": "Segments/turn",
        "create_thread": "Create thread",
    },
}


def ui_label(key: str, language: str = "de") -> str:
    lang = (language or "de").lower()
    table = UI_TEXT.get(lang, UI_TEXT["de"])
    return table.get(key, UI_TEXT["de"].get(key, key))
