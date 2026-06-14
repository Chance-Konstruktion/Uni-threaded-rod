import importlib.util
import math
import pathlib
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Vec:
    def __init__(self, xyz):
        self.x, self.y, self.z = map(float, xyz)

    def __sub__(self, other):
        return Vec((self.x - other.x, self.y - other.y, self.z - other.z))

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        vector_length = self.length
        if vector_length:
            self.x /= vector_length
            self.y /= vector_length
            self.z /= vector_length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z


def cross(a, b):
    return Vec((a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x))


class Seq(list):
    pass


class Vert:
    def __init__(self, co):
        self.co = co


class Edge:
    def __init__(self, a, b):
        self.verts = (a, b)
        self.faces = []

    @property
    def is_manifold(self):
        return len(self.faces) == 2


class Face:
    def __init__(self, verts):
        self.verts = tuple(verts)

    @property
    def normal(self):
        normal = cross(self.verts[1].co - self.verts[0].co, self.verts[2].co - self.verts[0].co)
        normal.normalize()
        return normal

    def normal_flip(self):
        self.verts = tuple(reversed(self.verts))

    def calc_center_median(self):
        count = len(self.verts)
        return Vec(
            (
                sum(v.co.x for v in self.verts) / count,
                sum(v.co.y for v in self.verts) / count,
                sum(v.co.z for v in self.verts) / count,
            )
        )


class BMesh:
    def __init__(self):
        self.verts = Seq()
        self.edges = Seq()
        self.faces = Seq()
        self._edge_map = {}
        self.verts.new = self._new_vert
        self.faces.new = self._new_face

    def _new_vert(self, co):
        vert = Vert(co)
        self.verts.append(vert)
        return vert

    def _new_face(self, verts):
        face = Face(verts)
        self.faces.append(face)
        for first, second in zip(face.verts, face.verts[1:] + face.verts[:1]):
            key = tuple(sorted((id(first), id(second))))
            edge = self._edge_map.get(key)
            if not edge:
                edge = Edge(first, second)
                self._edge_map[key] = edge
                self.edges.append(edge)
            edge.faces.append(face)
        return face

    def normal_update(self):
        pass

    def free(self):
        pass


