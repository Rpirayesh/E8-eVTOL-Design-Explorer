# Independent engineering and sourcing review

Review date: 2026-11-09 (America/New_York). Scope: the initial 147-component concept draft, selected parameters, report, BOM, source ledger and scalar analysis outputs. The reviewer did not generate the design, contact vendors, order parts or approve flight hardware.

**Result: suitable for an explicitly labelled educational concept package; not a complete, physically validated aircraft or procurement release.** Manufacturer headline specifications and the dated bulk-cell price were corroborated. Several necessary engineering constraints remain unsatisfied or unverified. Numerical agreement and valid CAD solids do not resolve those findings.

## Findings requiring prominent disclosure

### E01 — Rotor-out cases also exceed maximum motor torque

The draft already states that every single-rotor-out allocation exceeds its conservative 30 kW continuous-power screen. An additional limit follows independently from Q=P/ω at 1800 rpm:

| Failed rotor index (zero based) | Highest shaft power kW | Torque at 1800 rpm Nm | Versus 200 Nm published maximum |
| --- | --- | --- | --- |
| 0 or 1 | 41.229 | 218.724 | Exceeds |
| 2, 3, 4 or 5 | 36.283 | 192.489 | Below, but continuous ability unverified |
| 6 or 7 | 41.686 | 221.152 | Exceeds |

