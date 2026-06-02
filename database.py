MM_PER_INCH = 25.4

# Kleine praxisrelevante ISO-Tabellenbasis (erweiterbar) für exakte Nennreihen.
# Werte in mm, abgeleitet aus ISO 261 / ISO 965-1 (vereinfachte Auswahldaten).
ISO_METRIC_COARSE_PITCH_SERIES = {
    1.0: 0.25, 1.2: 0.25, 1.4: 0.3, 1.6: 0.35, 1.8: 0.35,
    2.0: 0.4, 2.5: 0.45, 3.0: 0.5, 3.5: 0.6, 4.0: 0.7,
    5.0: 0.8, 6.0: 1.0, 7.0: 1.0, 8.0: 1.25, 10.0: 1.5,
    12.0: 1.75, 14.0: 2.0, 16.0: 2.0, 18.0: 2.5, 20.0: 2.5,
    22.0: 2.5, 24.0: 3.0, 27.0: 3.0, 30.0: 3.5, 33.0: 3.5,
    36.0: 4.0, 39.0: 4.0, 42.0: 4.5, 45.0: 4.5, 48.0: 5.0,
    52.0: 5.0, 56.0: 5.5, 60.0: 5.5, 64.0: 6.0,
}

ISO_METRIC_FINE_PITCH_SERIES = {
    1.0: 0.2, 1.2: 0.2, 1.4: 0.2, 1.6: 0.2, 1.8: 0.2,
    2.0: 0.25, 2.5: 0.35, 3.0: 0.35, 3.5: 0.35, 4.0: 0.5,
    5.0: 0.5, 6.0: 0.75, 7.0: 0.75, 8.0: 1.00, 10.0: 1.25,
    12.0: 1.50, 14.0: 1.50, 16.0: 1.50, 18.0: 1.50, 20.0: 1.50,
    22.0: 1.50, 24.0: 2.00, 27.0: 2.00, 30.0: 2.00, 33.0: 2.00,
    36.0: 3.00, 39.0: 3.00, 42.0: 3.00, 45.0: 3.00, 48.0: 3.00,
    52.0: 4.00, 56.0: 4.00, 60.0: 4.00, 64.0: 4.00, 72.0: 4.00,
    80.0: 4.00, 90.0: 4.00, 100.0: 4.00,
}

ISO_METRIC_COARSE_TABLE = {
    f"M{diameter:g}": {
        "diameter": diameter,
        "pitch": pitch,
        "d2_basic": diameter - 0.649519 * pitch,
        "d3_basic": diameter - 1.226869 * pitch,
        # ISO 68-1 Grundprofil: Kuppenabflachung P/8, Kerbradius ~0.14434*P (typ. extern)
        "crest_flat": pitch / 8.0,
        "root_radius": 0.14434 * pitch,
    }
    for diameter, pitch in ISO_METRIC_COARSE_PITCH_SERIES.items()
}

# Vereinfachte fundamentale Abmaße (radial) für häufige Paarung 6g / 6H.
# Ziel: reproduzierbares Fit-Verhalten statt generischer Pauschal-Offsets.
ISO_965_TOLERANCE_RADIAL_OFFSETS = {
    (6.0, 1.0): {"6g_external": -0.010, "6H_internal": 0.000},
    (8.0, 1.25): {"6g_external": -0.010, "6H_internal": 0.000},
    (10.0, 1.5): {"6g_external": -0.010, "6H_internal": 0.000},
    (12.0, 1.75): {"6g_external": -0.013, "6H_internal": 0.000},
}

