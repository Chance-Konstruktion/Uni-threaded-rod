import inspect
import os
import sys

try:
    _THIS = __file__
except NameError:
    _THIS = inspect.getfile(inspect.currentframe())
_DIR = os.path.dirname(os.path.abspath(_THIS))
for _PATH in (_DIR, os.path.join(_DIR, "freecad_backend"), os.path.join(_DIR, "freecad_backend", "workbench")):
    if _PATH not in sys.path:
        sys.path.insert(0, _PATH)

import FreeCADGui

_ICON = os.path.join(_DIR, "freecad_backend", "workbench", "icons", "uni_threaded_rod.svg")


class UniThreadedRodWorkbench(FreeCADGui.Workbench):
    MenuText = "Uni-threaded-rod"
    ToolTip = "Shared-core FreeCAD workbench for Uni-threaded-rod"

    def Initialize(self):
        from freecad_backend.workbench.wb_commands import register_commands

        register_commands()
        self.appendToolbar("Uni-threaded-rod", ["UniThreadedRod_Create"])
        self.appendMenu("Uni-threaded-rod", ["UniThreadedRod_Create"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"


UniThreadedRodWorkbench.Icon = _ICON
FreeCADGui.addWorkbench(UniThreadedRodWorkbench())
