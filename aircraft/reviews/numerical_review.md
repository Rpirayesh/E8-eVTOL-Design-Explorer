# Independent numerical review

**Decision: the disclosed arithmetic is reproducible; the aircraft is not physically validated or released for fabrication/flight.** No numerical mismatch was found within the review coverage below. Several major engineering screens fail, and those failures must remain visible wherever the model is shared.

## Method and coverage

`verify_numerics.py` independently implements mass/CG, wing/drag force balance, hover momentum power, tilted-rotor inflow, profile power, battery resistance loss, mission energy/range and elementary beam equations. It imports the production module only for actual values to compare; expected values are calculated by the separate implementation. Pure axial inflow uses a closed-form root, other inflow uses a different numerical solver, battery current uses a numerical root rather than the production quadratic expression, and rotor allocation optima are independently found by bisection of a thrust-cap feasibility problem.

The saved `numerical_results.json` records:

- 624 complete trade-grid cases, including reproduction of the scalar screening decisions and the selected finite-grid minimum.
- 576 separate adverse operating points: winged/wingless; density 0.7, 0.9, 1.225 and 1.3 kg/m³; speeds 20, 80, 140 and 220 km/h; rotor diameters 1.6 and 1.9 m; mass multipliers 0.8, 1.0 and 1.3; resistance multipliers 0.75, 1.0 and 1.25.
- Seven named scenarios from the saved analysis.
- Wing-spar and boom bending checks.
- All nine static allocations: nominal and each of eight single-rotor failures, checking force, roll/pitch and assumed yaw balance, failed-rotor zero thrust, optimal maximum-thrust cap, power and torque.
- **31,070 numeric comparisons, zero mismatches; maximum relative error 4.94×10⁻¹².** The absolute comparison tolerance is scaled by max(1, |expected|); it is a floating-point implementation check, not an accuracy bound on aircraft predictions.

The independent grid has 46 eligible winged points and reproduces the selected 1.70 m diameter, 12 m² wing, 9 m span, 140 km/h and 16 parallel strings. That minimum applies only to the declared energy objective and listed constraints; it is not a global aircraft optimum or a lowest-cost solution.

Run from the repository root:

```bash
python aircraft/reviews/verify_numerics.py
```

The input and implementation SHA-256 hashes in the JSON identify the reviewed numerical snapshot. Rerun the script after a numerical input/code change.

## Independent selected-point examples

| Quantity | Recomputed value |
| --- | --- |
| Mass incl. two occupants and growth | 1054.850 kg |
| Hover shaft / electrical load | 192.381 / 210.610 kW |
| Mean hover torque per motor at 1800 rpm | 127.577 Nm |
| Cruise drag / shaft / electrical load | 1679.041 N / 78.104 / 86.396 kW |
| Nominal battery / available mission energy | 46.080 / 32.256 kWh |
| Low-OCV hover battery current | 507.435 A pack / 31.715 A per cell |
| Loaded hover bus / battery heat | 415.048 V / 32.959 kW |
| Mission chemical energy / remaining allocation | 28.178 / 4.078 kWh |
| Energy-based range under the stated surrogate | 26.274 km |
| Wing-spar stress / tip deflection | 217.776 MPa / 121.153 mm |
| Longitudinal-boom stress / tip deflection | 192.287 MPa / 136.226 mm |

## Engineering findings that arithmetic verification cannot clear

1. **Rotor-out fails.** Each single failure requires more than the conservative 30 kW continuous allowance at the most loaded remaining rotor: about 36.28–41.69 kW. Outer-row failures additionally require roughly 219–221 Nm at 1800 rpm, exceeding the cited motor's 200 Nm maximum. A 50 kW peak headline does not make those points possible at that rpm. Even a static proxy pass would not establish transient control or fault tolerance.
2. **Battery voltage margin is fragile.** Increasing the single assumed DC resistance by 25% lowers the hover bus to 394.604 V, below the candidate motor's stated 400 V lower range; battery heat rises to 45.578 kW. The design has not closed thermal rejection, cold/aged voltage, interconnect losses or fire containment. The nominal heat value alone is substantial.
3. **Mass sensitivity is material.** The +15% mass and degraded-efficiency scenarios exceed the 20 km energy allocation and go below the motor voltage screen. Nominal “passes” do not represent a robust operating envelope.
4. **Structural mass is not closed.** Principal tube geometry gives 82.194 kg. The four modeled 65 mm OD/3 mm wall diagonal braces add approximately 10.348 kg using their 2.767 m length and the same density. These bare tubes total **92.542 kg, exceeding the original 90 kg boom-system allowance before fittings**. Disposition: the author transferred 20 kg from unallocated growth to this system, increasing its allowance to 110 kg and reducing growth from 119 to 99 kg. Total design mass and power are preserved; estimated CG height changes. The additional modeled high-wing support rails are about 3.18 kg. This budget correction does not establish installed mass, joint strength or complete load paths. The wing-spar mass remains 42.854 kg before the other aero-system items.
5. **Trim and rotor physics remain open.** Full wing support is a vertical-force result; the calculation omits tail lift and pitch trim. Actual rotor geometry, airfoil/pitch maps, axial-cruise profile losses, rotor/wing interference, tilt transients and nonlinear torque/thrust relationships are absent. The equal Q/T yaw allocation is a declared mathematical proxy, not a verified rotor model.
6. **The beam result is conditional.** Homogeneous E, density and allowable do not establish composite laminate, joint, buckling, fatigue, crash, flutter or ultimate-load capability. Crossbeam load transfer and gyroscopic/tilt loads are not included. Passing the scalar wing screen is not a structural release.

## Interpretation and reuse limits

Keep the repository labeled an educational concept and a model-verification study. The review supports that the published numbers follow the disclosed equations. It does not support flight-ready, fully optimized, cheapest suitable aircraft, physically validated range, qualified components, complete electrical design or certified structure claims.

The intended architecture is fixed at eight rotors. Some production functions use literal `8` even though a `rotor_count` field exists; changing that field alone is not a supported architecture change. Likewise, modifying arbitrary geometry parameters requires checking that all CAD and analysis scripts use them consistently.

Final numerical verification was rerun after the 110 kg boom / 99 kg growth budget disposition; the saved JSON hashes identify that revised snapshot. The count remains 31,070 comparisons with zero mismatches.