# ------------------------------------------------------------------------------
# 3.1 NORMEN-DATENBANK
# ------------------------------------------------------------------------------
THREAD_STANDARDS = {
    "METRIC_ISO": {
        "name": "Metrisches ISO-Regelgewinde",
        "standard": "DIN 13 / ISO 68-1",
        "unit": "mm",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {
            **ISO_METRIC_COARSE_PITCH_SERIES,
        },
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.226869 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9382 * p,
        "tolerance_classes": {"external": ["4g", "6g", "8g"], "internal": ["4H", "5H", "6H", "7H"]},
        "special_params": {"crest_flat": "P/8", "root_flat": "P/4"},
    },
    "METRIC_FINE": {
        "name": "Metrisches ISO-Feingewinde",
        "standard": "DIN 13 / ISO 965-1",
        "unit": "mm",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {
            **ISO_METRIC_FINE_PITCH_SERIES,
        },
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.226869 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9382 * p,
        "tolerance_classes": {"external": ["4g", "6g", "8g"], "internal": ["4H", "5H", "6H", "7H"]},
        "special_params": {"crest_flat": "P/8", "root_flat": "P/4"},
    },
    "WHITWORTH_BSW": {
        "name": "Whitworth-Gewinde (grob)",
        "standard": "BS 84",
        "unit": "inch",
        "flank_angle": 55.0,
        "profile_type": "V",
        "diam_pitch_map": {1/8: 40, 3/16: 24, 1/4: 20, 5/16: 18, 3/8: 16, 7/16: 14, 1/2: 12, 5/8: 11, 3/4: 10, 7/8: 9, 1.0: 8, 1.125: 7, 1.25: 7, 1.5: 6, 1.75: 5, 2.0: 4.5},
        "d2_formula": lambda d, p: d - 0.640327 * p,
        "d3_formula": lambda d, p: d - 1.280654 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.960490 * p,
        "tolerance_classes": {"external": ["Close", "Medium", "Free"]},
        "special_params": {"rounded_radius": "0.137329*P", "crest_flat": "P/12", "root_flat": "P/6"},
    },
    "BSF": {
        "name": "British Standard Fine",
        "standard": "BS 84",
        "unit": "inch",
        "flank_angle": 55.0,
        "profile_type": "V",
        "diam_pitch_map": {3/16: 32, 1/4: 26, 5/16: 22, 3/8: 20, 7/16: 18, 1/2: 16, 9/16: 16, 5/8: 14, 11/16: 14, 3/4: 12, 7/8: 11, 1.0: 10, 1.125: 9, 1.25: 9, 1.5: 8, 1.75: 7, 2.0: 7},
        "d2_formula": lambda d, p: d - 0.640327 * p,
        "d3_formula": lambda d, p: d - 1.280654 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.960490 * p,
        "tolerance_classes": {"external": ["Close", "Medium", "Free"]},
        "special_params": {"rounded_radius": "0.137329*P", "crest_flat": "P/12", "root_flat": "P/6"},
    },
    "UNC": {
        "name": "Unified National Coarse",
        "standard": "ANSI/ASME B1.1",
        "unit": "inch",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {1/4: 20, 5/16: 18, 3/8: 16, 7/16: 14, 1/2: 13, 9/16: 12, 5/8: 11, 3/4: 10, 7/8: 9, 1.0: 8, 1.125: 7, 1.25: 7, 1.5: 6},
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.299038 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.974279 * p,
        "tolerance_classes": {"external": ["1A", "2A", "3A"], "internal": ["1B", "2B", "3B"]},
        "special_params": {"flat_root": True},
    },
    "UNF": {
        "name": "Unified National Fine",
        "standard": "ANSI/ASME B1.1",
        "unit": "inch",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {1/4: 28, 5/16: 24, 3/8: 24, 7/16: 20, 1/2: 20, 9/16: 18, 5/8: 18, 3/4: 16, 7/8: 14, 1.0: 12, 1.125: 12, 1.25: 12},
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.299038 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.974279 * p,
        "tolerance_classes": {"external": ["1A", "2A", "3A"], "internal": ["1B", "2B", "3B"]},
    },
    "UNEF": {
        "name": "Unified National Extra Fine",
        "standard": "ANSI/ASME B1.1",
        "unit": "inch",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {
            1/4: 32, 5/16: 32, 3/8: 32, 7/16: 28, 1/2: 28,
            9/16: 24, 5/8: 24, 11/16: 24, 3/4: 20, 13/16: 20,
            7/8: 20, 15/16: 20, 1.0: 20, 1.0625: 18, 1.125: 18,
            1.1875: 18, 1.25: 18, 1.3125: 18, 1.375: 18, 1.4375: 18,
            1.5: 18, 1.5625: 18, 1.625: 18, 1.6875: 18,
        },
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.299038 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.974279 * p,
        "tolerance_classes": {"external": ["1A", "2A", "3A"], "internal": ["1B", "2B", "3B"]},
    },
    "UNS": {
        "name": "Unified National Special",
        "standard": "ANSI/ASME B1.1",
        "unit": "inch",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {1/2: 12, 5/8: 16, 3/4: 14, 7/8: 18, 1.0: 16, 1.125: 16, 1.25: 16, 1.5: 14},
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.299038 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.974279 * p,
        "tolerance_classes": {"external": ["2A", "3A"], "internal": ["2B", "3B"]},
        "special_params": {"flat_root": True},
    },
    "BSPT": {
        "name": "British Standard Pipe Taper (konisch, dichtend)",
        "standard": "BS 21 / ISO 7-1",
        "unit": "inch",
        "flank_angle": 55.0,
        "profile_type": "V",
        "taper": 1 / 16,
        "diam_pitch_map": {"R1/16": 28, "R1/8": 28, "R1/4": 19, "R3/8": 19, "R1/2": 14, "R3/4": 14, "R1": 11, "R1 1/4": 11, "R1 1/2": 11, "R2": 11, "R2 1/2": 11, "R3": 11, "R4": 11},
        "diam_nominal_map": {"R1/16": 7.723, "R1/8": 9.728, "R1/4": 13.157, "R3/8": 16.662, "R1/2": 20.955, "R3/4": 26.441, "R1": 33.249, "R1 1/4": 41.910, "R1 1/2": 47.803, "R2": 59.614, "R2 1/2": 75.184, "R3": 87.884, "R4": 113.030},
        "d2_formula": lambda d, p: d - 0.640327 * p,
        "d3_formula": lambda d, p: d - 1.280654 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.960490 * p,
        "tolerance_classes": {"external": ["R"], "internal": ["Rc", "Rp"]},
        "special_params": {"crest_flat": "P/12", "root_flat": "P/6", "taper_ratio": 1 / 16},
    },
    "PIPE_G": {
        "name": "Rohrgewinde (zylindrisch, nicht dichtend)",
        "standard": "DIN EN ISO 228",
        "unit": "inch",
        "flank_angle": 55.0,
        "profile_type": "V",
        "diam_pitch_map": {"G1/8": 28, "G1/4": 19, "G3/8": 19, "G1/2": 14, "G3/4": 14, "G1": 11, "G1 1/4": 11, "G1 1/2": 11, "G2": 11},
        "diam_nominal_map": {"G1/8": 9.728, "G1/4": 13.157, "G3/8": 16.662, "G1/2": 20.955, "G3/4": 26.441, "G1": 33.249, "G1 1/4": 41.910, "G1 1/2": 47.803, "G2": 59.614},
        "d2_formula": lambda d, p: d - 0.640327 * p,
        "d3_formula": lambda d, p: d - 1.280654 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.960490 * p,
        "tolerance_classes": {"external": ["A", "B"]},
        "special_params": {"crest_flat": "P/12", "root_flat": "P/6"},
    },
    "PIPE_R": {
        "name": "Rohrgewinde (konisch, dichtend)",
        "standard": "DIN EN 10226 / ISO 7-1",
        "unit": "inch",
        "flank_angle": 55.0,
        "profile_type": "V",
        "taper": 1 / 16,
        "diam_pitch_map": {"R1/8": 28, "R1/4": 19, "R3/8": 19, "R1/2": 14, "R3/4": 14, "R1": 11, "R1 1/4": 11, "R1 1/2": 11, "R2": 11},
        "diam_nominal_map": {"R1/8": 9.728, "R1/4": 13.157, "R3/8": 16.662, "R1/2": 20.955, "R3/4": 26.441, "R1": 33.249, "R1 1/4": 41.910, "R1 1/2": 47.803, "R2": 59.614},
        "d2_formula": lambda d, p: d - 0.640327 * p,
        "d3_formula": lambda d, p: d - 1.280654 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.960490 * p,
        "tolerance_classes": {"external": ["R"], "internal": ["Rc", "Rp"]},
        "special_params": {"crest_flat": "P/12", "root_flat": "P/6", "taper_ratio": 1 / 16},
    },
    "TRAPEZOIDAL": {
        "name": "Trapezgewinde",
        "standard": "DIN 103",
        "unit": "mm",
        "flank_angle": 30.0,
        "profile_type": "TRAPEZOID",
        "diam_pitch_map": {8: 1.5, 10: 2.0, 12: 3.0, 16: 4.0, 20: 4.0, 24: 5.0, 28: 5.0, 32: 6.0, 36: 6.0, 40: 7.0, 44: 7.0, 48: 8.0, 52: 8.0, 60: 9.0, 70: 10.0, 80: 10.0},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p - 2 * 0.25,
        "tensile_stress_area_formula": lambda d, p: d - 0.5 * p - 0.25,
        "tolerance_classes": {"external": ["7e", "8e", "9e"]},
        "special_params": {"crest_width": "0.5*P", "root_width": "0.5*P - 0.5"},
    },
    "METRIC_TRAPEZOIDAL_FINE": {
        "name": "Metrisches Feintrapezgewinde",
        "standard": "DIN 380",
        "unit": "mm",
        "flank_angle": 30.0,
        "profile_type": "TRAPEZOID",
        "diam_pitch_map": {10: 1.5, 12: 2.0, 16: 2.0, 20: 2.0, 24: 3.0, 30: 3.0, 36: 3.0, 42: 4.0, 48: 4.0, 60: 5.0, 70: 5.0},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p - (0.25 if p >= 4.0 else 0.15),
        "tensile_stress_area_formula": lambda d, p: d - 0.5 * p - 0.25,
        "tolerance_classes": {"external": ["7e", "8e", "9e"], "internal": ["7H", "8H"]},
        "special_params": {"crest_width": "0.5*P", "root_width": "0.5*P - 0.15"},
    },
    "BUTTRESS": {
        "name": "Sägengewinde",
        "standard": "DIN 513",
        "unit": "mm",
        "flank_angle": 33.0,
        "profile_type": "BUTTRESS",
        "diam_pitch_map": {10: 2.0, 12: 3.0, 16: 4.0, 20: 5.0, 24: 6.0, 28: 7.0, 32: 8.0, 36: 9.0, 40: 10.0, 44: 11.0, 48: 12.0},
        "d2_formula": lambda d, p: d - 0.75 * p,
        "d3_formula": lambda d, p: d - 1.5 * p - 0.5,
        "tensile_stress_area_formula": lambda d, p: d - 1.25 * p,
        "tolerance_classes": {"external": ["7e", "8e", "9e"], "internal": ["7H", "8H"]},
        "special_params": {"pressure_flank": 30.0, "clearance_flank": 3.0},
    },
    "ROUND": {
        "name": "Rundgewinde",
        "standard": "DIN 405",
        "unit": "mm",
        "flank_angle": 30.0,
        "profile_type": "ROUND",
        "diam_pitch_map": {8: 1.5, 10: 2.0, 12: 3.0, 16: 4.0, 20: 4.0, 24: 5.0},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p - 1.0,
        "tensile_stress_area_formula": lambda d, p: d - 0.75 * p,
        "tolerance_classes": {"external": ["7e", "8e", "9e"], "internal": ["7H", "8H"]},
        "special_params": {"radius": "P/4"},
    },
    "KNUCKLE": {
        "name": "Knuckle thread",
        "standard": "ASME B1.9",
        "unit": "inch",
        "flank_angle": 30.0,
        "profile_type": "ROUND",
        "diam_pitch_map": {1/4: 20, 3/8: 16, 1/2: 12, 5/8: 10, 3/4: 8, 1.0: 6, 1.25: 5, 1.5: 4, 2.0: 3},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p - 0.5 * (p / 4.0),
        "tensile_stress_area_formula": lambda d, p: d - 0.5 * p - 0.125,
        "tolerance_classes": {"external": ["2A"], "internal": ["2B"]},
        "special_params": {"radius": "P/4"},
    },
    "ACME": {
        "name": "ACME-Gewinde",
        "standard": "ASME B1.5",
        "unit": "inch",
        "flank_angle": 29.0,
        "profile_type": "TRAPEZOID",
        "diam_pitch_map": {1/4: 16, 5/16: 14, 3/8: 12, 1/2: 10, 5/8: 8, 3/4: 6, 7/8: 6, 1.0: 5, 1.25: 5, 1.5: 4, 2.0: 4},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p - 0.020 * MM_PER_INCH,
        "tensile_stress_area_formula": lambda d, p: d - 0.5 * p,
        "tolerance_classes": {"external": ["2G", "3G", "4G"]},
    },
    "STUB_ACME": {
        "name": "Stub ACME",
        "standard": "ASME B1.8",
        "unit": "inch",
        "flank_angle": 29.0,
        "profile_type": "TRAPEZOID",
        "diam_pitch_map": {1/4: 16, 5/16: 14, 3/8: 12, 1/2: 10, 5/8: 8, 3/4: 6, 1.0: 5, 1.25: 5, 1.5: 4, 2.0: 4},
        "d2_formula": lambda d, p: d - 0.25 * p,
        "d3_formula": lambda d, p: d - 0.5 * p - 0.020 * MM_PER_INCH,
        "tensile_stress_area_formula": lambda d, p: d - 0.5 * p,
        "tolerance_classes": {"external": ["2G", "3G", "4G"]},
        "special_params": {"height_factor": 0.5},
    },
    "NPT": {
        "name": "National Pipe Taper",
        "standard": "ANSI B1.20.1",
        "unit": "inch",
        "flank_angle": 60.0,
        "profile_type": "V",
        "taper": 1 / 16,
        "diam_pitch_map": {"1/16": 27, "1/8": 27, "1/4": 18, "3/8": 18, "1/2": 14, "3/4": 14, "1": 11.5, "1 1/4": 11.5, "1 1/2": 11.5, "2": 11.5},
        "diam_nominal_map": {"1/16": 7.9, "1/8": 10.3, "1/4": 13.7, "3/8": 17.1, "1/2": 21.3, "3/4": 26.7, "1": 33.4, "1 1/4": 42.2, "1 1/2": 48.3, "2": 60.3},
        "d2_formula": lambda d, p: d - 0.8 * p,
        "d3_formula": lambda d, p: d - 1.6 * p,
        "tensile_stress_area_formula": lambda d, p: d - 1.2 * p,
        "tolerance_classes": {"external": ["L1", "L2"], "internal": ["L1", "L2"]},
        "special_params": {"taper_ratio": 1 / 16},
    },
    "PG": {
        "name": "Panzergewinde (Elektro)",
        "standard": "DIN 40430",
        "unit": "mm",
        "flank_angle": 80.0,
        "profile_type": "V",
        "diam_pitch_map": {"Pg7": 1.27, "Pg9": 1.41, "Pg11": 1.41, "Pg13.5": 1.41, "Pg16": 1.41, "Pg21": 1.588, "Pg29": 1.588, "Pg36": 1.814, "Pg42": 1.814, "Pg48": 1.814},
        "diam_nominal_map": {"Pg7": 12.5, "Pg9": 15.2, "Pg11": 18.6, "Pg13.5": 20.4, "Pg16": 22.5, "Pg21": 28.3, "Pg29": 37.0, "Pg36": 47.0, "Pg42": 54.0, "Pg48": 59.3},
        "d2_formula": lambda d, p: d - 0.6 * p,
        "d3_formula": lambda d, p: d - 1.2 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9 * p,
        "special_params": {"tolerance_note": "DIN 40430/Pg: keine separaten Add-on-Toleranzklassen hinterlegt"},
    },
    "EDISON": {
        "name": "Edison-Lampensockel-Gewinde (E10/E14/E27/E40)",
        "standard": "IEC 60061-1",
        "unit": "mm",
        "flank_angle": 0.0,
        "profile_type": "EDISON",
        "diam_pitch_map": {"E10": 1.5, "E14": 2.5, "E27": 3.5, "E40": 6.0},
        "diam_nominal_map": {"E10": 10.0, "E14": 14.0, "E27": 27.0, "E40": 40.0},
        "d2_formula": lambda d, p: d - 0.5 * p,
        "d3_formula": lambda d, p: d - p,
        "tensile_stress_area_formula": lambda d, p: d - 0.75 * p,
        "tolerance_classes": {"external": ["IEC"], "internal": ["IEC"]},
        "special_params": {"radius_ratio": 1.0 / 3.0},
    },
    "SPARK_PLUG": {
        "name": "Zündkerzengewinde",
        "standard": "ISO 28741",
        "unit": "mm",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {"M8x1": 1.0, "M10x1": 1.0, "M12x1.25": 1.25, "M14x1.25": 1.25, "M18x1.5": 1.5},
        "diam_nominal_map": {"M8x1": 8.0, "M10x1": 10.0, "M12x1.25": 12.0, "M14x1.25": 14.0, "M18x1.5": 18.0},
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.226869 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9382 * p,
        "tolerance_classes": {"external": ["6g"], "internal": ["6H"]},
        "special_params": {"crest_flat": "P/8", "root_flat": "P/4"},
    },
    "CABLE_GLAND_M": {
        "name": "Kabelverschraubung, metrisch",
        "standard": "DIN EN 60423 / IEC 60423",
        "unit": "mm",
        "flank_angle": 60.0,
        "profile_type": "V",
        "diam_pitch_map": {"M12x1.5": 1.5, "M16x1.5": 1.5, "M20x1.5": 1.5, "M25x1.5": 1.5, "M32x1.5": 1.5, "M40x1.5": 1.5, "M50x1.5": 1.5, "M63x1.5": 1.5},
        "diam_nominal_map": {"M12x1.5": 12.0, "M16x1.5": 16.0, "M20x1.5": 20.0, "M25x1.5": 25.0, "M32x1.5": 32.0, "M40x1.5": 40.0, "M50x1.5": 50.0, "M63x1.5": 63.0},
        "d2_formula": lambda d, p: d - 0.649519 * p,
        "d3_formula": lambda d, p: d - 1.226869 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9382 * p,
        "tolerance_classes": {"external": ["6g"], "internal": ["6H"]},
        "special_params": {"crest_flat": "P/8", "root_flat": "P/4"},
    },
    "CONDUIT_PG": {
        "name": "Panzergewinde Elektroinstallation",
        "standard": "DIN 40430",
        "unit": "mm",
        "flank_angle": 80.0,
        "profile_type": "V",
        "diam_pitch_map": {"Pg7": 1.27, "Pg9": 1.41, "Pg11": 1.41, "Pg13.5": 1.41, "Pg16": 1.41, "Pg21": 1.588, "Pg29": 1.588, "Pg36": 1.814, "Pg42": 1.814, "Pg48": 1.814},
        "diam_nominal_map": {"Pg7": 12.5, "Pg9": 15.2, "Pg11": 18.6, "Pg13.5": 20.4, "Pg16": 22.5, "Pg21": 28.3, "Pg29": 37.0, "Pg36": 47.0, "Pg42": 54.0, "Pg48": 59.3},
        "d2_formula": lambda d, p: d - 0.6 * p,
        "d3_formula": lambda d, p: d - 1.2 * p,
        "tensile_stress_area_formula": lambda d, p: d - 0.9 * p,
        "special_params": {"tolerance_note": "Alias zu Pg-Größen: keine separaten Add-on-Toleranzklassen hinterlegt"},
    },
    "LAMP_B": {
        "name": "Bajonett-Lampensockel (B15/B22)",
        "standard": "IEC 60061-1",
        "unit": "mm",
        "flank_angle": 0.0,
        "profile_type": "BAYONET",
        "diam_pitch_map": {"B15s": 0.0, "B15d": 0.0, "B22d": 0.0},
        "diam_nominal_map": {"B15s": 15.0, "B15d": 15.0, "B22d": 22.0},
        "d2_formula": lambda d, p: d,
        "d3_formula": lambda d, p: d,
        "special_params": {"note": "Bajonett-Lampensockel — kein helikales Gewinde, separate Pipeline erforderlich"},
    },
    "STORZ": {
        "name": "Storz-Festkupplung (Feuerwehr, Bajonett)",
        "standard": "DIN 14318",
        "unit": "mm",
        "flank_angle": 0.0,
        "profile_type": "BAYONET",
        "diam_pitch_map": {"A-110": 0.0, "B-75": 0.0, "C-52": 0.0, "D-25": 0.0, "F-150": 0.0},
        "diam_nominal_map": {"A-110": 133.0, "B-75": 89.0, "C-52": 66.0, "D-25": 31.0, "F-150": 160.0},
        "d2_formula": lambda d, p: d,
        "d3_formula": lambda d, p: d,
        "tolerance_classes": {"external": ["DIN 14318"]},
        "special_params": {"note": "Bajonett-Knaggenkupplung — kein Gewinde, separate Pipeline erforderlich"},
    },
}

