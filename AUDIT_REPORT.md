# E8 offline explorer — independent audit and stress tests

Review date: November 9, 2026 (America/New_York). Audited delivered edition: 1.0. Corrected edition: 1.1.

## Conclusion

The declared lift, thrust, power, battery and range equations are internally consistent. An independently coded Python solver reproduced JavaScript power and energy-based range across **20,245 bounded operating points** without calculation or conservation failures. Three separate agent reviews covered physics, numerical stress testing and offline/software reliability.

This establishes implementation consistency under the stated assumptions. It does **not** establish measured aircraft performance, aerodynamic feasibility, controllability or airworthiness. No experimental rotor/airframe dataset was available, and no empirical uncertainty bound is claimed.

## Issues found and corrected

1. **False energy shortfall at an exact-range boundary.** In edition 1.0, 301 of 3,061 eligible exact-range trips were falsely classified as shortfalls solely due to floating-point cancellation. For example, winged defaults with density 0.7 kg/m³ and a trip distance of 51.05903077241828 km produced a margin of −3.552713678800501e−15 kWh even though trip distance equaled calculated range. Edition 1.1 treats margins within `1e-10 × max(1, available energy, trip energy)` kWh as numerical zero, consistently in status, CSV and the energy budget. At feasible exact-range boundaries within the permitted energy domain this is below 0.09 J. It does not materially extend range.
2. **CSV export hidden at 621–820 CSS pixels.** A responsive rule hid the sole export button at common tablet/narrow-window widths. Edition 1.1 preserves the button and supplies the accessible name “Export study as CSV.” Export is also blocked while any invalid numeric edit remains highlighted, avoiding ambiguity between pending text and the last valid assumptions.
3. **Model scope needed greater prominence.** This was an interpretation risk, not an algebra error. Extreme rotor assumptions can pass power/energy screens despite blade loading the model cannot substantiate. Edition 1.1 labels the output “Energy-based range,” puts the qualification beside the results, shows hover/cruise blade-loading diagnostics, and adds an embedded exact-range regression check. No universal blade-stall threshold is invented.

The input defaults and predicted lift, power and range are unchanged. Only the treatment of numerically zero trip margins changes classification. The separate private hosted site was not modified by this offline audit.

## Numerical coverage

| Check | Coverage | Result in edition 1.1 |
| --- | ---: | --- |
| Joint random inputs, fixed seed 20261110 | 20,000 operating points | No solver/conservation failures |
| One-input lower/middle/upper boundary cases | 168 operating points | Passed |
| Mass/battery/disk/density/speed corners | 64 operating points | Passed |
| Named design and failure examples | 13 operating points | Passed |
| Eligible exact-range trips derived from main suite | 3,061 trips | No false shortfalls after correction |
| Separate exact/inside/outside mission regressions | 600 trips | 200 exact, 200 at 0.1 m inside, 200 at 0.1 m outside: all correct |
| Invalid inputs | 339 cases | NaN, infinities, wrong types, range and SOC/reserve violations correctly rejected |

Coverage counts describe checks; they should not be added as a count of unique aircraft designs. Cases that exceed a screen are expected to return a withheld range, rather than a numerical range presented as usable.

The independent implementation uses dimensionless Brent roots and algebraic projections. The app uses fixed-count bisection and trigonometric projections. Both apply the declared physical assumptions. Maximum scaled discrepancies `abs(JS−Python)/max(1,abs(Python))` were 6.23e-15 for electrical cruise power and 1.65e-14 for energy-only range. Those are arithmetic agreement measures, not estimates of physical accuracy. Five separate physics spot checks use a Newton root and an analytical pure-axial case.

## Different examples checked

The figures below use defaults except the full overrides recorded in `VALIDATION_EXAMPLES.json`. Power is electrical kW; range includes entered hover/transition energy and the selected reserve. “Pass selected screens” refers only to the app's power, energy and edgewise-advance-ratio checks, not flight feasibility.

| Case | Configuration | Speed km/h | Cruise kW | Hover kW | Energy-based range km | Screen outcome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Default winged | Winged | 120 | 55.469 | 130.866 | 46.205 | Pass selected screens |
| Default wingless | Wingless | 120 | 69.888 | 117.649 | 37.428 | Pass selected screens |
| Low-speed wing assist | Winged | 40 | 95.164 | 130.866 | 8.977 | Pass selected screens |
| Full wing support | Winged | 160 | 83.205 | 130.866 | 41.070 | Pass selected screens |
| Thin air | Winged | 120 | 47.851 | 160.787 | 51.059 | Pass selected screens |
| Heavy battery | Winged | 140 | 93.665 | 170.731 | 103.595 | Pass selected screens |
| Battery power failure | Winged | 120 | 55.469 | 130.866 | Withheld | Screen failed |
| Shaft power failure | Wingless | 120 | 69.888 | 117.649 | Withheld | Screen failed |
| Energy exhaustion | Winged | 120 | 50.251 | 96.867 | Withheld | Screen failed |
| Tight reserve | Winged | 120 | 55.469 | 130.866 | 0.857 | Pass selected screens |
| Very small rotors | Wingless | 120 | 249.762 | 302.440 | Withheld | Screen failed |
| High-speed wingless model limit | Wingless | 220 | 129.621 | 107.289 | Withheld | Screen failed |
| Large disks heavy lift | Wingless | 120 | 152.589 | 313.936 | 132.120 | Pass selected screens |

