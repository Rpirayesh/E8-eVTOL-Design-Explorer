"""Independent physics spot checks. No import or evaluation of the app code."""
import math, json
from pathlib import Path

BASE = dict(speed=120., emptyMass=330., personMass=95., batteryMass=180., diameter=1.8,
            wingMass=60., wingArea=10., aspectRatio=7., oswald=.8, clMax=1.5,
            stallMargin=1.2, wingCd0=.025, flatPlate=.65, rho=1.225, tipSpeed=170.,
            solidity=.08, bladeCd=.012, kappa=1.15, motorEfficiency=.92, motorPower=25.,
            auxPower=1., specificEnergy=220., soc=90., reserve=20., maxC=5.,
            hoverMinutes=2., transitionEnergy=2., tripDistance=40.)

def spot(name, wing, changes):
    p = BASE | changes
    m = p['emptyMass'] + 2*p['personMass'] + p['batteryMass'] + (p['wingMass'] if wing else 0)
    W, A, V = m*9.80665, 2*math.pi*p['diameter']**2, p['speed']/3.6
    q = p['rho']*V**2/2
    L = min(W, q*p['wingArea']*p['clMax']/p['stallMargin']**2) if wing else 0.
    D = q*p['flatPlate']
    if wing:
        D += q*p['wingArea']*p['wingCd0'] + L**2/(q*p['wingArea']*math.pi*p['oswald']*p['aspectRatio'])
    Z = W-L
    T = math.sqrt(Z*Z+D*D)
    Va, Vp = V*D/T, V*Z/T  # algebraic projections, rather than trigonometric projections
    vh = math.sqrt(W/(2*p['rho']*A))
    if Z == 0:
        vi = 2*T/(2*p['rho']*A)/(V+math.sqrt(V*V+2*T/(p['rho']*A)))  # stable analytical axial root
        method = 'analytical axial root'
    else:
        vi = math.sqrt(T/(2*p['rho']*A))
        for _ in range(100):
            u = math.sqrt(Vp*Vp+(Va+vi)**2)
            f = 2*p['rho']*A*vi*u-T
            derivative = 2*p['rho']*A*(u+vi*(Va+vi)/u)
            step = f/derivative
            vi -= step
            if abs(step) < 1e-13:
                break
        method = 'Newton root using algebraic inflow projections'
    residual = 2*p['rho']*A*vi*math.hypot(Vp,Va+vi)-T
    p0 = p['rho']*A*p['tipSpeed']**3*p['solidity']*p['bladeCd']/8
    profile = p0*(1+3*(Vp/p['tipSpeed'])**2)
    shaft = (D*V+p['kappa']*T*vi+profile)/1000
    elec = shaft/p['motorEfficiency']+p['auxPower']
    hover_shaft = (p['kappa']*W*vh+p0)/1000
    hover = hover_shaft/p['motorEfficiency']+p['auxPower']
    nominal = p['batteryMass']*p['specificEnergy']/1000
    available = nominal*(p['soc']-p['reserve'])/100
    fixed = hover*p['hoverMinutes']/60+p['transitionEnergy']
    range_km = max(0.,available-fixed)/elec*p['speed']
    power_screen = max(shaft,hover_shaft)<=8*p['motorPower'] and max(elec,hover)<=nominal*p['maxC']
    ct_sigma_hover = W/(p['rho']*A*p['tipSpeed']**2*p['solidity'])
    return dict(name=name, winged=wing, overrides=changes, root_method=method, mass_kg=m,
                wing_lift_N=L, rotor_vertical_N=Z, drag_N=D, rotor_thrust_N=T,
                vi_m_s=vi, momentum_residual_N=residual,
                cruise_electrical_kW=elec, hover_electrical_kW=hover, range_km=range_km,
                trip_margin_kWh=available-fixed-elec*p['tripDistance']/p['speed'],
                power_screen_pass=power_screen, hover_ct_sigma=ct_sigma_hover,
                cruise_ct_sigma=T/(p['rho']*A*p['tipSpeed']**2*p['solidity']),
                approximate_hover_mean_blade_cl=6*ct_sigma_hover)

CASES = [
    ('Default winged at 120 km/h', True, {}),
    ('Default wingless at 120 km/h', False, {}),
    ('Winged rotor assistance at 40 km/h', True, {'speed':40.}),
    ('Winged axial propulsion at 200 km/h', True, {'speed':200.}),
    ('High blade loading that still clears current screens', False,
     dict(speed=20.,emptyMass=150.,personMass=50.,batteryMass=150.,diameter=.8,wingMass=0.,
          tipSpeed=120.,solidity=.04,bladeCd=.006,kappa=1.,motorEfficiency=.98,
          motorPower=80.,specificEnergy=400.,soc=100.,reserve=0.,maxC=12.,transitionEnergy=0.,tripDistance=5.))
]
rows = [spot(*c) for c in CASES]
a = (200/3.6)/170
fp_axial = .5*math.sqrt(1+a*a)*(2+5*a*a)+1.5*a**4*math.asinh(1/a)
p0 = 1.225*(2*math.pi*1.8**2)*170**3*.08*.012/8/1000
high = rows[3]
corrected_power = high['cruise_electrical_kW'] + p0*(fp_axial-1)/.92
cruise_energy = 27.72-high['hover_electrical_kW']*2/60-2
out = dict(method='Independent Python spot calculations; no app-code import. These verify arithmetic of the declared model, not real-aircraft accuracy.',
           cases=rows,
           axial_profile_sensitivity=dict(speed_kmh=200.,axial_ratio=a,
             old_profile_factor=1.,ndarc_axial_profile_factor=fp_axial,
             old_electrical_kW=high['cruise_electrical_kW'],profile_only_alternative_electrical_kW=corrected_power,
             old_range_km=high['range_km'],profile_only_alternative_range_km=cruise_energy/corrected_power*200,
             caveat='Sensitivity to a single omitted term. Other assumptions held fixed; this is not a validated performance correction.'))
path = Path(__file__).with_name('independent_examples.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
