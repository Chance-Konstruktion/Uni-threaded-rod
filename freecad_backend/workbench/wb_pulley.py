import inspect
import os
import sys

try:
    _THIS = __file__
except NameError:
    _THIS = inspect.getfile(inspect.currentframe())
_DIR = os.path.dirname(os.path.abspath(_THIS))
_ROOT = os.path.dirname(os.path.dirname(_DIR))
for _PATH in (_ROOT, os.path.join(_ROOT, "freecad_backend"), _DIR):
    if _PATH not in sys.path:
        sys.path.insert(0, _PATH)

from freecad_backend.backend_freecad import build_thread_shape_from_object


class UniThreadedRodProxy:
    def __init__(self, obj):
        obj.Proxy = self
        self.add_properties(obj)
        self.update_editor_modes(obj)

    def add_properties(self, obj):
        properties = {
            "Standard": ("App::PropertyEnumeration", "Thread", ["METRIC_ISO", "METRIC_FINE", "UNC", "UNF", "TRAPEZOIDAL"]),
            "Diameter": ("App::PropertyString", "Thread", "10"),
            "Length": ("App::PropertyFloat", "Thread", 30.0),
            "ToleranceClass": ("App::PropertyString", "Thread", "6g"),
            "Internal": ("App::PropertyBool", "Thread", False),
            "Starts": ("App::PropertyInteger", "Thread", 1),
            "Clearance": ("App::PropertyFloat", "Thread", 0.0),
            "Handedness": ("App::PropertyEnumeration", "Thread", ["RIGHT", "LEFT"]),
        }
        for name, (kind, group, default) in properties.items():
            if not hasattr(obj, name):
                obj.addProperty(kind, name, group)
                setattr(obj, name, default)

    def update_editor_modes(self, obj):
        standard = getattr(obj, "Standard", "METRIC_ISO")
        has_clearance = bool(getattr(obj, "Internal", False))
        is_threaded = standard != "TRAPEZOIDAL"
        modes = {
            "Clearance": 0 if has_clearance else 2,
            "Starts": 0 if is_threaded else 2,
            "Handedness": 0 if is_threaded else 2,
        }
        for name, mode in modes.items():
            if hasattr(obj, "setEditorMode"):
                obj.setEditorMode(name, mode)

    def onChanged(self, obj, prop):
        if prop in {"Standard", "Internal"}:
            self.update_editor_modes(obj)

    def execute(self, obj):
        self.update_editor_modes(obj)
        obj.Shape = build_thread_shape_from_object(obj)


def create_thread_object(doc):
    obj = doc.addObject("Part::FeaturePython", "UniThreadedRod")
    UniThreadedRodProxy(obj)
    return obj
