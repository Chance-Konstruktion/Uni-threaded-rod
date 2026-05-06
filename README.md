# Uni-threaded-rod for Blender

Blender-Add-on zur parametrischen Erzeugung von Außengewinden, Innengewinde-Cuttern, mehrgängigen Gewinden und Kugelgewindetrieb-Basisgeometrie.

## Installation

1. Repository als ZIP packen oder den Ordner als lokalen Add-on-Ordner verwenden.
2. In Blender `Edit > Preferences > Add-ons` öffnen.
3. `Install...` wählen und die ZIP-Datei oder den Ordner auswählen.
4. Das Add-on `Uni-threaded-rod` aktivieren.
5. Im 3D-Viewport die Sidebar mit `N` öffnen und `Uni-threaded-rod` auswählen.

## Minimalbeispiel

### Blender-UI

1. Standard `METRIC_ISO` auswählen.
2. Nenngröße `M10` auswählen.
3. Länge `50 mm` setzen.
4. `Create Thread` ausführen.

### Python-API

```python
from Uni_threaded_rod.api import thread

result = thread("M10", fit="6g/6H", material="8.8", length=50)
print(result["diameter_mm"], result["pitch_mm"])
```

## Unterstützte Standards

| Schlüssel | Name | Normbezug | Einheit | Profil |
| --- | --- | --- | --- | --- |
| `METRIC_ISO` | Metrisches ISO-Regelgewinde | DIN 13 / ISO 68-1 | mm | V |
| `METRIC_FINE` | Metrisches ISO-Feingewinde | DIN 13 / ISO 965-1 | mm | V |
| `WHITWORTH_BSW` | Whitworth-Gewinde | BS 84 | inch | V |
| `UNC` | Unified National Coarse | ANSI/ASME B1.1 | inch | V |
| `UNF` | Unified National Fine | ANSI/ASME B1.1 | inch | V |
| `PIPE_G` | Rohrgewinde, zylindrisch | DIN EN ISO 228 | inch | V |
| `TRAPEZOIDAL` | Trapezgewinde | DIN 103 | mm | Trapez |
| `BUTTRESS` | Sägengewinde | DIN 513 | mm | Buttress |
| `ROUND` | Rundgewinde | DIN 405 | mm | Rund |
| `ACME` | ACME-Gewinde | ASME B1.5 | inch | Trapez |
| `NPT` | National Pipe Taper | ANSI B1.20.1 | inch | V, konisch |
| `PG` | Panzergewinde | DIN 40430 | mm | V |
| `EDISON` | Edison-Gewinde | IEC 60061 | mm | Rund |
| `BALL_SCREW` | Kugelgewindetrieb | DIN 69051 / ISO 3408 | mm | Gothic |

## Lizenz

Dieses Repository enthält derzeit keine Lizenzdatei. Ohne Lizenz bleiben alle Rechte beim Rechteinhaber; vor Nutzung, Weitergabe oder Änderung ist eine passende Lizenzklärung erforderlich.
