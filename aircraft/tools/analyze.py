"""Reproducible preliminary sizing, bounded trade study and beam screening.

No CFD, FEA, blade-element model, flight control verification or certification.
SI internally; the steady-flight equations follow the repository explorer.
"""
from pathlib import Path
import copy, csv, json, math, itertools
import numpy as np
from scipy.optimize import brentq, linprog

ROOT = Path(__file__).resolve().parents[1]
G = 9.80665

def load():
    return json.loads((ROOT / 'design_parameters.json').read_text())

def battery(p):
    cells = p['battery_series'] * p['battery_parallel']
    cell_mass = cells * p['cell_mass_kg']
    return dict(cells=cells, cell_mass_kg=cell_mass,
                installed_mass_kg=cell_mass*(1+p['pack_noncell_fraction']),
                nominal_kwh=cells*p['cell_ah']*p['cell_v_nominal']/1000,
                nominal_v=p['battery_series']*p['cell_v_nominal'],
                maximum_v=p['battery_series']*p['cell_v_max'],
                screening_minimum_v=p['battery_series']*p['cell_v_screen_min'])

def mass_rows(p, winged=True):
    rows = copy.deepcopy(p['mass_allowances'])
    rows += [dict(item='Eight motors',kg=8*p['motor_mass_each_kg'],x_m=0,z_m=2.36),
             dict(item='Eight inverters',kg=8*p['inverter_mass_each_kg'],x_m=0,z_m=1.0),
             dict(item='Installed battery',kg=battery(p)['installed_mass_kg'],x_m=.55,z_m=-.4),
             dict(item='Two occupants',kg=2*p['person_mass_kg'],x_m=-.6,z_m=.45),
             dict(item='Unallocated growth allowance',kg=p['growth_allowance_kg'],x_m=0,z_m=.3)]
    if winged:
        rows.append(dict(item='Wing, tail and aerodynamic controls',kg=p['wing_system_mass_kg'],x_m=.15,z_m=1.4))
    return rows

def mass_cg(p,winged=True):
    rows=mass_rows(p,winged); mass=sum(x['kg'] for x in rows)
    return mass, sum(x['kg']*x['x_m'] for x in rows)/mass, sum(x['kg']*x['z_m'] for x in rows)/mass

def induced_velocity(t,rho,a,va,vp):
    if t <= 0: return 0.0
    upper=math.sqrt(t/(2*rho*a))
    return brentq(lambda vi: 2*rho*a*vi*math.hypot(vp,va+vi)-t,0,upper,xtol=1e-12)

def hover_shaft_w(p,mass,n=8,rho=None):
    rho = p['rho_kg_m3'] if rho is None else rho
    area=n*math.pi*p['rotor_diameter_m']**2/4
    tip=math.pi*p['rotor_diameter_m']*p['rotor_rpm']/60
    w=mass*G
    return p['kappa']*w*math.sqrt(w/(2*rho*area))+p['rotor_solidity_assumed']*p['blade_cd_assumed']/8*rho*area*tip**3

def battery_load(p,load_kw,voltage):
    """Constant OCV/resistance proxy; lower-current root of P=VI-RI².
    Losses are conservatively evaluated at the screening minimum voltage.
    Cell resistance is a single published typical value, not a pack test.
    """
    resistance=p['battery_series']*p['cell_dc_resistance_ohm']/p['battery_parallel']
    discriminant=voltage**2-4*resistance*load_kw*1000
    if discriminant<=0:
        return dict(current_a=1e9,cell_current_a=1e9,heat_kw=1e9,chemical_kw=1e9,terminal_v=0)
    current=2*load_kw*1000/(voltage+math.sqrt(discriminant))
    heat=current*current*resistance/1000
    return dict(current_a=current,cell_current_a=current/p['battery_parallel'],heat_kw=heat,
                chemical_kw=load_kw+heat,terminal_v=voltage-current*resistance)