# ------------------------------------------------------------------------------
# 3.2 MATERIAL-PRESETS
# ------------------------------------------------------------------------------
MATERIAL_PRESETS = {
    "STEEL_4.6": {"name": "Stahl 4.6", "color": (0.6, 0.6, 0.6, 1.0), "metallic": 0.8, "roughness": 0.4, "ior": 1.45},
    "STEEL_8.8": {"name": "Stahl 8.8", "color": (0.5, 0.5, 0.5, 1.0), "metallic": 0.9, "roughness": 0.3, "ior": 1.45},
    "STEEL_10.9": {"name": "Stahl 10.9", "color": (0.4, 0.4, 0.4, 1.0), "metallic": 0.95, "roughness": 0.2, "ior": 1.45},
    "STAINLESS_A2": {"name": "Edelstahl A2", "color": (0.7, 0.7, 0.7, 1.0), "metallic": 1.0, "roughness": 0.3, "ior": 1.45},
    "STAINLESS_A4": {"name": "Edelstahl A4", "color": (0.65, 0.65, 0.65, 1.0), "metallic": 1.0, "roughness": 0.25, "ior": 1.45},
    "ZINC": {"name": "Verzinkt", "color": (0.8, 0.8, 0.75, 1.0), "metallic": 0.6, "roughness": 0.5, "ior": 1.45},
    "HOT_DIP": {"name": "Feuerverzinkt", "color": (0.5, 0.5, 0.45, 1.0), "metallic": 0.4, "roughness": 0.7, "ior": 1.45},
    "BRASS": {"name": "Messing", "color": (0.9, 0.7, 0.2, 1.0), "metallic": 0.9, "roughness": 0.3, "ior": 1.45},
}

