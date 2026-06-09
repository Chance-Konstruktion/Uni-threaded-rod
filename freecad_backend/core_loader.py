import importlib.util
import pathlib
import sys
import types

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PACKAGE_NAME = "utg_freecad_core"


def core_module(module_name):
    if _PACKAGE_NAME not in sys.modules:
        package = types.ModuleType(_PACKAGE_NAME)
        package.__path__ = [str(_ROOT)]
        sys.modules[_PACKAGE_NAME] = package

    full_name = f"{_PACKAGE_NAME}.{module_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]

    spec = importlib.util.spec_from_file_location(full_name, _ROOT / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module
