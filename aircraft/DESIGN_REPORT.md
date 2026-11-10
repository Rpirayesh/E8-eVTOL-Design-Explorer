# E8 aircraft concept design report — edition 0.1

**Preliminary educational concept. No fabrication or flight release.** This is an assembled, reproducible CAD and sizing study, not a completed airworthy aircraft. Independent reviews are in `reviews/`. The search minimum is conditional on the specified surrogate models and finite grid, not a global optimum or a verified cheapest aircraft.

## Configuration and selected study point

Two 95 kg occupants; eight tilting rotors; side-by-side cabin. Nose is −X, Y is lateral, Z is up. All CAD coordinates are millimetres; sizing is SI. The all-rotor tilt architecture follows the original explorer. Wingless removes the wing/tail system but retains the booms and powered rotors; it is a comparative alternative, not a stability solution.

| Quantity | Selected concept |
| --- | --- |
| Total mass including occupants and growth | 1054.8 kg |
| Unallocated mass growth | 99 kg |
| Wing / span / rectangular chord | 12.0 m² / 9.0 m / 1.333 m |
| Rotor diameter / reference rpm | 1.70 m / 1800 rpm |
| Eight rotor stations | x = ±2.10, ±4.45 m; y = ±3.30 m |
| Hover hub height / tilt-pivot height | 2.50 m / 2.10 m |
| High-wing reference height | 1.60 m, above the cabin |
| Overall rotor footprint in hover | 10.60 × 8.30 m |
| Fuselage envelope length | 4.80 m |
| CG estimate incl. assumed growth placement | x=0.017 m, z=0.599 m |
| Study cruise speed / mission distance | 140 km/h / 20 km |
| Hover electrical / cruise electrical load | 210.6 / 86.4 kW |
| Hover per motor shaft / torque | 24.05 kW / 127.6 Nm |
| Hover thrust per rotor | 1293.1 N (131.9 kgf) |
| Battery typical energy / mission allocation | 46.080 / 32.256 kWh |
| 20 km mission chemical energy proxy | 28.18 kWh |
| Energy-based range to the entered reserve | 26.27 km |

These values do not establish maximum speed, range, payload or continuous hover capability. Hover and cruise estimates use unmeasured rotor coefficients and do not resolve interference. The NACA 0022 wing shape in CAD is a geometric envelope; CLmax/CD0 are not validated for that section or Reynolds number.

## Bounded trade study

`analysis/trade_study.csv` contains 624 candidates: winged/wingless, diameters 1.6–1.9 m, wing areas 12–18 m², spans 9–11 m, speeds 120–150 km/h, and 12/16/20 parallel cell strings. Wing mass scales as 95(S/14)^0.9(b/10)^0.6 kg, including an allowance for tail/controls. Other masses and growth remain fixed; rotor/inverter mass is not optimized. Winged candidates require full wing support at CLmax/1.2², ≥20% scalar continuous hover power headroom, sufficient mission energy, ≤40 A/cell resistance-model current, loaded bus ≥400 V, charge voltage ≤800 V, edgewise μ≤0.35, beam stress below the assumed allowable, wing deflection below semi-span/30, and spar depth fitting a 22%-thick wing envelope. There are 46 winged candidates passing these scalar screens.

The selected point minimizes the 20 km mission energy among those candidates. Geometry cost, rotor-out, stability, actual propeller maps, thermal rejection, manufacturing cost and certification are not solved by this objective. The coarse grid and constant profile-drag model can favor smaller rotors and shift the minimum; this is not a rotor recommendation by itself.

## Equations and energy accounting

Mass is the sum in `analysis/mass_budget.csv`; CG is Σ(mᵢxᵢ)/Σmᵢ and likewise for z. Growth has an explicitly assumed location, not a measured one.

q=ρV²/2; W=mg; A=NπD²/4; AR=b²/S. Wing lift is min(W,qSCLmax/1.2²). Drag is qf+qS(CD0+CL²/(πeAR)) when winged, qf when wingless. f is an assumed equivalent drag area including exposed systems; no separate validated tail/boom drag build-up exists. T=sqrt((W−L)²+Ddrag²); α=atan2(Ddrag,W−L). Va=V sinα, Vp=V cosα. The positive root of T=2ρAvi sqrt(Vp²+(Va+vi)²) is found by Brent's method.

