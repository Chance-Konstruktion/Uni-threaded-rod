# Test-Hinweis

Die Unit-Tests in diesem Ordner sind absichtlich ohne Blender-Laufzeit ausgelegt.

## Empfohlener Lauf

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Warum nicht direkt `pytest`?

Das Repository enthält auf Root-Ebene ein Blender-Addon-`__init__.py`, das `bpy` importiert.
Ohne Blender-Umgebung führt eine pytest-Collection auf Projektebene daher zu `ModuleNotFoundError: bpy`.