def performance(p,winged=True,speed=None,rho=None,mass_override=None):
    mass,cgx,cgz=mass_cg(p,winged)
    if mass_override is not None: mass=mass_override
    rho=p['rho_kg_m3'] if rho is None else rho
    speed=p['cruise_kph'] if speed is None else speed
    v=speed/3.6; w=mass*G; q=.5*rho*v*v
    area=8*math.pi*p['rotor_diameter_m']**2/4
    tip=math.pi*p['rotor_diameter_m']*p['rotor_rpm']/60
    s=p['wing_area_m2']; ar=p['wing_span_m']**2/s
    lift=min(w,q*s*p['cl_max_assumed']/p['stall_speed_factor']**2) if winged else 0
    cl=lift/(q*s) if winged else 0
    drag=q*p['equivalent_flat_plate_m2_assumed']
    if winged: drag+=q*s*(p['wing_cd0_assumed']+cl*cl/(math.pi*p['oswald_assumed']*ar))
    vertical=w-lift; thrust=math.hypot(vertical,drag)
    tilt=math.atan2(drag,vertical); va=v*math.sin(tilt); vp=v*math.cos(tilt)
    vi=induced_velocity(thrust,rho,area,va,vp); mu=vp/tip
    p0=p['rotor_solidity_assumed']*p['blade_cd_assumed']/8*rho*area*tip**3
    shaft=(p['kappa']*thrust*vi+drag*v+p0*(1+3*mu*mu))/1000
    electric=shaft/p['motor_efficiency_assumed']+p['auxiliary_kw']
    hover_shaft=hover_shaft_w(p,mass,rho=rho)/1000
    hover=hover_shaft/p['motor_efficiency_assumed']+p['auxiliary_kw']
    b=battery(p); usable=b['nominal_kwh']*(p['start_soc']-p['reserve_soc'])
    hb=battery_load(p,hover,b['screening_minimum_v']); cb=battery_load(p,electric,b['screening_minimum_v'])
    # Extra transition allowance is chemical energy; phase duration is not simulated.
    fixed=hb['chemical_kw']*p['hover_minutes']/60+p['transition_energy_kwh']
    trip=fixed+cb['chemical_kw']*p['mission_km']/speed
    torque=hover_shaft*1000/8/(2*math.pi*p['rotor_rpm']/60)
    stall=math.sqrt(2*w/(rho*s*p['cl_max_assumed']))*3.6 if winged else None
    return dict(mass_kg=mass,cg_x_m=cgx,cg_z_m=cgz,speed_kph=speed,rho_kg_m3=rho,
        wing_lift_n=lift,weight_n=w,drag_n=drag,thrust_n=thrust,tilt_deg=math.degrees(tilt),
        induced_velocity_m_s=vi,cruise_shaft_kw=shaft,cruise_electrical_kw=electric,
        hover_shaft_kw=hover_shaft,hover_electrical_kw=hover,hover_torque_each_nm=torque,
        hover_thrust_each_n=w/8,tip_m_s=tip,hover_tip_mach=tip/340.3,
        advancing_tip_mach_screen=(tip+v)/340.3,edgewise_mu=mu,stall_kph=stall,
        nominal_kwh=b['nominal_kwh'],usable_kwh=usable,fixed_mission_kwh=fixed,
        trip_kwh=trip,energy_margin_kwh=usable-trip,
        energy_based_range_km=max(0,usable-fixed)/cb['chemical_kw']*speed,
        hover_chemical_kw_screen=hb['chemical_kw'],cruise_chemical_kw_screen=cb['chemical_kw'],
        cell_hover_current_a_screen=hb['cell_current_a'],cell_ohmic_heat_kw_screen=hb['heat_kw'],
        battery_hover_terminal_v_screen=hb['terminal_v'],
        adiabatic_cell_rise_k_screen=hb['heat_kw']*1000*p['hover_minutes']*60/(b['cell_mass_kg']*1000),
        continuous_motor_margin=8*p['motor_continuous_kw_screen']/hover_shaft,
        full_wing_support=lift>=w-1e-6 if winged else False)

def rotor_centres(p):
    return [(x,y,p['rotor_hub_z_m']) for x in p['rotor_rows_x_m'] for y in [-p['rotor_y_m'],p['rotor_y_m']]]

