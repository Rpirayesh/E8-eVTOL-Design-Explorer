# Independent design reviews and corrections

These reviews verify a preliminary educational concept. They do not establish an airworthy aircraft, approved components, physical performance or a procurement/fabrication release.

| Review | Evidence | Result |
| --- | --- | --- |
| [Numerical review](numerical_review.md) | [Results](numerical_results.json), [independent implementation](verify_numerics.py) | 624 trade cases, 576 adverse cases, 7 named scenarios and 31,070 comparisons; no numerical mismatches |
| [Geometry review](geometry_review.md) | [Results](geometry_results.json), [reproducible solid checks](final_geometry_check.py) | Export, attachment-envelope and sampled tilt checks; see report for exact coverage and limits |
| [Engineering/sourcing review](engineering_review.md) | [Results](engineering_results.json) | Ratings and dated prices corroborated; rotor-out, torque, thermal, mass detail and supplier-matching gaps remain |
| [Viewer software test](viewer_results.json) | [Exact-script Canvas test](test_viewer_canvas.cjs) | 89 interactions, two canvas sizes, no network calls; DOM adapter, not a real browser |

A real Chromium browser test was attempted but could not launch under this environment's Unix-socket restriction. [Optional Playwright test](test_viewer.cjs) is included for reproduction on a workstation with Chromium. No fresh real-browser or cross-browser pass is claimed.

The [November 10 recovery review](recovery_review.md) records fresh numerical, geometry and viewer rechecks, plus the corrected complete-folder archive.

## Corrections applied before publication

- Raised the wing, main spar and ribs above the cabin to remove the spar/seat-back clash. Added high-wing pylons and rails to connect their geometric support envelopes.
- Extended all blade roots into the hub envelopes, added rotating motor yokes, fixed fork crossheads, and overlapping lower standoff mount envelopes. Detailed bearings, joints, fasteners and load transfer are still absent.
- Added 5 mm battery-bay clearance cutouts around all four case envelopes. Bay covers, sealing, containment, attachment loads and thermal design remain open.
- Extended landing-gear struts into the hull/floor attachment envelopes.
- Added separate motor torque and peak-power flags. All single-rotor-out continuous-power screens still fail; outer-row failures also exceed the published maximum torque.
- Added the +25% cell-resistance sensitivity, which drops loaded hover voltage below the motor's published lower voltage range.
- Assigned 20 kg from growth to the boom-system budget: 110 kg boom allowance, 99 kg remaining growth. Total mass and the energy trade-study selection are unchanged; CG was recomputed. Actual laminate/joint masses remain unverified.

The engineering review records the initial 147-component draft, including issues it discovered. The final geometry review covers the corrected 167-component assembly. Historical findings are retained so corrections and unresolved limitations remain inspectable. “Pass” in a numerical or geometry output applies only to that test's scope. There is no overall aircraft flight-readiness pass.