Utip=πD·rpm/60; μ=Vp/Utip. Profile power P0=σCd,b ρA Utip³/8. Shaft power is κTvi+Ddrag·V+P0(1+3μ²). This constant-drag rotor approximation is particularly uncertain in axial cruise, where actual pitch, advance ratio, blade stall and efficiency need propeller maps. Electrical load is Pshaft/η+Paux; η=0.92 is an assumed **combined motor/inverter/wiring efficiency**, not an advertised peak motor efficiency.

Cells: 160s16p, 2560 cells. Nominal 576.0 V, maximum 672.0 V; each of four conceptual modules is 160s4p. Nominal energy uses 18 Wh/cell; minimum-capacity and aging sensitivities still need qualification. Cell mass is 181.76 kg; installed pack mass 222.22 kg includes a 22.26% non-cell allowance. This is a functional architecture, not assembly instructions or a production electrical schematic.

Resistance proxy: Rpack=Ns·Rcell/Np, using 12.8 mΩ typical DC resistance. At an assumed minimum **open-circuit** cell voltage of 3.0 V, solve Pload=Voc·I−Rpack·I² using the smaller root. Heat=I²Rpack; chemical power=Pload+heat. This fixed low-OCV approximation is used throughout the mission as a conservative energy screen; it is not a time-resolved SOC/temperature model. Available chemical energy=Enom(0.90−0.20). Mission energy=hover chemical power×3/60 + 3 kWh transition allowance + cruise chemical power×distance/speed. Range=(available−hover−transition)/cruise chemical power×speed. Unlike the original browser explorer, this study explicitly adds a simple battery-resistance loss estimate; the browser defaults were not changed.

The selected worst-voltage hover proxy gives 31.7 A/cell, 415.0 V loaded bus and **33.0 kW battery heat**. With assumed cell heat capacity 1000 J/(kg K), three minutes without cooling gives 32.6 K average rise. This is not a thermal pass: local gradients, cold/aged resistance, connections, containment, ventilation and heat exchanger performance are unresolved. The 12 kg cooling allowance has not been demonstrated adequate.

## Structural screening

Euler-Bernoulli only. Main spar: 120×260 mm hollow rectangular envelope, 4 mm wall, E=70 GPa, density=1600 kg/m³, assumed allowable=250 MPa. For a uniform 3.8g wing load, each semi-span root has M=wL²/2; stress=Mc/I; tip deflection=wL⁴/(8EI). This gives 217.8 MPa and 121.2 mm tip deflection. The bare spar mass estimate is 42.9 kg. The aerodynamic-system mass allowance must still cover ribs, skins, tail, controls and attachments.

Longitudinal boom screen: 150 mm OD / 4 mm wall, supports at |x|=.85 m, two rotor loads at 1.25 and 3.60 m beyond each support, 2.0× nominal hover thrust. M=ΣFᵢaᵢ and δtip=ΣFᵢaᵢ²(3L−aᵢ)/(6EI). Estimated stress 192.3 MPa, tip deflection 136.2 mm. All principal tube lengths give 82.2 kg for the principal tubes. Four diagonal braces add about 10.35 kg, and the high-wing rails add about 3.18 kg. The boom-system allowance is 110 kg after assigning 20 kg from growth; the remaining 99 kg growth remains unallocated. Fittings and actual laminates still require a measured mass build-up.

The load factors and allowable are design assumptions, not a certification basis. Composite anisotropy, compression/buckling, joints, motor torque, gyroscopic and tilt loads, crossbeam transfer, aerodynamic balance, vibration, fatigue, flutter, landing and crash loads remain unverified. **No FEA or CFD was run.** OpenFOAM and a verified structural solver were not available in this environment.

## Failure and sensitivity findings

| Scenario | Mass kg | Hover electrical kW | Mission kWh | Energy margin kWh | Loaded hover bus V |
| --- | --- | --- | --- | --- | --- |
| selected | 1054.8 | 210.6 | 28.18 | 4.08 | 415.0 |
| thin air | 1054.8 | 229.5 | 28.04 | 4.21 | 408.0 |
| low density | 1054.8 | 240.3 | 28.14 | 4.11 | 403.8 |
| wingless same hardware | 977.2 | 189.2 | 31.58 | 0.67 | 422.7 |
| mass plus 15 percent | 1213.1 | 256.6 | 32.54 | -0.29 | 397.3 |
| lower efficiency | 1054.8 | 255.7 | 32.59 | -0.33 | 397.7 |
| resistance plus 25 percent | 1054.8 | 210.6 | 29.00 | 3.26 | 394.6 |

