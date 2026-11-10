# Independent geometry and export review

**Assessment: suitable as a clearly labelled educational CAD concept; not a manufacturing, flight or airworthiness release.** This review independently imported the exported files with FreeCAD 1.0 and tested the resulting solids rather than relying only on the generator's validity flags. Reproduce with `python aircraft/reviews/final_geometry_check.py` from the repository root, using an interpreter with FreeCAD's modules installed.

## Export integrity and dimensions

- Winged hover STEP, winged cruise STEP and native FreeCAD each contain **167 valid named leaf solids**. Wingless hover STEP contains **149 valid leaf solids**. No invalid leaf solids were found in those imports.
- STEP explicitly declares millimetres (`SI_UNIT(.MILLI.,.METRE.)`). The winged hover extents are approximately x=−5300…5300, y=−4500…4500, z=−1250…2535 mm. The 9 m wing span, rotor stations, 4.8 m fuselage envelope and 1.7 m reference rotor diameter agree with the selected parameters.
- Binary STL sizes match their declared triangle counts and all inspected coordinates are finite. These are multi-component tessellations with intentional overlaps, not a single fused watertight manufacturing body. STL format itself does not encode units; users must import it as millimetres.
- STEP and FreeCAD preserve editable solid bodies, but the native file is an imported assembly, not a fully constrained sketch/feature design. The Python/JSON source is the parametric master.

## Corrections verified during review

The earlier low wing/spar occupied both seat backs. The revised main wing/spar sits at z=1.60 m; all four seat/spar intersection volumes are now zero, with at least **670 mm** separation. Six ribs are clipped to their wing envelope.

The original blade silhouettes were disconnected from the hubs. All **16 revised blades** now have zero distance and positive intersection volume with their respective hub envelopes. All eight motor/yoke/tilt-axle interfaces also have positive geometric contact. Added fixed crossheads connect the standoffs to the forks, added support rails connect the high-wing pylons to the crossbeams, and the revised standoff lower ends overlap their boom mounting envelopes. These fixes establish geometric continuity only; they do not size bearings, saddles, bolts, laminates, actuators or joints.

The four battery/hull bay interfaces were checked separately. The first draft boxes intersected the hull placeholder by about 4.36–5.94 litres each; the final cutout follow-up found **zero intersection volume and 5.0 mm separation for each of the four cases**. The native FreeCAD and STEP hull volumes match to within 0.000002 mm³. Details are recorded in `geometry_results.json`. Battery containment, covers, sealing, structural reinforcement, crash restraint and thermal/fire design remain unresolved regardless of zero geometric overlap.

## Limited kinematic checks

Independent full rigid rotor disks, 20 mm thick, were checked against fixed modeled geometry at **19 tilt angles (0° to 90° in 5° increments) for all eight rotors**. No fixed-geometry disk intersections were found. This sweep preceded the final hull bay cutouts; those cutouts only remove distant fixed material and do not change the tested moving geometry or attachments. Motor and rotating-yoke bodies were also checked through those angles, excluding each rotor's own intended axle interface; no unintended fixed-geometry intersections were found in that sample.

The selected adjacent hover disk gap is 0.65 m. A conservative independent-hub fore-aft shift allowance of 0.40 m leaves a 0.25 m neighbor gap before tolerances or deformation. At cruise placement the nominal disk bottom is 1.25 m versus the 1.075 m main-boom top. These are rigid-envelope screens, not a complete swept-volume proof or running-rotor clearance qualification. Actual rotor deflection, airfoil/pitch, bearing motion, structural flex, unsynchronized tilt, actuator failures and gyroscopic loads need engineering and tests.

The external wing/tail solids intentionally overlap the internal spar/rib envelopes. Frame/shell attachment interfaces also overlap. This review did not conduct or pass a full pairwise collision-free assembly check, and it does not represent every internal interface as mechanically fitted.

## Viewer and presentation

The generated CAD isometry was visually inspected: the full assembly is visible, including the raised wing, cabin, battery envelopes, eight rotors, structure and tail. The standalone viewer embeds its mesh and scripts. A fresh browser attempt was blocked before file loading because this sandbox did not permit Chromium's process-singleton socket; **no fresh browser or cross-browser pass is claimed by this review**. The unsuccessful attempt is recorded in `geometry_viewer_attempt.json`. Separate Canvas/DOM-adapter functional tests may verify the application script, but they do not replace browser rendering evidence.

## Remaining scope limits

The 15 mm shell and NACA 0022 wing are display/design envelopes; neither is a validated laminate or aerodynamic section selection. Motor and system blocks are not manufacturer-provided mounting CAD. Blades are flat silhouettes with no pitch, twist, structural section or root fitting. Fasteners, bearing interfaces, tilt locks, detailed cable routing, complete electrical protection, thermal containment and manufacturing tolerances are not provided. Solid validity and sampled rigid clearance do not establish structural strength, aerodynamic feasibility, control authority, aircraft completeness or safe human occupancy.
