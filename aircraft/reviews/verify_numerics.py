"""Independent equation verification; does not validate aircraft physics.
Run from any directory: python aircraft/reviews/verify_numerics.py
Expected values are implemented here, not imported from tools/analyze.py.
The production module is imported only to obtain actual outputs for comparison.
"""
from pathlib import Path
import math, json, copy, itertools, importlib.util, hashlib
import numpy as np
from scipy.optimize import root_scalar, linprog
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'selected_design.json').read_text())
spec=importlib.util.spec_from_file_location('production',ROOT/'tools'/'analyze.py')
production=importlib.util.module_from_spec(spec);spec.loader.exec_module(production)
G=9.80665

def independent(c,winged=True,speed=None,rho=None, mass_override=None):
    n=c['rotor_count'];rho=c['rho_kg_m3'] if rho is None else rho
    velocity=(c['cruise_kph'] if speed is None else speed)/3.6
    nc=c['battery_series']*c['battery_parallel'];mc=nc*c['cell_mass_kg']
    mp=mc*(1+c['pack_noncell_fraction']);energy=nc*c['cell_ah']*c['cell_v_nominal']/1000
    # Explicit independent list of masses and positions.
    rows=[(v['kg'],v['x_m'],v['z_m']) for v in c['mass_allowances']]
    rows += [(n*c['motor_mass_each_kg'],0,2.36),(n*c['inverter_mass_each_kg'],0,1),
             (mp,.55,-.4),(2*c['person_mass_kg'],-.6,.45),(c['growth_allowance_kg'],0,.3)]
    if winged:rows += [(c['wing_system_mass_kg'],.15,1.4)]
    m=sum(v[0] for v in rows);cgx=sum(v[0]*v[1] for v in rows)/m;cgz=sum(v[0]*v[2] for v in rows)/m
    if mass_override is not None:m=mass_override
    w=m*G;area=n*math.pi*(c['rotor_diameter_m']/2)**2
    q=rho*velocity**2/2;S=c['wing_area_m2'];aspect=c['wing_span_m']**2/S
    lift=min(q*S*c['cl_max_assumed']/c['stall_speed_factor']**2,w) if winged else 0
    drag=q*c['equivalent_flat_plate_m2_assumed']
    if winged:drag += q*S*c['wing_cd0_assumed']+lift**2/(q*S*math.pi*c['oswald_assumed']*aspect)
    tz=w-lift;T=math.hypot(tz,drag)
    # Direct direction cosine projection instead of atan/trig.
    va=velocity*drag/T;vp=velocity*tz/T
    vh=math.sqrt(T/(2*rho*area))
    if vp<1e-10:
        vi=(math.sqrt(va*va+4*vh*vh)-va)/2 # Closed-form purely axial momentum result.
    else:
        vi=root_scalar(lambda x:2*rho*area*x*math.sqrt(vp*vp+(va+x)**2)-T,
                       bracket=[0,vh],method='toms748',xtol=1e-11).root
    u=c['rotor_rpm']*2*math.pi/60*c['rotor_diameter_m']/2
    p0=c['rotor_solidity_assumed']*c['blade_cd_assumed']*rho*area*u**3/8
    shaft=(c['kappa']*T*vi+drag*velocity+p0*(1+3*(vp/u)**2))/1000
    hshaft=(c['kappa']*w**1.5/math.sqrt(2*rho*area)+p0)/1000
    load=shaft/c['motor_efficiency_assumed']+c['auxiliary_kw']
    hload=hshaft/c['motor_efficiency_assumed']+c['auxiliary_kw']
    R=c['battery_series']*c['cell_dc_resistance_ohm']/c['battery_parallel'];V=c['battery_series']*c['cell_v_screen_min']
    def loss(P):
        if V*V<4*R*P*1000:return dict(i=1e9,cell_i=1e9,heat=1e9,chem=1e9,vt=0)
        # Find the physical lower-current root by a different numerical method.
        i=root_scalar(lambda i:V*i-R*i*i-P*1000,bracket=[0,V/(2*R)],method='brentq',xtol=1e-10).root
        return dict(i=i,cell_i=i/c['battery_parallel'],heat=R*i*i/1000,chem=V*i/1000,vt=V-R*i)
    h=loss(hload);cr=loss(load);usable=energy*(c['start_soc']-c['reserve_soc'])
    fixed=h['chem']*c['hover_minutes']/60+c['transition_energy_kwh']
    trip=fixed+cr['chem']*c['mission_km']/(velocity*3.6)
    stall=math.sqrt(2*w/(rho*S*c['cl_max_assumed']))*3.6 if winged else None
    return dict(mass_kg=m,cg_x_m=cgx,cg_z_m=cgz,wing_lift_n=lift,weight_n=w,drag_n=drag,
        thrust_n=T,induced_velocity_m_s=vi,cruise_shaft_kw=shaft,cruise_electrical_kw=load,
        hover_shaft_kw=hshaft,hover_electrical_kw=hload,hover_torque_each_nm=hshaft*1000/n/(c['rotor_rpm']*2*math.pi/60),
        nominal_kwh=energy,usable_kwh=usable,fixed_mission_kwh=fixed,trip_kwh=trip,energy_margin_kwh=usable-trip,
        energy_based_range_km=max(0,usable-fixed)/cr['chem']*velocity*3.6,cell_hover_current_a_screen=h['cell_i'],
        cell_ohmic_heat_kw_screen=h['heat'],battery_hover_terminal_v_screen=h['vt'],
        hover_chemical_kw_screen=h['chem'],cruise_chemical_kw_screen=cr['chem'],stall_kph=stall,
        continuous_motor_margin=n*c['motor_continuous_kw_screen']/hshaft,
        full_wing_support=bool(lift>=w-1e-6) if winged else False)