The single-rotor-out allocation proxy solves vertical force, roll/pitch moments and yaw cancellation with an assumed equal torque/thrust ratio. It minimizes maximum rotor thrust, then calculates per-rotor power. **All eight single-rotor-out cases exceed the 30 kW continuous screen** (about 36–42 kW at the most loaded motor). Outer-row failures also require about 219–221 Nm at 1800 rpm, above the published 200 Nm maximum. They are not rescued by quoting the 50 kW peak rating: duration, thermal margin, actual Q/T, transient response and controllability are unverified. A tilt jam, failed bus/module, control-system faults and transition failures are not modeled. The wingless version also needs a dedicated stability/control assessment. Full wing support in the cruise calculation is vertical force balance only; pitch trim, tail lift/downforce, static margin and control authority are not solved.

The +15% mass and reduced-efficiency cases exceed the 20 km energy allocation and fall below the motor's published lower voltage range. A 25% increase in cell resistance alone drops loaded hover voltage to about 395 V, also below 400 V, while increasing battery heat to about 46 kW. These illustrative multipliers are not measured pack aging or cold-temperature characteristics. These sensitivities prevent claiming a robust flight design. The next engineering iteration should address rotor-out/control architecture, rotor maps and thermal closure before any cost optimization is represented as an aircraft optimum.

## Sourcing and cost decision

See `BOM.csv` and `sources/README.md`. The lowest observed listed price does not establish compatibility or lifecycle cost. Candidate motor/inverter/propeller prices require RFQs, so a complete aircraft price or a “cheapest best” parts combination is **not established**.

The cheaper T-MOTOR U15XXL has a $1999 motor listing. Its strongest opened NS62 test row is 101.449 kgf for a short bench condition. Eight give only 811.6 kgf, below the selected 1054.8 kg mass even before any thrust reserve. It is rejected for this full-scale concept. Do not extrapolate or transplant its test table to the larger candidate rotor.

The observed P50B bulk tier is $7.50/cell at 1000+, giving **$19,200 for 2560 bare cells only**, excluding pack production, BMS, protection, thermal management, screening, tax and shipping. Full selected propulsion and aircraft cost remain unknown. E-PROPS' €1304 two-blade aircraft listing is only a market benchmark, not a quotation for the required CW/CCW rotor set. The $422.99 Holybro Pixhawk 6X set is listed only as an educational subscale/bench option; it is not a human-carrying controller selection and its power module must not be connected to this concept's HV bus.

## CAD interpretation and reproducibility

The assembly contains 167 named components with geometrically valid solids at generation. STEP preserves named bodies; FreeCAD imports them as editable solids. The parametric source is Python plus JSON, not a fully constrained native FreeCAD sketch tree. STL is tessellated for GitHub preview; STEP is the precision interchange file. The standalone HTML viewer has no network dependencies. OpenSCAD opens the STL through the supplied wrapper. Blender images use the CAD tessellation, not invented image-generation geometry.

The main wing/tail solids are **external envelopes**, intentionally overlapping internal spars/ribs and fuselage at interfaces. The fuselage's 15 mm geometric shell, flat blade silhouettes, motor length, mounting forks, radiator blocks and avionics boxes are placeholders, not buildable supplier CAD. Blade pitch/twist/airfoil, bolt patterns, bearings, fasteners, tolerances, safety locks, actual skin/core construction and detailed electrical/thermal routing are absent. Battery bays have 5 mm geometric clearance cutouts around the case envelopes; covers, sealing, containment and structural attachments are unresolved. Not every interface is mechanically mated. The isometric rendering hides the canopy to show the cabin. Geometry checks cover solid validity and stated envelopes, not complete collision-free kinematics.

Run from the repository root:

```bash
python -m pip install -r aircraft/requirements.txt
python aircraft/tools/analyze.py
python aircraft/tools/build_cad.py
python aircraft/tools/build_viewer.py
python aircraft/tools/write_report.py
# Optional with separately installed applications:
python aircraft/tools/save_freecad.py
blender -b --python aircraft/tools/render_blender.py
```

## Required next work

1. Agree mission, payload, cruise, environment, footprint, noise and cost constraints with the project team.
2. Obtain manufacturer-confirmed continuous torque/cooling maps, matched CW/CCW propeller data, hub loads and complete quotations.
3. Close battery thermal, aging, minimum energy, voltage, protection and fire containment with instrumented tests.
4. Redesign and verify rotor-out, tilt failure, flight-control and electrical fault tolerance; demonstrate transition trim/stability in simulation and subscale testing.
5. Develop load paths, composite laminates/joints and mass estimates; verify mesh convergence and bench/structural tests before full-scale hardware.
6. Establish the applicable aircraft approval and flight-test process with qualified specialists before human occupancy.
