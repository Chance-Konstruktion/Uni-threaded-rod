from .params import FreeCADThreadParameters


def build_thread_shape(params):
    import Part
    from FreeCAD import Vector

    profile = params.profile()
    axial_scale = -1.0 if params.handedness.upper() == "LEFT" else 1.0
    turns = max(params.length_mm / params.pitch_mm, 0.05)
    helix = Part.makeHelix(params.pitch_mm * axial_scale, params.length_mm, params.diameter_mm / 2.0)
    profile_points = [Vector(point.x, 0.0, point.y) for point in profile]
    if profile_points[0] != profile_points[-1]:
        profile_points.append(profile_points[0])
    wire = Part.makePolygon(profile_points)
    face = Part.Face(wire)
    shell = Part.Wire(helix).makePipeShell([face], True, True)
    solid = Part.Solid(shell) if hasattr(Part, "Solid") else shell
    solid.Label = f"{params.standard} {params.diameter_token}x{params.length_mm:g}"
    solid.UserData = {"turns": turns, "starts": params.starts}
    return solid


def build_thread_shape_from_object(obj):
    params = FreeCADThreadParameters.from_standard(
        obj.Standard,
        obj.Diameter,
        obj.Length,
        tolerance_class=obj.ToleranceClass,
        internal=obj.Internal,
        starts=obj.Starts,
        clearance=obj.Clearance,
        handedness=obj.Handedness,
    )
    return build_thread_shape(params)