def allocation(p,failed=None):
    """Static proxy: vertical force, roll/pitch and equal Q/T yaw cancellation.
    Minimizes maximum thrust. It is NOT a transient rotor-out/control simulation.
    """
    mass,cgx,_=mass_cg(p); centres=rotor_centres(p)
    signs=[1,-1,-1,1,1,-1,-1,1]
    a=np.array([[1]*8,[x[0] for x in centres],[x[1] for x in centres],signs],float)
    eq=np.column_stack((a,np.zeros(4)))
    ub=np.zeros((8,9)); ub[np.arange(8),np.arange(8)]=1; ub[:,-1]=-1
    bounds=[(0,0) if i==failed else (0,None) for i in range(8)]+[(0,None)]
    r=linprog([0]*8+[1],A_ub=ub,b_ub=np.zeros(8),A_eq=eq,
              b_eq=[mass*G,mass*G*cgx,0,0],bounds=bounds,method='highs')
    if not r.success: return dict(failed_rotor=failed,static_equilibrium=False)
    area=math.pi*p['rotor_diameter_m']**2/4; rho=p['rho_kg_m3']
    tip=math.pi*p['rotor_diameter_m']*p['rotor_rpm']/60
    p0=p['rotor_solidity_assumed']*p['blade_cd_assumed']/8*rho*area*tip**3
    powers=[(p['kappa']*t*math.sqrt(t/(2*rho*area))+p0)/1000 if t>1e-8 else 0 for t in r.x[:8]]
    torques=[power*1000/(2*math.pi*p['rotor_rpm']/60) for power in powers]
    return dict(failed_rotor=failed,static_equilibrium=True,thrusts_n=list(r.x[:8]),
                shaft_powers_kw=powers,max_shaft_kw=max(powers),
                max_torque_nm=max(torques),
                published_max_torque_screen_pass=bool(max(torques)<=p['motor_max_torque_nm_published']),
                published_peak_power_screen_pass=bool(max(powers)<=p['motor_peak_kw_published']),
                continuous_power_screen_pass=bool(max(powers)<=p['motor_continuous_kw_screen']),
                interpretation='Necessary static proxy only; no dynamic controllability or safety claim')

def structural_screen(p):
    mass=mass_cg(p)[0]; b=p['wing_span_m']; E=p['beam_E_pa_assumed']; density=p['beam_density_kg_m3_assumed']
    width=p['wing_spar_width_m']; h=p['wing_spar_height_m']; t=p['wing_spar_wall_m']
    inertia=(width*h**3-(width-2*t)*(h-2*t)**3)/12
    L=b/2; line_load=p['wing_load_factor_assumed']*mass*G/b
    M=line_load*L**2/2; stress=M*h/2/inertia; deflection=line_load*L**4/(8*E*inertia)
    area=width*h-(width-2*t)*(h-2*t)
    d=p['boom_outer_diameter_m']; wall=p['boom_wall_m']; bi=math.pi*(d**4-(d-2*wall)**4)/64
    # Each outboard boom segment carries two concentrated lift loads beyond a support at |x|=.85.
    positions=[abs(x)-.85 for x in p['rotor_rows_x_m'] if x>0]
    f=p['hover_structure_factor_assumed']*mass*G/8; bl=max(positions)
    bm=sum(f*a for a in positions); bs=bm*d/2/bi
    bd=sum(f*a*a*(3*bl-a)/(6*E*bi) for a in positions)
    boom_length=2*(max(p['rotor_rows_x_m'])-min(p['rotor_rows_x_m']))+4*(p['rotor_y_m']-.75)
    boom_mass=math.pi*(d*d-(d-2*wall)**2)/4*boom_length*density
    return dict(wing_spar=dict(root_moment_nm=M,stress_pa=stress,tip_deflection_m=deflection,
            mass_kg=area*b*density,assumed_allowable_margin=p['beam_allowable_pa_assumed']/stress),
        longitudinal_boom=dict(root_moment_nm=bm,stress_pa=bs,tip_deflection_m=bd,
            all_tube_mass_estimate_kg=boom_mass,assumed_allowable_margin=p['beam_allowable_pa_assumed']/bs),
        limitations='Euler-Bernoulli beam screening; homogeneous assumed CFRP properties; no joints, laminate failure, buckling, fatigue, flutter or FEA. Crossbeam load transfer is not solved.')

