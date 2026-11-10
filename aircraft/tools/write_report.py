"""Generate readable design documentation, sourcing ledger, BOM and plots."""
from pathlib import Path
import json,csv,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import analyze
ROOT=Path(__file__).resolve().parents[1]

SOURCES=[
 dict(id='S01',title='MGM COMPRO REB 50',url='https://mgm-compro.com/electric-motor/reb-50-50-kw/',kind='manufacturer',facts='12 kg; 50 kW peak; 30–40 kW continuous; 200 Nm maximum torque; 1500–4000 rpm; 400–800 V. Installation-dependent ratings. Price by quotation.'),
 dict(id='S02',title='MGM COMPRO HBCi 400800',url='https://mgm-compro.com/controllers-inverters-escs/hbci-400800/',kind='manufacturer',facts='120–800 V; 4 kg cooling-plate version. Larger cooled versions weigh more. Specific cooling integration and price require supplier confirmation. Oversized for this concept.'),
 dict(id='S03',title='E-PROPS adjustable-pitch UAV range',url='https://uav.e-props.fr/adjustable-pitch.php',kind='manufacturer',facts='Ground-adjustable range for 50–180 kW engines. Matched CW/CCW diameter limited to 74.8 inches. Exact thrust, pitch, rpm, hub and aircraft match require supplier engineering; range membership does not establish compatibility.'),
 dict(id='S04',title='Molicel P50B product and datasheet v1.1',url='https://www.molicel.com/product/inr-21700-p50b/',kind='manufacturer',facts='3.6 V nominal; 5.0 Ah typical; maximum cell mass 71 g; manufacturer page lists 60 A discharge. Cell-level ratings are not a complete pack qualification.'),
 dict(id='S05',title='Molicel P50B original datasheet',url='https://www.molicel.com/wp-content/uploads/4.TR%E7%B0%A1%E6%98%93%E8%A6%8F%E6%A0%BC_INR21700P50B_1.1_Product-Data-Sheet-of-INR-21700-P50B-80122.pdf',kind='manufacturer',facts='18.0 Wh typical / 17.5 Wh minimum; 4.2 V charge; 12.8 mΩ typical DC impedance at 50% SOC; 60 A discharge with 80°C cutoff. Screening uses 40 A, 3.0 V OCV and constant resistance, not measured pack behavior.'),
 dict(id='S06',title='18650 Battery Store P50B retail/bulk listing',url='https://www.18650batterystore.com/products/molicel-21700-p50b-5000mah-50a-battery',kind='seller',facts='Opened page: $11.99 single cell; $7.50 at 1000+ quantity. Search excerpt showed a different promotion. Use the opened bulk tier for the dated cell-only cost, subject to checkout and stock confirmation.'),
 dict(id='S07',title='T-MOTOR U15XXL combination specifications and test table',url='https://store.tmotor.com/product/u15xxl-manned-aircraft-combo.html',kind='manufacturer/seller',facts='Motor listing $1999; Thunder 300A 24S $1599; NS62×24 listing $2599 (sales unit needs confirmation). NS62 test maximum is 101.449 kgf at 96 V, 209.09 A, 2203 rpm; coil temperature note 184°C at 32°C ambient after one minute at full throttle. This is not a continuous installed rating.'),
 dict(id='S08',title='E-PROPS aircraft prices (comparison only)',url='https://aircraft.e-props.fr/ordering.php',kind='manufacturer/seller',facts='Durandal/Excalibur two-blade listing €1304 excluding tax/shipping. This is not a quotation for the proposed matched UAV rotors and is not entered as their price.'),
 dict(id='S09',title='Holybro Pixhawk 6X',url='https://holybro.com/products/pixhawk-6x',kind='manufacturer/seller',facts='Opened Standard v2A / PM02D selection $422.99. Educational subscale/bench candidate only; the included power module is not rated for the concept HV bus. Not a qualified two-person flight-control system.'),
 dict(id='S10',title='NASA lift equation',url='https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation-2/',kind='theory',facts='Reference for L=ρV²SCL/2; airfoil coefficients remain assumptions.'),
 dict(id='S11',title='NASA NDARC theory appendix',url='https://rotorcraft.arc.nasa.gov/Publications/files/NASA%20TP-2009-215402-app3.pdf',kind='theory',facts='Reference background for rotor momentum and profile-power estimates. This repository is not NDARC and does not implement its complete rotor model.')
]

