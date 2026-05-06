import importlib.util, math, pathlib, sys, tempfile, types, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class Vec:
    def __init__(self, xyz): self.x, self.y, self.z = map(float, xyz)
    def __sub__(self, o): return Vec((self.x-o.x, self.y-o.y, self.z-o.z))
    @property
    def length(self): return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)
    def normalize(self):
        l = self.length
        if l: self.x, self.y, self.z = self.x/l, self.y/l, self.z/l
    def dot(self, o): return self.x*o.x+self.y*o.y+self.z*o.z

def cross(a, b): return Vec((a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x))

class Seq(list): pass
class Vert:
    def __init__(self, co): self.co = co
class Edge:
    def __init__(self, a, b): self.verts, self.faces = (a, b), []
    @property
    def is_manifold(self): return len(self.faces) == 2
class Face:
    def __init__(self, verts): self.verts = tuple(verts)
    @property
    def normal(self):
        n = cross(self.verts[1].co - self.verts[0].co, self.verts[2].co - self.verts[0].co); n.normalize(); return n
    def normal_flip(self): self.verts = tuple(reversed(self.verts))
    def calc_center_median(self):
        return Vec((sum(v.co.x for v in self.verts)/len(self.verts), sum(v.co.y for v in self.verts)/len(self.verts), sum(v.co.z for v in self.verts)/len(self.verts)))
class BMesh:
    def __init__(self):
        self.verts, self.edges, self.faces, self._edge_map = Seq(), Seq(), Seq(), {}
        self.verts.new, self.faces.new = self._new_vert, self._new_face
    def _new_vert(self, co):
        v = Vert(co); self.verts.append(v); return v
    def _new_face(self, verts):
        f = Face(verts); self.faces.append(f)
        for a, b in zip(f.verts, f.verts[1:] + f.verts[:1]):
            key = tuple(sorted((id(a), id(b)))); e = self._edge_map.get(key)
            if not e: e = self._edge_map[key] = Edge(a, b); self.edges.append(e)
            e.faces.append(f)
        return f
    def normal_update(self): pass
    def free(self): pass

def load(name):
    if "utg" not in sys.modules:
        pkg = types.ModuleType("utg"); pkg.__path__ = [str(ROOT)]; sys.modules["utg"] = pkg
    spec = importlib.util.spec_from_file_location(f"utg.{name}", ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); sys.modules[f"utg.{name}"] = mod; spec.loader.exec_module(mod); return mod

def single_loop_at_z(bm, z):
    verts = {v for v in bm.verts if abs(v.co.z - z) < 1e-8 and math.hypot(v.co.x, v.co.y) > 1e-8}
    edges = [(a, b) for e in bm.edges for a, b in [e.verts] if a in verts and b in verts]
    degree, seen, stack = {v: 0 for v in verts}, set(), [next(iter(verts))]
    for a, b in edges: degree[a] += 1; degree[b] += 1
    while stack:
        v = stack.pop(); seen.add(v)
        stack += [w for a, b in edges for w in ((b,) if a is v else (a,) if b is v else ()) if w not in seen]
    return len(edges) == len(verts) and all(v == 2 for v in degree.values()) and seen == verts

def face_volume(face):
    a, total = face.verts[0].co, 0.0
    for i in range(1, len(face.verts) - 1): total += a.dot(cross(face.verts[i].co, face.verts[i + 1].co)) / 6.0
    return total

def write_obj(bm):
    path, index = pathlib.Path(tempfile.gettempdir()) / "utg_m10x15_thread.obj", {v: i + 1 for i, v in enumerate(bm.verts)}
    path.write_text("".join([f"v {v.co.x} {v.co.y} {v.co.z}\n" for v in bm.verts] + ["f " + " ".join(str(index[v]) for v in f.verts) + "\n" for f in bm.faces]))

class ThreadMeshShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules.setdefault("bpy", types.ModuleType("bpy"))
        sys.modules["mathutils"] = types.SimpleNamespace(Vector=Vec)
        sys.modules["bmesh"] = types.SimpleNamespace(new=BMesh, ops=types.SimpleNamespace(remove_doubles=lambda *a, **k: None, holes_fill=lambda *a, **k: None))
        cls.database, cls.geometry_engine, cls.mesh_builder = load("database"), load("geometry_engine"), load("mesh_builder")
    def test_m10x15_mesh_is_single_solid_rod(self):
        d, p, length = 10.0, 1.5, 30.0
        bm = self.mesh_builder.create_thread_mesh("M10x1.5", self.geometry_engine.generate_profile("METRIC_ISO", d, p), d, p, length, end_type="FLAT")
        write_obj(bm)
        d3 = self.database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](d, p)
        expected, volume = math.pi * (d3 / 2.0) ** 2 * length, abs(sum(face_volume(f) for f in bm.faces))
        failures = []
        if not all(e.is_manifold for e in bm.edges): failures.append("(a) non-manifold edges")
        if not all(single_loop_at_z(bm, z) for z in sorted({round(v.co.z, 9) for v in bm.verts})): failures.append("(b) not exactly one closed polygon per z-section")
        if not expected * 0.8 <= volume <= expected * 1.2: failures.append(f"(c) volume {volume:.3f}, expected {expected:.3f}")
        self.assertEqual([], failures)

if __name__ == "__main__": unittest.main()