THREAD_PRESETS = {
    "M10_STD": {
        "name": "M10x1.5 8.8 verzinkt",
        "standard": "METRIC_ISO",
        "diameter_token": "10.0",
        "material": "STEEL_8.8",
        "surface": "ZINC",
        "tolerance_class": "6g",
        "clearance": 0.10,
        "starts": 1,
    },
    "M8_FINE_A2": {
        "name": "M8x1.0 A2",
        "standard": "METRIC_FINE",
        "diameter_token": "8.0",
        "material": "STAINLESS_A2",
        "surface": "NONE",
        "tolerance_class": "6g",
        "clearance": 0.06,
        "starts": 1,
    },
    "TR20_DRIVE": {
        "name": "Tr20x4 Antrieb",
        "standard": "TRAPEZOIDAL",
        "diameter_token": "20",
        "material": "STEEL_10.9",
        "surface": "NONE",
        "tolerance_class": "7e",
        "clearance": 0.05,
        "starts": 1,
    },
}


def get_diameter_items_for_standard(standard_key):
    std = THREAD_STANDARDS[standard_key]
    items = []
    for raw_key in std["diam_pitch_map"].keys():
        token = str(raw_key)
        if isinstance(raw_key, (int, float)) and std["unit"] == "inch":
            label = f'{raw_key:.4g}"'
        else:
            label = str(raw_key)
        items.append((token, label, f"{std['name']} {label}"))
    return items


