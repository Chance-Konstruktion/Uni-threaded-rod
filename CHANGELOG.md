# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — Blender 4.0+

### Changed
- `bl_info` now carries the real maintainer (`Chance-Konstruktion`) instead of
  the `Ihr Name` placeholder, and the add-on version was bumped to `0.3.0`.

### Removed
- Non-thread bayonet couplings have been dropped: the `STORZ` (DIN 14318 fire
  hose coupling) and `LAMP_B` (IEC 60061-1 bayonet lamp socket) standards, the
  whole `BAYONET` profile type, and the dedicated `bayonet_builder.py` module.
  This add-on is now exclusively for actual threads, so the standard count goes
  from 26 to 24. The corresponding operator branch, the
  `error_invalid_bayonet_dimensions` UI text and the bayonet smoke/regression
  tests were removed as well.

### Fixed
- `api.thread()` now resolves every thread standard, not just the metric ones.
  Previously the high-level API upper-cased the spec and stripped a leading
  `M`, which broke case-sensitive nominal tokens such as `Pg7`/`Pg13.5`
  (`PG`, `CONDUIT_PG`), `M8x1` (`SPARK_PLUG`) and `M12x1.5` (`CABLE_GLAND_M`).
  The token is now passed through unchanged, with the `M`-prefix removal kept
  only as a convenience fallback for metric sizes like `M10`. This also unblocks
  the same standards in the sister project **Uni-threaded-sleeve**, which calls
  this API.
- Round-thread profile (`ROUND` profile type — DIN 405 round threads and the
  ASME B1.9 `KNUCKLE` standard) was geometrically broken: the old arc
  construction produced an axially non-monotonic, self-intersecting contour, so
  the thread grooves ("negatives") were effectively missing. It is now a clean
  fully-rounded contour (one cosine wave per pitch) that runs from the major
  radius at the crest down to the core radius at the root and back.

## [0.2.0] — Blender 4.0+

- External threads for the supported thread standards, multi-start threads,
  material/surface presets and the high-level `api.thread()` entry point.
