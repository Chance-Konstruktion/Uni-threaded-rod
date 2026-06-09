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

import FreeCAD
import FreeCADGui

from freecad_backend.workbench.wb_pulley import create_thread_object


class CreateUniThreadedRodCommand:
    def GetResources(self):
        return {
            "MenuText": "Uni-threaded-rod",
            "ToolTip": "Create a threaded rod from the shared Uni-threaded-rod geometry core",
            "Pixmap": os.path.join(_DIR, "icons", "uni_threaded_rod.svg"),
        }

    def Activated(self):
        doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
        obj = create_thread_object(doc)
        doc.recompute()
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(obj)

    def IsActive(self):
        return True


def register_commands():
    FreeCADGui.addCommand("UniThreadedRod_Create", CreateUniThreadedRodCommand())
