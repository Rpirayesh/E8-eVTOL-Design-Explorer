# E8 eVTOL Design Explorer

An interactive design explorer for a **two-person, eight-motor electric VTOL concept**. Compare winged and wingless configurations, change aircraft and mission assumptions, and inspect estimated lift, power, energy use, and range.

**Student edition 1.1 · runs offline · no installation or sign-in needed after downloading.**

## 3D aircraft concept and parts study

The [aircraft design package](aircraft/README.md) adds a 167-component concept assembly in **STEP, FreeCAD and STL**, an [offline 3D viewer](aircraft/viewer/E8_3D_Viewer_Offline.html?raw=true), a sourced parts shortlist, a 624-case trade study and independent reviews. Download the [complete concept ZIP](https://github.com/Rpirayesh/E8-eVTOL-Design-Explorer/raw/refs/heads/main/downloads/E8_Aircraft_Concept_0_1.zip) for the models, analysis, reports and rebuild scripts.

**This is a preliminary educational concept, not a fabrication or flight release.** The reviews confirm unresolved rotor-out, torque, thermal and control limitations. The parts shortlist does not establish a cheapest complete aircraft. Read the [design report](aircraft/DESIGN_REPORT.md) and [review findings](aircraft/reviews/README.md) before using its estimates.

[START_HERE.md](START_HERE.md) explains how to open the complete aircraft archive. Fresh recovery checks are recorded in the [recovery review](aircraft/reviews/recovery_review.md).

## Start here — students

1. Download the [student offline package](downloads/E8_eVTOL_Explorer_Student_Offline.zip?raw=true).
2. Extract the ZIP file.
3. Double-click **E8_eVTOL_Explorer_Offline.html** and open it in a modern browser with JavaScript enabled.

You can also use GitHub's **Code → Download ZIP** to download this entire repository, extract it, and open the HTML file in the top-level folder. GitHub displays HTML source when you click an HTML file on the repository page; download it first to run the explorer.

The explorer contains its own code, styles, equations, and reference data. Calculations run on your computer with no network connections or accounts. Local input storage depends on your browser's support for local files; use **Export study** to save your results as CSV.

## What to explore

- Compare **Winged** and **Wingless** with the same shared assumptions.
- Vary cruise speed, empty mass, occupant mass, battery mass, and rotor diameter.
- Expand the wing, propulsion, battery/environment, and mission input groups.
- Compare the power and energy-based range curves across cruise speeds.
- Inspect the wing/rotor lift split and mission energy budget.
- Open **Model & equations** for the equations, assumptions, and limitations.
- Open **Validation** for the embedded reference checks, numerical cases, and current rotor-loading diagnostics.
- Export a CSV containing your assumptions, both configurations, and a 101-point speed sweep.

## Files and documentation

| Item | Purpose |
| --- | --- |
| [Offline explorer](E8_eVTOL_Explorer_Offline.html) | The complete standalone app; download and open locally |
| [Student ZIP](downloads/E8_eVTOL_Explorer_Student_Offline.zip?raw=true) | Ready-to-share offline package |
| [Opening instructions](README.txt) | Plain-text student instructions and edition notes |
| [Audit report](AUDIT_REPORT.md) | Independent reviews, corrections, examples, and verification limits |
| [Validation examples](VALIDATION_EXAMPLES.json) | Full input assumptions and independently calculated example outputs |
| [Audit tests](https://github.com/Rpirayesh/E8-eVTOL-Design-Explorer/tree/main/audit_tests) | Optional numerical, physics, and software verification materials |
| [Checksums](CHECKSUMS.txt) | SHA-256 checksums for the audited files |

## Model scope

The concept uses two occupants and eight equal, non-overlapping, tilting rotors. The optional wing adds both mass and aerodynamic drag. Cruise is steady, level, and in still air. Range deducts entered hover and transition/climb energy and retains the selected reserve. Motor power, battery power, mission energy, and edgewise advance ratio are screened.

**These are concept estimates, not demonstrated aircraft performance.** Passing the selected screens does not establish blade-stall, interference, compressibility, transition, control, structural, or thermal feasibility. The rotor-loading diagnostics do not apply a universal pass threshold. All starting values are illustrative assumptions.

## Verification included with edition 1.1

- 20,245 operating points compared with an independently coded Python solver.
- 3,061 exact-range mission checks and 600 separate exact/inside/outside regressions.
- 339 invalid-input cases rejected.
- 19 software test groups and 2,212 simulated UI operations, including 40 CSV exports and no network calls.

The audit found and corrected an exact-range rounding classification issue, tablet-width CSV button visibility, and ambiguous export during an invalid pending input. It also made the model domain more prominent. Power, lift, and range equations and default assumptions are unchanged. See the [audit report](AUDIT_REPORT.md) for test methods and limits, including the unavailable fresh direct-file and cross-browser tests.

## Optional developer checks

Students do not need Node.js or Python to use the explorer. For the included verification scripts:

```bash
# Node.js checks; no npm packages required
npm test

# Independent numerical audit; requires Python, NumPy, SciPy, and Node.js
python3 -m pip install -r requirements-audit.txt
python3 audit_tests/numerical/audit.py --model audit_tests/model-extracted.cjs --prefix rerun_
python3 audit_tests/numerical/boundary_regression.py --model audit_tests/model-extracted.cjs
```

The standalone HTML is the distributed app. `audit_tests/model-extracted.cjs` is the model extracted from that audited file for testing. Keep those synchronized when making changes.

## References

The equations and references are included in the explorer. The audit links the primary NASA sources and explains the simplifications. This project is an independent implementation; it is not the NASA NDARC software.