def main():
 p=json.loads((ROOT/'selected_design.json').read_text());component_count=len(json.loads((ROOT/'cad'/'assembly_manifest.json').read_text())['components']);r=json.loads((ROOT/'analysis'/'results.json').read_text());v=r['scenarios']['selected'];b=r['battery']
 for s in SOURCES:s['checked_date']='2026-11-09';s['status']='Web source inspected; not a supplier quotation or approval'
 (ROOT/'sources'/'source_ledger.json').write_text(json.dumps(SOURCES,indent=2)+'\n')
 items=[
 ('Motor','MGM COMPRO REB 50 candidate',8,12,'RFQ','S01','30 kW conservative continuous screen; full torque/cooling map and winding required'),
 ('Inverter','MGM COMPRO HBCi 400800 cold-plate candidate',8,4,'RFQ','S02','800 V ceiling exceeds 672 V charge; oversized; cooling mass separate'),
 ('Rotor','Matched two-blade CW/CCW propeller; E-PROPS inquiry candidate',8,2,'RFQ','S03','1.70 m envelope; 4 CW + 4 CCW; 1800 rpm assumed; hover requires about 132 kgf each; no matched blade data'),
 ('Cells','Molicel P50B',b['cells'],.071,'7.50 USD/cell (1000+ tier)','S04,S05,S06','Cell-only cost; traceability, screening, pack production and shipping extra'),
 ('Battery modules','Custom protected pack modules',4,(b['installed_mass_kg']-b['cell_mass_kg'])/4,'RFQ','assumption','Non-cell mass only here, to avoid double counting cells. Four 160s4p envelopes; architecture only'),
 ('Tilt mechanisms','Custom trunnion, actuator, lock and sensors',8,4,'RFQ','assumption','Kinematic envelopes; bearings, fail-safe locks, gear ratio and fatigue loads unresolved'),
 ('Primary frame','Fuselage structure, floor and shell',1,90,'RFQ','assumption','Allowable mass budget; CAD shell thickness is visual, not a laminate schedule'),
 ('Boom system','CFRP tubes, outriggers and joints',1,110,'RFQ','assumption','Tube screen 150 mm OD / 4 mm wall; joints and crossbeam load transfer not solved'),
 ('Aero system','Wing, tail, surfaces and fittings',1,p['wing_system_mass_kg'],'RFQ','assumption','Mass scaling allowance; includes tail. CFRP laminate and attachment details unresolved'),
 ('HV system','BMS interfaces, fuses, contactors, precharge, isolation, harness',1,18,'RFQ','assumption','Functional requirements only; no production wiring design'),
 ('Cooling','Cold plates, radiator, pumps, ducts and coolant',1,12,'RFQ','assumption','Mass allowance; 33 kW battery heat proxy during hover is not substantiated by cooling design'),
 ('Landing gear','Wheels, struts, brakes and attachments',1,20,'RFQ','assumption','Geometric arrangement only; drop/crash/braking tests required'),
 ('Avionics','Flight-control system, sensors and redundant LV supplies',1,10,'RFQ','assumption','Human-carrying architecture not selected or qualified'),
 ('Cabin','Seats, controls and restraints',1,18,'RFQ','assumption','Crashworthy seats/restraints require engineering and tests'),
 ('Safety','Detection, containment and emergency equipment',1,12,'RFQ','assumption','No parachute selection or deployment-envelope claim'),
 ('Growth','Unallocated mass growth',1,p['growth_allowance_kg'],'not procurement','assumption','99 kg at assumed x=0, z=.3; move/resize when actual component masses are known')]
 with (ROOT/'BOM.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['subsystem','candidate','quantity','unit_mass_kg_or_allowance','price_basis','source_ids','qualification_gap']);w.writerows(items)
 ledger='\n'.join(f"- **{s['id']} — [{s['title']}]({s['url']})** ({s['kind']}, checked {s['checked_date']}): {s['facts']}" for s in SOURCES)
 (ROOT/'sources'/'README.md').write_text('# Source ledger\n\nDated observations, paraphrased. Do not treat a product title or sales claim as an aircraft qualification. Prices can change. No vendor was contacted and no order was placed.\n\n'+ledger+'\n')
 table='\n'.join(f"| {key.replace('_',' ')} | {x['mass_kg']:.1f} | {x['hover_electrical_kw']:.1f} | {x['trip_kwh']:.2f} | {x['energy_margin_kwh']:.2f} | {x['battery_hover_terminal_v_screen']:.1f} |" for key,x in r['scenarios'].items())
 report=f'''# E8 aircraft concept design report — edition 0.1

**Preliminary educational concept. No fabrication or flight release.** This is an assembled, reproducible CAD and sizing study, not a completed airworthy aircraft. Independent reviews are in `reviews/`. The search minimum is conditional on the specified surrogate models and finite grid, not a global optimum or a verified cheapest aircraft.

## Configuration and selected study point

Two 95 kg occupants; eight tilting rotors; side-by-side cabin. Nose is −X, Y is lateral, Z is up. All CAD coordinates are millimetres; sizing is SI. The all-rotor tilt architecture follows the original explorer. Wingless removes the wing/tail system but retains the booms and powered rotors; it is a comparative alternative, not a stability solution.

| Quantity | Selected concept |
| --- | --- |
| Total mass including occupants and growth | {v['mass_kg']:.1f} kg |
| Unallocated mass growth | {p['growth_allowance_kg']:.0f} kg |
| Wing / span / rectangular chord | {p['wing_area_m2']:.1f} m² / {p['wing_span_m']:.1f} m / {p['wing_area_m2']/p['wing_span_m']:.3f} m |
| Rotor diameter / reference rpm | {p['rotor_diameter_m']:.2f} m / {p['rotor_rpm']} rpm |
| Eight rotor stations | x = ±2.10, ±4.45 m; y = ±3.30 m |
| Hover hub height / tilt-pivot height | 2.50 m / 2.10 m |
| High-wing reference height | 1.60 m, above the cabin |
| Overall rotor footprint in hover | 10.60 × 8.30 m |
| Fuselage envelope length | 4.80 m |
| CG estimate incl. assumed growth placement | x={v['cg_x_m']:.3f} m, z={v['cg_z_m']:.3f} m |
| Study cruise speed / mission distance | {p['cruise_kph']} km/h / {p['mission_km']} km |
| Hover electrical / cruise electrical load | {v['hover_electrical_kw']:.1f} / {v['cruise_electrical_kw']:.1f} kW |
| Hover per motor shaft / torque | {v['hover_shaft_kw']/8:.2f} kW / {v['hover_torque_each_nm']:.1f} Nm |
| Hover thrust per rotor | {v['hover_thrust_each_n']:.1f} N ({v['hover_thrust_each_n']/analyze.G:.1f} kgf) |
| Battery typical energy / mission allocation | {b['nominal_kwh']:.3f} / {v['usable_kwh']:.3f} kWh |
| 20 km mission chemical energy proxy | {v['trip_kwh']:.2f} kWh |
| Energy-based range to the entered reserve | {v['energy_based_range_km']:.2f} km |

These values do not establish maximum speed, range, payload or continuous hover capability. Hover and cruise estimates use unmeasured rotor coefficients and do not resolve interference. The NACA 0022 wing shape in CAD is a geometric envelope; CLmax/CD0 are not validated for that section or Reynolds number.

## Bounded trade study

`analysis/trade_study.csv` contains {r['optimization']['candidates']} candidates: winged/wingless, diameters 1.6–1.9 m, wing areas 12–18 m², spans 9–11 m, speeds 120–150 km/h, and 12/16/20 parallel cell strings. Wing mass scales as 95(S/14)^0.9(b/10)^0.6 kg, including an allowance for tail/controls. Other masses and growth remain fixed; rotor/inverter mass is not optimized. Winged candidates require full wing support at CLmax/1.2², ≥20% scalar continuous hover power headroom, sufficient mission energy, ≤40 A/cell resistance-model current, loaded bus ≥400 V, charge voltage ≤800 V, edgewise μ≤0.35, beam stress below the assumed allowable, wing deflection below semi-span/30, and spar depth fitting a 22%-thick wing envelope. There are {r['optimization']['eligible_winged']} winged candidates passing these scalar screens.

The selected point minimizes the 20 km mission energy among those candidates. Geometry cost, rotor-out, stability, actual propeller maps, thermal rejection, manufacturing cost and certification are not solved by this objective. The coarse grid and constant profile-drag model can favor smaller rotors and shift the minimum; this is not a rotor recommendation by itself.

## Equations and energy accounting

Mass is the sum in `analysis/mass_budget.csv`; CG is Σ(mᵢxᵢ)/Σmᵢ and likewise for z. Growth has an explicitly assumed location, not a measured one.

q=ρV²/2; W=mg; A=NπD²/4; AR=b²/S. Wing lift is min(W,qSCLmax/1.2²). Drag is qf+qS(CD0+CL²/(πeAR)) when winged, qf when wingless. f is an assumed equivalent drag area including exposed systems; no separate validated tail/boom drag build-up exists. T=sqrt((W−L)²+Ddrag²); α=atan2(Ddrag,W−L). Va=V sinα, Vp=V cosα. The positive root of T=2ρAvi sqrt(Vp²+(Va+vi)²) is found by Brent's method.

Utip=πD·rpm/60; μ=Vp/Utip. Profile power P0=σCd,b ρA Utip³/8. Shaft power is κTvi+Ddrag·V+P0(1+3μ²). This constant-drag rotor approximation is particularly uncertain in axial cruise, where actual pitch, advance ratio, blade stall and efficiency need propeller maps. Electrical load is Pshaft/η+Paux; η=0.92 is an assumed **combined motor/inverter/wiring efficiency**, not an advertised peak motor efficiency.

Cells: {p['battery_series']}s{p['battery_parallel']}p, {b['cells']} cells. Nominal {b['nominal_v']:.1f} V, maximum {b['maximum_v']:.1f} V; each of four conceptual modules is 160s4p. Nominal energy uses 18 Wh/cell; minimum-capacity and aging sensitivities still need qualification. Cell mass is {b['cell_mass_kg']:.2f} kg; installed pack mass {b['installed_mass_kg']:.2f} kg includes a {p['pack_noncell_fraction']*100:.2f}% non-cell allowance. This is a functional architecture, not assembly instructions or a production electrical schematic.

Resistance proxy: Rpack=Ns·Rcell/Np, using 12.8 mΩ typical DC resistance. At an assumed minimum **open-circuit** cell voltage of 3.0 V, solve Pload=Voc·I−Rpack·I² using the smaller root. Heat=I²Rpack; chemical power=Pload+heat. This fixed low-OCV approximation is used throughout the mission as a conservative energy screen; it is not a time-resolved SOC/temperature model. Available chemical energy=Enom(0.90−0.20). Mission energy=hover chemical power×3/60 + 3 kWh transition allowance + cruise chemical power×distance/speed. Range=(available−hover−transition)/cruise chemical power×speed. Unlike the original browser explorer, this study explicitly adds a simple battery-resistance loss estimate; the browser defaults were not changed.

The selected worst-voltage hover proxy gives {v['cell_hover_current_a_screen']:.1f} A/cell, {v['battery_hover_terminal_v_screen']:.1f} V loaded bus and **{v['cell_ohmic_heat_kw_screen']:.1f} kW battery heat**. With assumed cell heat capacity 1000 J/(kg K), three minutes without cooling gives {v['adiabatic_cell_rise_k_screen']:.1f} K average rise. This is not a thermal pass: local gradients, cold/aged resistance, connections, containment, ventilation and heat exchanger performance are unresolved. The 12 kg cooling allowance has not been demonstrated adequate.

## Structural screening

Euler-Bernoulli only. Main spar: 120×260 mm hollow rectangular envelope, 4 mm wall, E=70 GPa, density=1600 kg/m³, assumed allowable=250 MPa. For a uniform 3.8g wing load, each semi-span root has M=wL²/2; stress=Mc/I; tip deflection=wL⁴/(8EI). This gives {r['structure']['wing_spar']['stress_pa']/1e6:.1f} MPa and {r['structure']['wing_spar']['tip_deflection_m']*1000:.1f} mm tip deflection. The bare spar mass estimate is {r['structure']['wing_spar']['mass_kg']:.1f} kg. The aerodynamic-system mass allowance must still cover ribs, skins, tail, controls and attachments.

Longitudinal boom screen: 150 mm OD / 4 mm wall, supports at |x|=.85 m, two rotor loads at 1.25 and 3.60 m beyond each support, 2.0× nominal hover thrust. M=ΣFᵢaᵢ and δtip=ΣFᵢaᵢ²(3L−aᵢ)/(6EI). Estimated stress {r['structure']['longitudinal_boom']['stress_pa']/1e6:.1f} MPa, tip deflection {r['structure']['longitudinal_boom']['tip_deflection_m']*1000:.1f} mm. All principal tube lengths give {r['structure']['longitudinal_boom']['all_tube_mass_estimate_kg']:.1f} kg for the principal tubes. Four diagonal braces add about 10.35 kg, and the high-wing rails add about 3.18 kg. The boom-system allowance is 110 kg after assigning 20 kg from growth; the remaining 99 kg growth remains unallocated. Fittings and actual laminates still require a measured mass build-up.

The load factors and allowable are design assumptions, not a certification basis. Composite anisotropy, compression/buckling, joints, motor torque, gyroscopic and tilt loads, crossbeam transfer, aerodynamic balance, vibration, fatigue, flutter, landing and crash loads remain unverified. **No FEA or CFD was run.** OpenFOAM and a verified structural solver were not available in this environment.

## Failure and sensitivity findings

| Scenario | Mass kg | Hover electrical kW | Mission kWh | Energy margin kWh | Loaded hover bus V |
| --- | --- | --- | --- | --- | --- |
{table}

The single-rotor-out allocation proxy solves vertical force, roll/pitch moments and yaw cancellation with an assumed equal torque/thrust ratio. It minimizes maximum rotor thrust, then calculates per-rotor power. **All eight single-rotor-out cases exceed the 30 kW continuous screen** (about 36–42 kW at the most loaded motor). Outer-row failures also require about 219–221 Nm at 1800 rpm, above the published 200 Nm maximum. They are not rescued by quoting the 50 kW peak rating: duration, thermal margin, actual Q/T, transient response and controllability are unverified. A tilt jam, failed bus/module, control-system faults and transition failures are not modeled. The wingless version also needs a dedicated stability/control assessment. Full wing support in the cruise calculation is vertical force balance only; pitch trim, tail lift/downforce, static margin and control authority are not solved.

The +15% mass and reduced-efficiency cases exceed the 20 km energy allocation and fall below the motor's published lower voltage range. A 25% increase in cell resistance alone drops loaded hover voltage to about 395 V, also below 400 V, while increasing battery heat to about 46 kW. These illustrative multipliers are not measured pack aging or cold-temperature characteristics. These sensitivities prevent claiming a robust flight design. The next engineering iteration should address rotor-out/control architecture, rotor maps and thermal closure before any cost optimization is represented as an aircraft optimum.

## Sourcing and cost decision

See `BOM.csv` and `sources/README.md`. The lowest observed listed price does not establish compatibility or lifecycle cost. Candidate motor/inverter/propeller prices require RFQs, so a complete aircraft price or a “cheapest best” parts combination is **not established**.

The cheaper T-MOTOR U15XXL has a $1999 motor listing. Its strongest opened NS62 test row is 101.449 kgf for a short bench condition. Eight give only 811.6 kgf, below the selected {v['mass_kg']:.1f} kg mass even before any thrust reserve. It is rejected for this full-scale concept. Do not extrapolate or transplant its test table to the larger candidate rotor.

The observed P50B bulk tier is $7.50/cell at 1000+, giving **${b['cells']*7.5:,.0f} for {b['cells']} bare cells only**, excluding pack production, BMS, protection, thermal management, screening, tax and shipping. Full selected propulsion and aircraft cost remain unknown. E-PROPS' €1304 two-blade aircraft listing is only a market benchmark, not a quotation for the required CW/CCW rotor set. The $422.99 Holybro Pixhawk 6X set is listed only as an educational subscale/bench option; it is not a human-carrying controller selection and its power module must not be connected to this concept's HV bus.

## CAD interpretation and reproducibility

The assembly contains {component_count} named components with geometrically valid solids at generation. STEP preserves named bodies; FreeCAD imports them as editable solids. The parametric source is Python plus JSON, not a fully constrained native FreeCAD sketch tree. STL is tessellated for GitHub preview; STEP is the precision interchange file. The standalone HTML viewer has no network dependencies. OpenSCAD opens the STL through the supplied wrapper. Blender images use the CAD tessellation, not invented image-generation geometry.

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
'''
 (ROOT/'DESIGN_REPORT.md').write_text(report)
 (ROOT/'README.md').write_text(f'''# E8 aircraft CAD and preliminary design study

**Educational concept — no fabrication or flight release.** A {component_count}-component assembled model for the two-person, eight-motor concept, plus a bounded sizing study and sourced component shortlist. Rotor-out, thermal, structural detail and control design remain open. This is not a proven cheapest or globally optimal aircraft.

![Assembled aircraft concept](images/E8_Assembly_Isometric.png)

## Open the 3D model

- **No installation:** download [E8_3D_Viewer_Offline.html](viewer/E8_3D_Viewer_Offline.html?raw=true), then double-click it. Orbit, zoom, hide the shell, inspect batteries/structure, remove the wing/tail, and tilt the rotors. GitHub shows HTML source until you download it.
- **GitHub 3D preview:** open [winged STL](cad/E8_Winged_Hover.stl) or [wingless STL](cad/E8_Wingless_Hover.stl). GitHub may take time to render or require download on some devices.
- **CAD:** download [FreeCAD assembly](cad/E8_Concept_Assembly.FCStd?raw=true), [winged hover STEP](cad/E8_Winged_Hover.step?raw=true), [winged cruise STEP](cad/E8_Winged_Cruise.step?raw=true), or [wingless STEP](cad/E8_Wingless_Hover.step?raw=true). Units: mm.
- **Everything:** [complete aircraft concept ZIP](https://github.com/Rpirayesh/E8-eVTOL-Design-Explorer/raw/refs/heads/main/downloads/E8_Aircraft_Concept_0_1.zip).

## Study and inspect

| File | Contents |
| --- | --- |
| [Design report](DESIGN_REPORT.md) | Assumptions, equations, limitations, mass, energy, structures and unresolved failures |
| [BOM](BOM.csv) | Candidate parts, quantities, mass allowances, source IDs and quotation gaps |
| [Sources](sources/README.md) | Manufacturer specifications and dated prices; no vendor approvals implied |
| [Selected parameters](selected_design.json) | CAD and sizing inputs chosen from the finite grid |
| [Analysis results](analysis/results.json) | Winged/wingless comparison, sensitivities and static rotor-out proxies |
| [Trade study](analysis/trade_study.csv) | {r['optimization']['candidates']} candidates; {r['optimization']['eligible_winged']} winged candidates pass the listed scalar screens |
| [Independent reviews](reviews/README.md) | Separate numerical, geometry/software and sourcing/engineering reviews |
| [Rebuild scripts](tools) | Reproducible CAD, analysis, viewer and document generation |

Selected study point: {v['mass_kg']:.1f} kg including growth, {p['wing_area_m2']} m² wing, {p['wing_span_m']} m span, {p['rotor_diameter_m']} m rotors, {p['cruise_kph']} km/h. Estimates: {v['hover_electrical_kw']:.1f} kW hover electrical load and {v['energy_based_range_km']:.1f} km energy-based range under the listed assumptions. **All eight single-rotor-out cases exceed the conservative continuous-power screen.** Battery heat rejection and actual rotor performance are unresolved.

Only bare cells have a selected dated bulk price: ${b['cells']*7.5:,.0f}; this is not the aircraft price. Motors, inverters, propellers, airframe and qualification require quotations. The much cheaper drone propulsion shortlist fails the full-scale thrust requirement.

The original [offline performance explorer](../E8_eVTOL_Explorer_Offline.html) remains available with its own defaults and assumptions. This new study adds simple battery-resistance losses and should not be represented as validation of the original illustrative defaults.
''')
 speeds=list(range(80,181,5));fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for winged,label,color in [(True,'Winged','#147d87'),(False,'Wingless','#d67443')]:
  perf=[analyze.performance(p,winged,speed=s) for s in speeds]
  ax[0].plot(speeds,[x['cruise_electrical_kw'] for x in perf],label=label,color=color,lw=2)
  ax[1].plot(speeds,[x['energy_based_range_km'] for x in perf],label=label,color=color,lw=2)
 for a in ax:a.grid(alpha=.2);a.set_xlabel('Speed (km/h)');a.legend(frameon=False)
 ax[0].set_ylabel('Cruise electrical load (kW)');ax[1].set_ylabel('Energy-based range to reserve (km)')
 fig.suptitle('Concept estimates · same hardware; wing/tail mass removed for wingless')
 fig.savefig(ROOT/'images'/'Power_Range_Tradeoffs.png',dpi=170);plt.close(fig)
 print('Wrote report, source ledger, BOM and tradeoff plot')

if __name__=='__main__':main()
