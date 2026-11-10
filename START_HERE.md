# Open the E8 project

Extract the entire ZIP first. Keep its folders together.

1. Open `aircraft/viewer/E8_3D_Viewer_Offline.html` in a modern browser to inspect the assembled aircraft. It works offline after extraction. Orbit, zoom, inspect components and compare winged/wingless and rotor-tilt views.
2. Open `E8_eVTOL_Explorer_Offline.html` for the original student performance explorer.
3. Open `aircraft/cad/E8_Concept_Assembly.FCStd` in FreeCAD, or import one of the STEP files into a compatible CAD application. All CAD dimensions are millimetres. Import STL files as millimetres too.
4. Read [aircraft/README.md](aircraft/README.md), [the design report](aircraft/DESIGN_REPORT.md), [the parts shortlist](aircraft/BOM.csv) and [the reviews](aircraft/reviews/README.md).

The offline viewers require no installation or account. On a phone, download and extract the ZIP and use a browser that permits local HTML with JavaScript; a computer is recommended for CAD applications.

**This is a preliminary educational concept. It is not released for fabrication or flight.** The rotor-out power/torque screens fail, battery cooling is unresolved, and no matched propeller, detailed structural/control design, complete aircraft price or globally optimal design is established.

Optional rebuild commands in [aircraft/ENVIRONMENT.md](aircraft/ENVIRONMENT.md) run from this top-level folder, next to `aircraft/`. Install the stated optional software first. Package the complete folder again with `python3 aircraft/tools/package_project.py`.

The ZIP includes the original student files, the CAD exports, the analysis, sourced parts observations, review evidence and rebuild scripts. The archive's own download link points to GitHub and needs a network connection; viewing the extracted models does not.