def get_default_tolerance_class(standard_key, internal=False):
    std = THREAD_STANDARDS.get(standard_key)
    if not std:
        return "6g"
    classes = std.get("tolerance_classes", {})
    key = "internal" if internal else "external"
    values = classes.get(key, []) or classes.get("external", []) or classes.get("internal", [])
    return str(values[0]) if values else "6g"


def _resolve_diameter_mm(std, diameter_token):
    # Symbolische Nennwerte zuerst auflösen: rein numerisch aussehende String-Keys
    # wie NPT "1"/"2" dürfen nicht über float() als Zoll-Durchmesser fehlinterpretiert
    # werden, sonst ist ihre Steigung im diam_pitch_map nicht mehr auffindbar.
    nom_map = std.get("diam_nominal_map", {})
    if diameter_token in nom_map:
        return float(nom_map[diameter_token]), diameter_token
    try:
        raw_numeric = float(diameter_token)
        if std["unit"] == "inch":
            return raw_numeric * MM_PER_INCH, raw_numeric
        return raw_numeric, raw_numeric
    except ValueError:
        raise ValueError(f"Durchmesserwert {diameter_token} in {std['name']} nicht auflösbar")


def resolve_thread_parameters(standard_key, diameter_token):
    if standard_key not in THREAD_STANDARDS:
        raise ValueError(f"Unbekannter Standard: {standard_key}")
    std = THREAD_STANDARDS[standard_key]
    diameter_mm, raw_key = _resolve_diameter_mm(std, diameter_token)

    if raw_key in std["diam_pitch_map"]:
        pitch_or_tpi = std["diam_pitch_map"][raw_key]
    else:
        numeric_keys = [k for k in std["diam_pitch_map"].keys() if isinstance(k, (int, float))]
        if not numeric_keys:
            raise ValueError(f"Für {standard_key} sind nur symbolische Nennwerte erlaubt")
        closest = min(numeric_keys, key=lambda x: abs(x - float(raw_key)))
        pitch_or_tpi = std["diam_pitch_map"][closest]

    pitch_mm = MM_PER_INCH / pitch_or_tpi if std["unit"] == "inch" else pitch_or_tpi
    return diameter_mm, pitch_mm


