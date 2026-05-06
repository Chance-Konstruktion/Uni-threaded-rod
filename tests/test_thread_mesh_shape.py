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

    def test_m10x15_mesh_is_single_solid_rod(self):
        diameter = 10.0
        pitch = 1.5
        length = 30.0
        profile = self.geometry_engine.generate_profile("METRIC_ISO", diameter, pitch)
        bm = self.mesh_builder.create_thread_mesh("M10x1.5", profile, diameter, pitch, length, end_type="FLAT")
        write_obj(bm)

        d3 = self.database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter, pitch)
        expected = math.pi * (d3 / 2.0) ** 2 * length
        volume = abs(sum(face_volume(face) for face in bm.faces))
        failures = []

        if not all(edge.is_manifold for edge in bm.edges):
            failures.append("(a) non-manifold edges")
        if not all(single_loop_at_z(bm, z) for z in sorted({round(vert.co.z, 9) for vert in bm.verts})):
            failures.append("(b) not exactly one closed polygon per z-section")
        if not expected * 0.8 <= volume <= expected * 1.2:
            failures.append(f"(c) volume {volume:.3f}, expected {expected:.3f}")

        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
