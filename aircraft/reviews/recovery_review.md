# Recovery and publication verification — November 10, 2026

The original working files were recovered after an interrupted publication step. All 52 files in the saved publication manifest matched their recorded SHA-256 values. The original models and numerical outputs have been preserved; the archive layout, download links and recovery documentation were updated for distribution.

Three separate reviewers checked numerics, geometry, and distribution/software. Their fresh results support publication as the explicitly labelled educational concept. They do not establish an airworthy or buildable aircraft.

| Check | Recovery result |
| --- | --- |
| Numerical reproduction | 624 trade cases, 46 eligible winged cases, 576 adverse cases, seven scenarios; 31,070 comparisons with zero failures; maximum relative error 4.94e-12 |
| Regenerated analysis | Selected design, results, mass budget, trade study and numerical review outputs are byte-identical to the recovered files |
| Imported geometry | 167 winged-hover, 167 winged-cruise, 149 wingless and 167 native FreeCAD valid named leaf solids; zero invalid |
| Export integrity | STEP explicitly declares millimetres; native FreeCAD ZIP CRC passes; both STL byte lengths, triangle counts and finite-coordinate checks pass |
| Sampled rotor movement | All eight rotors checked at 19 angles, 0–90 degrees; no intersections with tested fixed geometry for the rigid disks or motor/yoke bodies |
| Selected internal clearances | Four battery cases have 5 mm hull clearance; seat/spar separation is at least 670 mm |
| Viewer functional check | 89 operations, desktop and mobile Canvas sizes, reset/tilt transforms and zero network calls pass using the exact distributed script |
| Browser check | Chromium again failed before loading HTML because the environment disallowed its process-singleton Unix socket; no browser or cross-browser pass is claimed |
| Sources and quotations | All BOM source IDs resolve to the 11-entry ledger. Observations remain dated November 9; recovery does not refresh vendor prices or establish a complete aircraft cost |

Fresh geometry evidence is in [recovery_geometry_results.json](recovery_geometry_results.json) and [recovery_export_results.json](recovery_export_results.json). Reproduce the numerical and geometry checks with the existing scripts listed in [README.md](README.md).

## Distribution correction

The original archive contained the final aircraft files but stripped the `aircraft/` directory required by its reproduction commands. The replacement archive preserves the repository folder structure and includes the original Explorer and student materials. [START_HERE.md](../../START_HERE.md) supplies extraction and opening instructions. Archive download links point to GitHub so the archive need not contain a copy of itself. [package_project.py](../tools/package_project.py) rebuilds the archive, refreshes aircraft checksums, checks ZIP CRCs and compares every archived file with its source.

## Engineering findings retained

All eight single-rotor-out allocations exceed the conservative continuous-power screen. Four outer-rotor failures also exceed the published maximum torque. A 25% increase in assumed cell resistance drops loaded hover voltage below the candidate motor's stated minimum, and battery heat rejection remains unclosed. Matched propeller maps, detailed load paths/laminates/joints, flight controls, transition trim and physical performance are unverified. No CFD or FEA result is supplied. The finite energy-grid selection is not a global optimum or a lowest-cost aircraft.

The native FreeCAD assembly contains editable imported solids; Python and JSON remain the parametric source. Intentional envelope overlap and sampled rigid clearances are not mechanical joints or complete collision/kinematic qualification.
