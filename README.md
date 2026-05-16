# Uni-threaded-rod for Blender

Blender add-on for parametric generation of external solid threaded rods, bayonet couplings, and multi-start threads.

Blender-Add-on zur parametrischen Erzeugung massiver Außengewinde-Stangen, Bajonettkupplungen und mehrgängiger Gewinde.

## Release 0.2 status / Release-0.2-Status

Release 0.2 is ready for tagging when the repository test suite and `ruff check .` pass. It includes external threads for all 26 advertised standards, the STORZ/LAMP_B bayonet mesh path, unified material preset handling in the high-level API, and the removed internal-thread-cutter UI remains out of scope for this rod add-on.

Release 0.2 ist bereit zum Taggen, sobald die Test-Suite und `ruff check .` grün sind. Enthalten sind alle 26 angekündigten Normen, der STORZ/LAMP_B-Bajonett-Meshpfad, vereinheitlichte Material-Presets in der High-Level-API; die entfernte Innengewinde-Cutter-UI bleibt außerhalb des Scopes dieses Stangen-Add-ons.

## Related project / Verwandtes Projekt

[Uni-threaded-sleeve](https://github.com/Chance-Konstruktion/Uni-threaded-sleeve) — counterpart for internal-thread sleeves. Shares the same standards database as this add-on and does not work without `Uni-threaded-rod`.

[Uni-threaded-sleeve](https://github.com/Chance-Konstruktion/Uni-threaded-sleeve) — Gegenstück für Innengewinde-Hülsen. Nutzt dieselbe Normen-Datenbank wie dieses Add-on und ist ohne `Uni-threaded-rod` nicht lauffähig.

## Installation

### English

1. Package the repository as a ZIP, or use the folder as a local add-on directory.
2. In Blender, open `Edit > Preferences > Add-ons`.
3. Select `Install...` and choose the ZIP file or the folder.
4. Enable the `Uni-threaded-rod` add-on.
5. In the 3D viewport, open the sidebar with `N` and select `Uni-threaded-rod`.

### Deutsch

1. Repository als ZIP packen oder den Ordner als lokalen Add-on-Ordner verwenden.
2. In Blender `Edit > Preferences > Add-ons` öffnen.
3. `Install...` wählen und die ZIP-Datei oder den Ordner auswählen.
4. Das Add-on `Uni-threaded-rod` aktivieren.
5. Im 3D-Viewport die Sidebar mit `N` öffnen und `Uni-threaded-rod` auswählen.

## Minimal example / Minimalbeispiel

### Blender UI

1. Select standard `METRIC_ISO` / Standard `METRIC_ISO` auswählen.
2. Pick nominal size `M10` / Nenngröße `M10` auswählen.
3. Set length to `50 mm` / Länge `50 mm` setzen.
4. Run `Create Thread` / `Create Thread` ausführen.

### Python API

```python
from Uni_threaded_rod.api import thread

result = thread("M10", fit="6g/6H", material="8.8", length=50)
print(result["diameter_mm"], result["pitch_mm"])
```

## Supported standards / Unterstützte Standards

| Key | Name | Standard | Unit | Profile |
| --- | --- | --- | --- | --- |
| `METRIC_ISO` | Metric ISO coarse / Metrisches ISO-Regelgewinde | DIN 13 / ISO 68-1 | mm | V |
| `METRIC_FINE` | Metric ISO fine / Metrisches ISO-Feingewinde | DIN 13 / ISO 965-1 | mm | V |
| `WHITWORTH_BSW` | Whitworth | BS 84 | inch | V |
| `UNC` | Unified National Coarse | ANSI/ASME B1.1 | inch | V |
| `UNF` | Unified National Fine | ANSI/ASME B1.1 | inch | V |
| `PIPE_G` | Pipe thread, parallel / Rohrgewinde, zylindrisch | DIN EN ISO 228 | inch | V |
| `TRAPEZOIDAL` | Trapezoidal / Trapezgewinde | DIN 103 | mm | Trapezoid |
| `BUTTRESS` | Buttress / Sägengewinde | DIN 513 | mm | Buttress |
| `ROUND` | Round / Rundgewinde | DIN 405 | mm | Round |
| `ACME` | ACME | ASME B1.5 | inch | Trapezoid |
| `NPT` | National Pipe Taper | ANSI B1.20.1 | inch | V, tapered |
| `PG` | Conduit thread / Panzergewinde | DIN 40430 | mm | V |
| `EDISON` | Edison lamp socket / Edison-Lampensockel (E10/E14/E27/E40) | IEC 60061-1 | mm | Edison (sine) |
| `UNEF` | Unified National Extra Fine | ANSI/ASME B1.1 | inch | V |
| `UNS` | Unified National Special | ANSI/ASME B1.1 | inch | V |
| `PIPE_R` | Pipe thread, tapered / Rohrgewinde, kegelig | DIN EN 10226 | inch | V, tapered |
| `BSPT` | British Standard Pipe Taper | BS 21 / ISO 7-1 | inch | V, tapered |
| `BSF` | British Standard Fine | BS 84 | inch | V |
| `METRIC_TRAPEZOIDAL_FINE` | Metric fine trapezoidal / Metrisches Feintrapezgewinde | DIN 380 | mm | Trapezoid |
| `STUB_ACME` | Stub ACME | ASME B1.8 | inch | Trapezoid |
| `KNUCKLE` | Knuckle (round, US) | ASME B1.9 | inch | Round |
| `SPARK_PLUG` | Spark plug / Zündkerzengewinde | ISO 28741 | mm | V |
| `STORZ` | Storz coupling (fire hose) / Storz-Festkupplung (Feuerwehr) | DIN 14318 | mm | Bayonet (no thread) |
| `CABLE_GLAND_M` | Cable gland, metric / Kabelverschraubung, metrisch | DIN EN 60423 / IEC 60423 | mm | V |
| `CONDUIT_PG` | Conduit thread / Panzergewinde Elektroinstallation | DIN 40430 | mm | V |
| `LAMP_B` | Bayonet lamp socket / Bajonett-/Stiftsockel-Gewinde | IEC 60061-1 | mm | Round |

## License / Lizenz

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). The full license text is in the [`LICENSE`](LICENSE) file.

Dieses Projekt steht unter der GNU General Public License v3.0 (GPL-3.0). Der vollständige Lizenztext befindet sich in der Datei [`LICENSE`](LICENSE).
