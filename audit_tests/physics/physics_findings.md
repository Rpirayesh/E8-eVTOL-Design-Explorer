# Independent physics review of the delivered E8 offline explorer

## Finding

No algebraic or dimensional error was found in the declared low-fidelity model. The mass budget, wing lift and induced drag, horizontal/vertical force balance, positive oblique-inflow root, useful/induced/profile power split, electrical conversion, and nominal-pack energy accounting are internally consistent. Five independent Python spot checks agree with the delivered JavaScript to floating-point precision. This is **numerical verification of the stated equations**, not validation against a real aircraft or rotor test data.

The main issue is the breadth of the permitted design space relative to the model's fidelity. Its screens exclude some power/energy/advance-ratio failures, but do not test blade loading, rotor stall, compressibility, achievable trim, transition/control, or structural/thermal feasibility. The original app does disclose those omissions. It should make them prominent beside the results, because extreme combinations can clear all existing screens.

## Recommended minimal hardening

Keep the numerical model unchanged and use **Energy-based range** rather than **Estimated range**. Place this sentence beside the operating-point status:

> Passing these power and energy screens does not verify blade loading, rotor stall, compressibility, transition, stability or control. Range is an energy-based estimate under the stated assumptions.

Add hover and cruise blade-loading diagnostics to Validation:

\[
A=8\pi d^2/4,\qquad
C_{T,h}/\sigma=\frac{W}{\rho A U_{tip}^2\sigma},\qquad
C_{T,c}/\sigma=\frac{T}{\rho A U_{tip}^2\sigma}.
\]

Because all eight identical rotors share load, using total thrust and total disk area gives the same coefficient as per-rotor quantities. For a rough uniform-chord diagnostic, \(\bar c_\ell\approx6C_T/\sigma\). This is not the local maximum section lift coefficient and is not a pass/fail stall prediction. Do not invent a universal cutoff: a usable bound needs actual blade geometry, airfoil data, pitch/RPM limits and operating-condition evidence.

Suggested diagnostic caveat:

> CT/σ describes blade loading only. No blade-stall or compressibility limit is applied; an acceptable value requires rotor-specific aerodynamic data.

The μ ≤ 0.35 condition is a chosen model screen, not an aircraft flight-envelope limit. Keep that distinction in the displayed explanation. Also state that zero hover/transition allowances intentionally remove those mission-energy costs; they do not predict a zero-energy VTOL transition.

## Independent examples

All rows use the published defaults except the explicit changes. Power is electrical. Range includes the selected reserve and the entered hover/transition allowances.

| Case | Overrides | Cruise kW | Hover kW | Energy-based range km | Hover CT/σ |
|---|---|---:|---:|---:|---:|
| Default winged, 760 kg | None | 55.469303 | 130.865741 | 46.204602 | 0.129266 |
| Default wingless, 700 kg | Wingless | 69.888334 | 117.649167 | 37.428326 | 0.119061 |
| Low-speed winged rotor assistance | speed = 40 km/h | 95.163503 | 130.865741 | 8.977311 | 0.129266 |
| Full-wing-support axial propulsion | speed = 200 km/h | 131.363718 | 130.865741 | 32.517059 | 0.129266 |
| High-loading counterexample | Wingless; details below | 79.636174 | 81.130259 | 14.389355 | 1.382491 |

The counterexample uses speed = 20, emptyMass = 150, personMass = 50, batteryMass = 150, diameter = 0.8, wingMass = 0, tipSpeed = 120, solidity = 0.04, bladeCd = 0.006, kappa = 1, motorEfficiency = 0.98, motorPower = 80, specificEnergy = 400, soc = 100, reserve = 0, maxC = 12, transitionEnergy = 0 and tripDistance = 5, in the app's displayed units. Other inputs remain default. Gross mass is 400 kg. It clears the existing power/energy/μ screens and the 5 km trip budget, but its rough hover mean blade CL is 8.294945. The model cannot substantiate aerodynamic feasibility at this loading. The point demonstrates an unchecked physical constraint, not a failure of the implemented arithmetic.

`independent_examples.py` does not import the app. It uses algebraic force projections and a Newton root; the full-wing-support case uses the analytical axial root. `independent_examples.json` contains all parameter changes, intermediate forces, root residuals and final numbers. Maximum displayed spot-check momentum residual is about 9.1e-13 N.

## Axial-profile sensitivity, not a required arithmetic correction

The app deliberately uses \(P_0=P_{0,h}(1+3\mu^2)\), constant blade Cd and constant tip speed. Its omission of axial-flow profile correction is already disclosed. A more complete profile model changes the estimate even when the implementation is flawless.

For the default winged case at 200 km/h, full wing support makes μ ≈ 0 and axial speed ratio a = V/Utip = 0.326797. The NDARC profile integral reduces in pure axial flow to

\[
F_{P,ax}=\tfrac12\sqrt{1+a^2}(2+5a^2)+\tfrac32a^4\operatorname{asinh}(1/a),\qquad F_{P,ax}(0)=1.
\]

It gives 1.364363 instead of the app's factor 1. Holding every other assumption fixed, replacing only this profile factor would move electrical cruise power from 131.363718 to 137.186562 kW and energy-based range from 32.517059 to 31.136881 km. That is a single-term sensitivity, **not** a validated corrected range: interference, loading-dependent Cd, geometry, control and transition remain unresolved. It is a good example of why matching numerical benchmarks does not establish real-aircraft accuracy.

## Primary references and precise locations

1. NASA Glenn, **Lift Equation**, equation and experimental-coefficient discussion: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation-2/ . 
2. NASA Glenn, **Induced Drag Coefficient**, \(C_{Di}=C_L^2/(\pi eAR)\), reference-area convention and \(AR=b^2/S\): https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/ . 
3. Wayne Johnson, **NDARC Theory, Appendix 3, Release 1.7**, NASA TP 2009-215402 (December 2012), §11-4.1 printed pp. 94–95 (PDF pp. 99–100): Glauert ideal inflow; §11-5 printed pp. 104–105 (PDF pp. 109–110): power split and profile factor; §11-5.1.2 printed pp. 106–108 (PDF pp. 111–113): loading-dependent blade drag, stall and compressibility. https://rotorcraft.arc.nasa.gov/Publications/files/NASA%20TP-2009-215402-app3.pdf . 

The NDARC references support the underlying relations and explain omitted physics. The E8 explorer is not NDARC, and this review does not transfer NDARC validation to the explorer.