def load(name):
    if "utg" not in sys.modules:
        pkg = types.ModuleType("utg")
        pkg.__path__ = [str(ROOT)]
        sys.modules["utg"] = pkg
    spec = importlib.util.spec_from_file_location(f"utg.{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"utg.{name}"] = module
    spec.loader.exec_module(module)
    return module


def single_loop_at_z(bm, z):
    verts = {
        vert
        for vert in bm.verts
        if abs(vert.co.z - z) < 1e-8 and math.hypot(vert.co.x, vert.co.y) > 1e-8
    }
    edges = [edge.verts for edge in bm.edges if edge.verts[0] in verts and edge.verts[1] in verts]
    degree = {vert: 0 for vert in verts}
    for first, second in edges:
        degree[first] += 1
        degree[second] += 1

    seen = set()
    stack = [next(iter(verts))]
    while stack:
        vert = stack.pop()
        seen.add(vert)
        for first, second in edges:
            if first is vert and second not in seen:
                stack.append(second)
            elif second is vert and first not in seen:
                stack.append(first)

    return len(edges) == len(verts) and all(value == 2 for value in degree.values()) and seen == verts


def face_volume(face):
    anchor = face.verts[0].co
    total = 0.0
    for index in range(1, len(face.verts) - 1):
        total += anchor.dot(cross(face.verts[index].co, face.verts[index + 1].co)) / 6.0
    return total


def write_obj(bm):
    path = pathlib.Path(tempfile.gettempdir()) / "utg_m10x15_thread.obj"
    index = {vert: i + 1 for i, vert in enumerate(bm.verts)}
    lines = [f"v {vert.co.x} {vert.co.y} {vert.co.z}\n" for vert in bm.verts]
    lines.extend("f " + " ".join(str(index[vert]) for vert in face.verts) + "\n" for face in bm.faces)
    path.write_text("".join(lines))


class ThreadMeshShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules.setdefault("bpy", types.ModuleType("bpy"))
        sys.modules["mathutils"] = types.SimpleNamespace(Vector=Vec)
        sys.modules["bmesh"] = types.SimpleNamespace(
            new=BMesh,
            ops=types.SimpleNamespace(remove_doubles=lambda *args, **kwargs: None, holes_fill=lambda *args, **kwargs: None),
        )
        cls.database = load("database")
        cls.geometry_engine = load("geometry_engine")
        cls.mesh_builder = load("mesh_builder")


    def test_chamfer_end_type_changes_top_ring_radius(self):
        diameter = 10.0
        pitch = 1.5
        length = 30.0
        profile = self.geometry_engine.generate_profile("METRIC_ISO", diameter, pitch)

        flat = self.mesh_builder.create_thread_mesh(profile, diameter, pitch, length, end_type="FLAT")
        chamfered = self.mesh_builder.create_thread_mesh(profile, diameter, pitch, length, end_type="CHAMFER")

        blender_length = length / 1000.0
        flat_top_radius = max(math.hypot(vert.co.x, vert.co.y) for vert in flat.verts if abs(vert.co.z - blender_length) < 1e-8)
        chamfered_top_radius = max(
            math.hypot(vert.co.x, vert.co.y) for vert in chamfered.verts if abs(vert.co.z - blender_length) < 1e-8
        )

        self.assertLess(chamfered_top_radius, flat_top_radius)


    def test_mesh_coordinates_convert_mm_inputs_to_blender_meters(self):
        diameter = 10.0
        pitch = 1.5
        length = 30.0
        profile = self.geometry_engine.generate_profile("METRIC_ISO", diameter, pitch)

        bm = self.mesh_builder.create_thread_mesh(profile, diameter, pitch, length, end_type="FLAT")

        max_diameter = 2.0 * max(math.hypot(vert.co.x, vert.co.y) for vert in bm.verts)
        max_length = max(vert.co.z for vert in bm.verts)
        self.assertAlmostEqual(max_diameter, diameter / 1000.0, delta=0.0002)
        self.assertAlmostEqual(max_length, length / 1000.0, places=9)

    def test_m10x15_mesh_is_single_solid_rod(self):
        diameter = 10.0
        pitch = 1.5
        length = 30.0
        profile = self.geometry_engine.generate_profile("METRIC_ISO", diameter, pitch)
        d3 = self.database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter, pitch)
        expected = math.pi * (d3 / 2.0) ** 2 * length / 1_000_000_000.0

        for starts in (1, 2, 4):
            with self.subTest(starts=starts):
                bm = self.mesh_builder.create_thread_mesh(profile, diameter, pitch, length, starts=starts, end_type="FLAT")
                write_obj(bm)

                volume = abs(sum(face_volume(face) for face in bm.faces))
                failures = []

                if not all(edge.is_manifold for edge in bm.edges):
                    failures.append("(a) non-manifold edges")
                if not all(single_loop_at_z(bm, z) for z in sorted({round(vert.co.z, 9) for vert in bm.verts})):
                    failures.append("(b) not exactly one closed polygon per z-section")
                if not expected * 0.8 <= volume <= expected * 1.2:
                    failures.append(f"(c) volume {volume:.3f}, expected {expected:.3f}")

                self.assertEqual([], failures)


    def test_tapered_pipe_mesh_uses_large_end_at_start(self):
        diameter = 21.3
        pitch = 1.814
        length = 32.0
        taper_ratio = 1 / 16
        profile = self.geometry_engine.generate_profile("NPT", diameter, pitch, tolerance_class="L1")

        bm = self.mesh_builder.create_thread_mesh(
            profile, diameter, pitch, length, end_type="FLAT", taper_ratio=taper_ratio
        )

        start_radius = max(math.hypot(vert.co.x, vert.co.y) for vert in bm.verts if abs(vert.co.z) < 1e-8)
        end_z = length / 1000.0
        end_radius = max(math.hypot(vert.co.x, vert.co.y) for vert in bm.verts if abs(vert.co.z - end_z) < 1e-8)
        self.assertAlmostEqual(start_radius - end_radius, 0.5 * taper_ratio * length / 1000.0, delta=0.00015)


if __name__ == "__main__":
    unittest.main()