Examples include a 500 kg battery with larger rotors/higher motor ratings; a 1C pack that cannot supply the required power; a 5 kW-per-motor failure; a small depleted-energy mission; and a 61% starting SOC with a 60% reserve and zero entered hover/transition cost. Zero allowances **omit those costs**; they do not predict a zero-energy takeoff or transition.

## One baseline hand check

For winged defaults at 120 km/h: mass = 330 + 2×95 + 180 + 60 = 760 kg; weight = 7,453.054 N. Total disk area = 8π(1.8²)/4 = 20.3575 m². Dynamic pressure = 680.5556 Pa. The allowed wing lift coefficient is 1.5/(1.2²) = 1.041667, so wing lift = 7,089.1204 N and rotor vertical support = 363.9336 N.

The pack is 180×220/1000 = 39.6 kWh nominal; available energy above the 20% reserve from 90% starting charge is 39.6×(90−20)/100 = 27.72 kWh. Hover plus the entered transition allowance consumes 130.865741×2/60 + 2 = 6.362191 kWh. Thus range = (27.72−6.362191)/55.469303×120 = 46.204602 km. The independently coded solver agrees.

## Where physical accuracy remains unverified

Rotor blade stall/loading, loading-dependent blade drag, rotor interference, axial-flow profile correction, compressibility, wing download, detailed transition/climb trajectory, trim, stability/control, rotor-out behavior, structural and thermal limits, wind and battery aging are not resolved. Parameters are illustrative assumptions rather than measurements of this aircraft.

The physics review deliberately tested a 400 kg wingless concept with 0.8 m rotors, 120 m/s tip speed and solidity 0.04, with enough selected motor/pack power. The app reports 79.636 kW cruise, 81.130 kW hover and 14.389 km and clears the selected screens. Yet hover blade loading Cₜ/σ is 1.38249 and a rough mean blade lift coefficient is about 8.295. The simplified model cannot substantiate aerodynamic operation there. The added diagnostics make the unchecked constraint visible; they are not a blade-stall predictor.

A separate sensitivity uses winged defaults at 200 km/h. Adding only the NASA pure-axial profile correction, while holding all other assumptions fixed, changes electrical cruise power from 131.364 to 137.187 kW and range from 32.517 to 31.137 km. This is a sensitivity to one omitted term, **not** a measured error bar, validated correction or worst-case bound. Other omitted physics may matter more.

## Offline/software verification

The final corrected HTML passed **19 software test groups and 2,212 simulated UI operations**. Coverage includes 1,000 repeated input edits/resets, 56 numeric min/max edits, 168 invalid-edit cases, 10 missing/corrupt/unavailable-storage scenarios, configuration/view/range controls, chart click conversion, invalid-input export blocking, and 40 CSV exports checked against both current configurations and all 101 speed-sweep rows. No network API calls occurred in the offline runtime tests. Static checks find only embedded scripts, styles and benchmark data, and a security policy that blocks connections.

Fresh browser checks of the exact file served through the supported local HTTP preview confirmed functioning controls, 9/9 embedded checks, 5/5 numerical reference cases, rotor diagnostics, reset, invalid-export blocking and successful CSV export after correction. The tablet export fix was checked against the responsive CSS rules; a separate 700 px rendered viewport check was not available.

**Verification limits:** a fresh direct `file://` browser run could not be completed because native desktop text input failed through the test environment's accessibility provider, while the cloud browser permits only HTTP/HTTPS. No security settings were changed or bypassed. Cross-browser runs in Edge, Firefox and Safari were not completed. Dependency-free packaging, denied-storage behavior, and no-network execution were tested, but those do not substitute for testing every browser/platform combination.

## Primary references

- NASA Glenn, Lift Equation: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation-2/
- NASA Glenn, Induced Drag Coefficient: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/
- Wayne Johnson, NDARC Theory, NASA TP 2009-215402, Appendix 3, Release 1.7 (December 2012): https://rotorcraft.arc.nasa.gov/Publications/files/NASA%20TP-2009-215402-app3.pdf . §11-4.1, printed pp. 94–95: ideal inflow; §11-5, pp. 104–105: power split/profile factor; §11-5.1.2, pp. 106–108: loading-dependent drag, stall and compressibility. The explorer is an independent simplification, not the NDARC software.

## Traceability and reproduction

- Original ZIP SHA-256: `269c8ac8b29e29c3c85f8c6c02d8119c09dfc4db0ee5731eceffec025ccce783`
- Corrected HTML SHA-256: `a9aa0bf10cdfd63cecf21506f5413119ebb7029bdecc7963080a53525f3c46c7`
- Tested extracted model SHA-256: `f1a661affc8586b7e34f4f582630d9b9dfcaae6240ebfc2abdcd7fe0b1e36ee7`

`audit_tests/` contains the numerical, physics and software review scripts and their result summaries. These are optional developer verification materials; students do not need them to run the HTML. The numerical audit requires Python with NumPy/SciPy and Node.js. From this extracted package, run `python3 audit_tests/numerical/audit.py --model audit_tests/model-extracted.cjs --prefix rerun_`, `python3 audit_tests/numerical/boundary_regression.py --model audit_tests/model-extracted.cjs`, and `node audit_tests/numerical/invalid_input_test.cjs audit_tests/model-extracted.cjs`. The HTML remains the standalone student app.