def sweep(p):
    rows=[]
    for winged,d,s,span,speed,np_ in itertools.product([True,False],[1.6,1.7,1.8,1.9],[12,14,16,18],[9,10,11],[120,130,140,150],[12,16,20]):
        # Wingless duplicate geometry choices are omitted.
        if not winged and (s!=14 or span!=10): continue
        c=copy.deepcopy(p); c.update(rotor_diameter_m=d,wing_area_m2=s,wing_span_m=span,cruise_kph=speed,battery_parallel=np_)
        c['wing_system_mass_kg']=95*(s/14)**.9*(span/10)**.6
        r=performance(c,winged)
        reasons=[]
        if r['continuous_motor_margin']<1.2: reasons.append('less than 20% continuous hover power headroom')
        if r['energy_margin_kwh']<0: reasons.append('mission energy')
        if r['cell_hover_current_a_screen']>c['cell_current_screen_a']: reasons.append('cell current proxy')
        if r['battery_hover_terminal_v_screen']<c['motor_voltage_min_v_published']: reasons.append('loaded voltage below motor published range')
        if battery(c)['maximum_v']>c['inverter_max_dc_v']: reasons.append('inverter maximum voltage')
        if winged and not r['full_wing_support']: reasons.append('stall margin / full wing support')
        if r['cruise_shaft_kw']>8*c['motor_continuous_kw_screen']: reasons.append('cruise motor power')
        if r['edgewise_mu']>.35: reasons.append('edgewise model domain')
        if winged:
            structure=structural_screen(c)
            if structure['wing_spar']['assumed_allowable_margin']<1: reasons.append('wing spar stress proxy')
            if structure['wing_spar']['tip_deflection_m']>span/60: reasons.append('wing spar deflection proxy')
            if c['wing_spar_height_m']>.2*s/span: reasons.append('spar depth / wing envelope')
        rows.append(dict(configuration='winged' if winged else 'wingless',diameter_m=d,wing_area_m2=s if winged else 0,
            span_m=span if winged else 0,cruise_kph=speed,battery_parallel=np_,mass_kg=r['mass_kg'],
            mission_kwh=r['trip_kwh'],range_km=r['energy_based_range_km'],hover_kw=r['hover_electrical_kw'],
            pass_screens=not reasons,reasons='; '.join(reasons)))
    return rows

def main():
    p=load(); out=ROOT/'analysis'; out.mkdir(exist_ok=True)
    rows=sweep(p)
    with (out/'trade_study.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    eligible=[r for r in rows if r['pass_screens'] and r['configuration']=='winged']
    best=min(eligible,key=lambda r:r['mission_kwh'])
    selected=copy.deepcopy(p); selected.update(rotor_diameter_m=best['diameter_m'],wing_area_m2=best['wing_area_m2'],
        wing_span_m=best['span_m'],cruise_kph=best['cruise_kph'],battery_parallel=best['battery_parallel'])
    selected['wing_system_mass_kg']=95*(best['wing_area_m2']/14)**.9*(best['span_m']/10)**.6
    (ROOT/'selected_design.json').write_text(json.dumps(selected,indent=2)+'\n')
    scenarios={}
    for name,c,rho in [('selected',selected,1.225),('thin_air',selected,1.0),('low_density',selected,.9)]:
        scenarios[name]=performance(c,True,rho=rho)
    scenarios['wingless_same_hardware']=performance(selected,False)
    scenarios['mass_plus_15_percent']=performance(selected,mass_override=mass_cg(selected)[0]*1.15)
    degraded=copy.deepcopy(selected);degraded['motor_efficiency_assumed']=.85;degraded['kappa']=1.3
    scenarios['lower_efficiency']=performance(degraded)
    resistant=copy.deepcopy(selected);resistant['cell_dc_resistance_ohm']*=1.25
    scenarios['resistance_plus_25_percent']=performance(resistant)
    results=dict(status='Concept estimates; numerical verification is not physical validation',
        optimization=dict(objective='Minimum 20 km mission energy among enumerated winged candidates passing the listed scalar screens',
            global_optimum=False,candidates=len(rows),eligible_winged=len(eligible),selected=best,
            omitted='Part quotes, manufacturing cost, aeroelasticity, full transition, robust control, thermal rejection and supplier matching are not optimization constraints'),
        battery=battery(selected),scenarios=scenarios,mass_rows=mass_rows(selected),
        structure=structural_screen(selected),static_allocations=[allocation(selected,i) for i in [None]+list(range(8))])
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    with (out/'mass_budget.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['item','kg','x_m','z_m']);writer.writeheader();writer.writerows(mass_rows(selected))
    print(json.dumps(dict(optimization=results['optimization'],selected=scenarios['selected'],structure=results['structure']),indent=2))

if __name__=='__main__': main()
