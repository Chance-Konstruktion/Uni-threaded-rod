from dataclasses import dataclass

from .core_loader import core_module


def _database():
    return core_module("database")


@dataclass(frozen=True)
class FreeCADThreadParameters:
    standard: str
    diameter_token: str
    diameter_mm: float
    pitch_mm: float
    length_mm: float
    tolerance_class: str
    internal: bool = False
    starts: int = 1
    clearance_mm: float = 0.0
    handedness: str = "RIGHT"

    @classmethod
    def from_standard(
        cls,
        standard,
        diameter_token,
        length,
        tolerance_class=None,
        internal=False,
        starts=1,
        clearance=0.0,
        handedness="RIGHT",
    ):
        database = _database()
        diameter_mm, pitch_mm = database.resolve_thread_parameters(standard, str(diameter_token))
        fit = tolerance_class or database.get_default_tolerance_class(standard, internal=internal)
        return cls(
            standard=str(standard),
            diameter_token=str(diameter_token),
            diameter_mm=float(diameter_mm),
            pitch_mm=float(pitch_mm),
            length_mm=float(length),
            tolerance_class=str(fit),
            internal=bool(internal),
            starts=int(starts),
            clearance_mm=float(clearance),
            handedness=str(handedness),
        )

    def profile(self):
        geometry_engine = core_module("geometry_engine")
        return geometry_engine.generate_profile(
            self.standard,
            self.diameter_mm,
            self.pitch_mm,
            tolerance_class=self.tolerance_class,
            internal=self.internal,
            clearance=self.clearance_mm,
        )
