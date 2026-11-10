# Reproduction environment

Students only need the downloaded standalone HTML file and a modern browser with JavaScript to inspect the model. Downloading the whole concept ZIP also provides the CAD files and reports. No account or network is needed to use the offline viewer after downloading.

The generated artifacts were produced in Linux with Python 3.12, CadQuery 2.7.0, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, FreeCAD 1.0, OpenSCAD 2021.01 and Blender 4.3.2. Separate applications and their native libraries must be installed to reproduce their respective exports. Installing the Python requirements alone does not install FreeCAD, Blender or OpenSCAD.

The STEP/FreeCAD/STL models use millimetres. STEP declares its unit; STL does not. The standalone viewer converts tessellated millimetres to metres for display. The FreeCAD file contains imported editable solid bodies; regenerate the parametric assembly using the Python/JSON sources.

From the repository root, after installing the optional Python dependencies:

```bash
python aircraft/tools/analyze.py
python aircraft/tools/build_cad.py
python aircraft/tools/build_viewer.py
python aircraft/tools/write_report.py
python aircraft/reviews/verify_numerics.py
```

`save_freecad.py` requires a Python interpreter that can import FreeCAD and Import. The included search paths match this Linux environment; use FreeCAD's Python environment or adjust paths for another platform. See the design report for the optional Blender command. `cad/E8_Assembly.scad` imports the STL files relative to the wrapper and was successfully exported through OpenSCAD during verification.

Optional viewer-script test:

```bash
npm install --prefix aircraft
npm --prefix aircraft run test:viewer
```

This executes the exact distributed script with a small DOM adapter and native Canvas; it is not a browser test. The optional `test:viewer:browser` script needs Chromium, using `/usr/bin/chromium` by default or the `CHROMIUM_PATH` environment variable. Its fresh launch was blocked in this environment, as documented in the review. Desktop and mobile canvas images are functional-rendering evidence, not browser screenshots.

No OpenFOAM CFD or structural FEA was run. The structural calculations are explicit beam approximations, and all aerodynamic/propulsion results are conceptual model outputs. See `DESIGN_REPORT.md` and `reviews/` for failed screens and open physical-validation work.