The [REB 50 manufacturer page](https://mgm-compro.com/electric-motor/reb-50-50-kw/) corroborates the 200 Nm maximum. A 50 kW peak power label cannot establish 50 kW at arbitrary rpm: at 1800 rpm and 200 Nm, mechanical power is limited to 37.70 kW. The report should include this separate torque failure. The allocation is still only a static proxy with equal assumed torque/thrust ratio; it is not a rotor-out controllability simulation.

Normal equal-load hover requires 24.05 kW and 127.58 Nm per rotor; the CG-adjusted static allocation has a 24.18 kW maximum. The published 30–40 kW continuous range does not supply a continuous torque/cooling map at that operating point. Normal continuous hover therefore remains conditional on manufacturer-confirmed windings, voltage, rpm, cooling and propeller loading.

### E02 — Modest resistance variation removes the voltage margin

Independent calculation using P=Voc·I−R·I², Voc=480 V and R=0.128 Ω reproduces the nominal hover proxy. Changing resistance alone shows:

| Resistance multiplier | Loaded voltage V | Cell current A | Battery heat kW |
| --- | --- | --- | --- |
| 1.00 | 415.05 | 31.71 | 32.96 |
| 1.25 | 394.60 | 33.36 | 45.58 |
| 1.50 | 371.01 | 35.48 | 61.87 |
| 2.00 | 300.69 | 43.78 | 125.59 |

At only 1.25× resistance, loaded voltage falls below the motor page's stated 400 V lower range before the 40 A/cell screening limit is reached. This should be included alongside the existing mass/efficiency sensitivities. These factors are illustrative sensitivity values, not measured aging/cold multipliers for this pack.

The constant 3.0 V/cell OCV assumption is clearly labelled. The nominal-voltage energy allocation, fixed OCV resistance proxy and SOC reserve do not form a time-resolved electrochemical model. Resistance depends on SOC, temperature, age and production variation. Neither the 400 V operating boundary nor 40 A/cell is a substitute for a supplier-confirmed continuous motor/pack envelope.

### E03 — Thermal design has not closed

The draft discloses about 33 kW battery heat in the worst-voltage hover proxy and a 32.6 K average adiabatic cell rise over three minutes. Adding the assumed combined drivetrain losses gives about 49.69 kW total battery-plus-drivetrain heat before auxiliary heat. The 12 kg cooling-system allowance has no demonstrated rejection capacity, flow path, coolant budget, hover airflow or safe transient temperature distribution. A lumped average does not bound cell hot spots. Thermal management, fire containment and single-module fault isolation require detailed design and tests; they remain aircraft blockers.

### E04 — Tube mass already strains the boom allowance

The production beam calculation includes 82.19 kg for the principal 150 mm OD / 4 mm wall tubes at the assumed 1600 kg/m³ density. Four CAD diagonal braces, 65 mm OD / 3 mm wall and 2.767 m each, add approximately 10.35 kg under the same material-density assumption. Together they reach 92.54 kg before boom fittings or other attachments, exceeding the 90 kg boom allowance. Growth can cover this, but it must be assigned and the mass/CG analysis rerun. This is not a demonstrated mass closure.

The homogeneous beam allowable is correctly called an assumption. No qualified laminate, buckling, fitting, torque, gyroscopic, fatigue, landing or aeroelastic assessment exists. The rectangular wing spar envelope and its scalar stress screen do not validate a composite wing.

### E05 — A matched propeller has not been selected

The [E-PROPS adjustable-pitch range](https://uav.e-props.fr/adjustable-pitch.php) supports the stated matched CW/CCW diameter restriction; the selected 1.70 m envelope lies inside the range. Its pages require matching to the motor, aircraft and speed. That does not substantiate 131.9 kgf hover thrust at 1800 rpm from a specific two-blade item. There is no chosen blade pitch, section, twist, hub part number, thrust/torque map, allowable in-plane hub load or rotating inertia. The 2 kg per-unit rotor mass remains an allowance. The conservative correct label is an inquiry candidate, as in the draft, not a purchasable matched design.

The combined motor/inverter efficiency is explicitly assumed rather than copied from a peak rating. The constant profile-drag approximation can alter the diameter and cruise-speed minimum. The finite-grid minimum must remain a model-dependent study point.

## Sourcing checks

| Item | Independent source check | Assessment |
| --- | --- | --- |
| REB 50 | Manufacturer page: 12 kg; 50 kW peak; 30–40 kW continuous; 200 Nm maximum; 400–800 V; 1500–4000 rpm | Ledger agrees; quote and operating map required |
| HBCi 400800 | [Manufacturer](https://mgm-compro.com/controllers-inverters-escs/hbci-400800/): 120–800 V; 4 kg cold-plate version, heavier packaged cooler versions | 672 V charge ceiling fits nominal voltage range; this does not verify surge, cooling, motor pairing or electrical architecture |
| P50B cells | [Opened seller page](https://www.18650batterystore.com/products/molicel-21700-p50b-5000mah-50a-battery) shows $11.99 single-cell and $7.50 at 1000+ quantity | 2560×$7.50=$19,200 cell-only; pricing/stock require checkout or quote; no complete-aircraft price |
| Cheaper U15XXL | [Manufacturer's NS62 bench row](https://store.tmotor.com/product/u15xxl-manned-aircraft-combo.html): maximum reported 101.449 kgf, short bench condition | Eight total 811.592 kgf, below concept mass even without reserve; rejection is justified |

The 4 kg inverter mass is specifically the cold-plate version. Published cooled-version weights cannot be conflated with that number. The draft's separate cooling allowance acknowledges this but has not sized it.

The opened cell price differs from an indexed promotional excerpt; using the inspected bulk tier with its date is appropriate. No evidence establishes a globally cheapest rotor or propulsion set, or a best lifecycle-cost aircraft. E-PROPS' separate aircraft propeller price is correctly kept out of the selected BOM. The optional educational Pixhawk comparison is correctly distinguished from human-carrying flight-control selection and the high-voltage bus.

## Mass accounting and completeness

The BOM's masses, including non-cell battery-module mass only on the battery-module line, sum to 864.84997 kg with growth and without occupants. Adding 190 kg occupants reproduces 1054.84997 kg. No battery-cell double counting was found. This is arithmetic closure of allowances, not measured component or CAD-density mass closure.

Subsystems represented by envelopes still need mechanical interfaces, fasteners, bearings, locks, control surfaces/actuators, protection coordination, grounding/isolation, failure detection, redundant low-voltage power, control software, flight dynamics, crashworthiness, maintainability and test plans. The CAD does not provide manufacturing drawings or an assembly-ready kit.

## Release wording

The report already states that no CFD/FEA was run and that rotor-out, thermal design, actual rotor performance and flight stability remain open. Retain those statements in the README and final delivery. Add E01/E02 explicitly and quantify E04. Publication is appropriate as a preliminary model with failed screens and open requirements, not as a fully validated or airworthy aircraft. No independent engineering review here supplies a professional design approval, physical validation or flight authorization.