comparisons=0;max_relative=0;max_absolute=0;failures=[];examples={}
def compare(name, expected, actual):
    global comparisons,max_relative,max_absolute
    for k,e in expected.items():
        a=actual[k]
        if isinstance(e,bool) or e is None:
            if e!=a:failures.append(dict(case=name,key=k,expected=e,actual=a))
            continue
        comparisons+=1;absolute=abs(e-a);relative=absolute/max(1,abs(e));max_relative=max(max_relative,relative);max_absolute=max(max_absolute,absolute)
        if not math.isfinite(a) or relative>2e-8:failures.append(dict(case=name,key=k,expected=e,actual=a))

# Named scenarios (full loss/mass/force checks).
results=json.loads((ROOT/'analysis'/'results.json').read_text())
for name in results['scenarios']:
    c=copy.deepcopy(p);kwargs={};winged=True
    if name=='thin_air':kwargs['rho']=1
    if name=='low_density':kwargs['rho']=.9
    if name=='wingless_same_hardware':winged=False
    if name=='mass_plus_15_percent':kwargs['mass_override']=independent(p)['mass_kg']*1.15
    if name=='lower_efficiency':c['motor_efficiency_assumed']=.85;c['kappa']=1.3
    if name=='resistance_plus_25_percent':c['cell_dc_resistance_ohm']*=1.25
    expected=independent(c,winged,**kwargs);compare(name,expected,results['scenarios'][name]);examples[name]=expected

# Independent reproduction of entire finite grid including all screening decisions.
base=json.loads((ROOT/'design_parameters.json').read_text());grid=[]
for winged,d,S,span,speed,np_ in itertools.product([True,False],[1.6,1.7,1.8,1.9],[12,14,16,18],[9,10,11],[120,130,140,150],[12,16,20]):
    if not winged and (S!=14 or span!=10):continue
    c=copy.deepcopy(base);c.update(rotor_diameter_m=d,wing_area_m2=S,wing_span_m=span,cruise_kph=speed,battery_parallel=np_)
    c['wing_system_mass_kg']=95*(S/14)**.9*(span/10)**.6
    e=independent(c,winged);a=production.performance(c,winged);compare('grid',e,a)
    width,h,t=c['wing_spar_width_m'],c['wing_spar_height_m'],c['wing_spar_wall_m'];I=(width*h**3-(width-2*t)*(h-2*t)**3)/12
    line=c['wing_load_factor_assumed']*e['mass_kg']*G/span;L=span/2
    stress=line*L*L/2*h/2/I;defl=line*L**4/(8*c['beam_E_pa_assumed']*I)
    passes=(e['continuous_motor_margin']>=1.2 and e['energy_margin_kwh']>=0 and e['cell_hover_current_a_screen']<=c['cell_current_screen_a'] and
      e['battery_hover_terminal_v_screen']>=c['motor_voltage_min_v_published'] and c['battery_series']*c['cell_v_max']<=c['inverter_max_dc_v'] and
      (not winged or e['full_wing_support']) and e['cruise_shaft_kw']<=8*c['motor_continuous_kw_screen'] and a['edgewise_mu']<=.35 and
      (not winged or (stress<=c['beam_allowable_pa_assumed'] and defl<=span/60 and h<=.2*S/span)))
    grid.append(dict(configuration='winged' if winged else 'wingless',d=d,S=S,span=span,speed=speed,np=np_,passes=passes,energy=e['trip_kwh']))
selected=min([g for g in grid if g['configuration']=='winged' and g['passes']],key=lambda g:g['energy'])
if (selected['d'],selected['S'],selected['span'],selected['speed'],selected['np'])!=(p['rotor_diameter_m'],p['wing_area_m2'],p['wing_span_m'],p['cruise_kph'],p['battery_parallel']):failures.append({'selection_mismatch':selected})

