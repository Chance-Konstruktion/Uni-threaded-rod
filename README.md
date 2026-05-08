# Uni-threaded-rod for Blender

Blender-Add-on zur parametrischen Erzeugung von Außengewinden, Innengewinde-Cuttern und mehrgängigen Gewinden.

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
| `UNEF` | Unified National Extra Fine | ANSI/ASME B1.1 | inch | V |
| `UNS` | Unified National Special | ANSI/ASME B1.1 | inch | V |
| `PIPE_R` | Rohrgewinde, kegelig | DIN EN 10226 | inch | V, konisch |
| `BSPT` | British Standard Pipe Taper | BS 21 / ISO 7-1 | inch | V, konisch |
| `BSF` | British Standard Fine | BS 84 | inch | V |
| `METRIC_TRAPEZOIDAL_FINE` | Metrisches Feintrapezgewinde | DIN 380 | mm | Trapez |
| `STUB_ACME` | Stub-ACME-Gewinde | ASME B1.8 | inch | Trapez |
| `KNUCKLE` | Knuckle-Gewinde (Rund, US) | ASME B1.9 | inch | Rund |
| `SPARK_PLUG` | Zündkerzengewinde | ISO 28741 | mm | V |
| `STORZ` | Storz-Festkupplung (Feuerwehr) | DIN 14318 | mm | Sonderprofil |
| `CABLE_GLAND_M` | Kabelverschraubung, metrisch | DIN EN 60423 / IEC 60423 | mm | V |
| `CONDUIT_PG` | Panzergewinde Elektroinstallation | DIN 40430 | mm | V |
| `LAMP_E` | Edison-Lampensockel (E14/E27/E40) | IEC 60061-1 | mm | Rund |
| `LAMP_B` | Bajonett-/Stiftsockel-Gewinde | IEC 60061-1 | mm | Rund |

## Lizenz

Dieses Projekt steht unter der GNU General Public License v3.0 (GPL-3.0). Der vollständige Lizenztext befindet sich in der Datei [`LICENSE`](LICENSE).