def get_standard_pitch(standard_key, diameter):
    """Kompatibilitätshelfer: erhält eine numerische Diameter-Eingabe."""
    std = THREAD_STANDARDS[standard_key]
    if std["unit"] == "inch":
        raw = diameter / MM_PER_INCH
        numeric_keys = [k for k in std["diam_pitch_map"].keys() if isinstance(k, (int, float))]
        closest = min(numeric_keys, key=lambda x: abs(x - raw))
        return MM_PER_INCH / std["diam_pitch_map"][closest]

    if diameter in std["diam_pitch_map"]:
        return std["diam_pitch_map"][diameter]

    numeric_keys = [k for k in std["diam_pitch_map"].keys() if isinstance(k, (int, float))]
    closest = min(numeric_keys, key=lambda x: abs(x - diameter))
    return std["diam_pitch_map"][closest]


def resolve_iso_metric_coarse_row(diameter, pitch, diameter_tolerance=1e-6, pitch_tolerance=1e-6):
    """Liefert Datensatz aus der integrierten ISO-Regelgewinde-Tabelle."""
    for row in ISO_METRIC_COARSE_TABLE.values():
        if abs(row["diameter"] - diameter) <= diameter_tolerance and abs(row["pitch"] - pitch) <= pitch_tolerance:
            return row
    return None