# Separate adverse operating-point stress grid. No inference of physical accuracy.
stress_count=0
for winged,rho,speed,d,mult,r_factor in itertools.product([True,False],[.7,.9,1.225,1.3],[20,80,140,220],[1.6,1.9],[.8,1,1.3],[.75,1,1.25]):
    c=copy.deepcopy(p);c['rotor_diameter_m']=d;c['cell_dc_resistance_ohm']*=r_factor
    mass=independent(c,winged)['mass_kg']*mult
    e=independent(c,winged,speed=speed,rho=rho,mass_override=mass)
    a=production.performance(c,winged,speed=speed,rho=rho,mass_override=mass)
    compare('adverse',e,a);stress_count+=1

# Independent beam checks including an explicit sum over tip point-load compliance.
M=examples['selected']['mass_kg'];b=p['wing_span_m'];L=b/2;w=p['wing_load_factor_assumed']*M*G/b
width,h,t=p['wing_spar_width_m'],p['wing_spar_height_m'],p['wing_spar_wall_m'];I=(width*h**3-(width-2*t)*(h-2*t)**3)/12
wing=dict(root_moment_nm=w*L*L/2,stress_pa=w*L*L*h/(4*I),tip_deflection_m=w*L**4/(8*p['beam_E_pa_assumed']*I),mass_kg=(width*h-(width-2*t)*(h-2*t))*b*p['beam_density_kg_m3_assumed'])
compare('wing beam',wing,results['structure']['wing_spar'])
d=p['boom_outer_diameter_m'];t=p['boom_wall_m'];I=math.pi*(d**4-(d-2*t)**4)/64;positions=[1.25,3.6];F=p['hover_structure_factor_assumed']*M*G/8
bm=F*sum(positions);bd=sum(F*a*a*(3*3.6-a)/(6*p['beam_E_pa_assumed']*I) for a in positions)
compare('boom beam',dict(root_moment_nm=bm,stress_pa=bm*d/2/I,tip_deflection_m=bd),results['structure']['longitudinal_boom'])

# Verify all returned allocations and independently minimize the feasible thrust cap.
xy=np.array([(x,y) for x in p['rotor_rows_x_m'] for y in [-p['rotor_y_m'],p['rotor_y_m']]])
signs=np.array([1,-1,-1,1,1,-1,-1,1]);A=np.vstack([np.ones(8),xy[:,0],xy[:,1],signs]);B=np.array([M*G,M*G*examples['selected']['cg_x_m'],0,0])
alloc=[]
for row in results['static_allocations']:
    f=row['failed_rotor'];T=np.array(row['thrusts_n']);residual=np.max(np.abs(A@T-B));
    if residual>1e-6 or T.min()<-1e-6:failures.append(dict(allocation=f,residual=float(residual)))
    if f is not None and abs(T[f])>1e-6:failures.append(dict(failed_rotor_nonzero=f))
    lo=0;hi=M*G
    for _ in range(55):
        mid=(lo+hi)/2;bounds=[(0,0) if i==f else (0,mid) for i in range(8)]
        feasible=linprog(np.zeros(8),A_eq=A,b_eq=B,bounds=bounds,method='highs').success
        if feasible:hi=mid
        else:lo=mid
    cap=float(max(T));
    if abs(cap-hi)>2e-4:failures.append(dict(allocation_optimum=f,returned=cap,independent=hi))
    Ar=math.pi*(p['rotor_diameter_m']/2)**2;tip=p['rotor_rpm']*math.pi*p['rotor_diameter_m']/60;rho=p['rho_kg_m3'];p0=p['rotor_solidity_assumed']*p['blade_cd_assumed']/8*rho*Ar*tip**3
    powers=[(p['kappa']*v**1.5/math.sqrt(2*rho*Ar)+p0)/1000 if v>1e-8 else 0 for v in T]
    torque=max(powers)*1000/(p['rotor_rpm']*2*math.pi/60)
    compare('allocation power',dict(max_shaft_kw=max(powers),max_torque_nm=torque),row)
    alloc.append(dict(failed_rotor=f,max_thrust_n=cap,independent_cap_n=hi,residual=float(residual),max_shaft_kw=max(powers),max_torque_nm=torque))

report=dict(scope='Independent numerical implementation of the disclosed concept equations; no physical validation',
    grid_cases=len(grid),eligible_winged=sum(g['passes'] and g['configuration']=='winged' for g in grid),adverse_cases=stress_count,named_scenarios=len(examples),
    numeric_comparisons=comparisons,max_relative_error=max_relative,max_absolute_error=max_absolute,failures=failures,selected=selected,
    examples=examples,wing_beam=wing,static_allocations=alloc,
    input_sha256=hashlib.sha256((ROOT/'selected_design.json').read_bytes()).hexdigest(),
    implementation_sha256=hashlib.sha256((ROOT/'tools'/'analyze.py').read_bytes()).hexdigest())
(ROOT/'reviews'/'numerical_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['examples','static_allocations']},indent=2))
if failures:raise SystemExit(1)
