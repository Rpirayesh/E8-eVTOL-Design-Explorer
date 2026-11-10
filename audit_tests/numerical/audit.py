"""Independent numerical review of the exact delivered E8 model.

Python uses algebraic force projection, lift-squared induced drag, dimensionless
Brent inflow roots, and a second Brent root for power-only hover capacity.
The original JavaScript uses trigonometry and fixed-count bisection.
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess
import numpy as np
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--model',default=str(HERE.parent/'original/model-extracted.cjs'));parser.add_argument('--random',type=int,default=20000);parser.add_argument('--prefix',default='');args=parser.parse_args()
MODEL=Path(args.model)
def js(req):
    r=subprocess.run(['node',str(HERE/'run_model.cjs'),str(MODEL)],input=json.dumps(req),text=True,capture_output=True,check=True)
    return json.loads(r.stdout)
metadata=js({'metadata':True});D=metadata['defaults'];LIMITS=metadata['limits']

def independent(changes,winged):
    p=dict(D,**changes)
    mass=p['emptyMass']+2*p['personMass']+p['batteryMass']+(p['wingMass'] if winged else 0)
    W=mass*9.80665; A=8*math.pi*(p['diameter']/2)**2; V=p['speed']/3.6; q=p['rho']*V*V/2
    L=min(W,q*p['wingArea']*p['clMax']/(p['stallMargin']*p['stallMargin'])) if winged else 0
    drag=q*p['flatPlate']
    if winged: drag+=q*p['wingArea']*p['wingCd0']+L*L/(q*p['wingArea']*math.pi*p['oswald']*p['aspectRatio'])
    z=W-L;T=math.sqrt(z*z+drag*drag);Va=V*drag/T;Vp=V*z/T
    vh=math.sqrt(T/(2*p['rho']*A));va=Va/vh;vp=Vp/vh
    u=brentq(lambda u:u*math.sqrt(vp*vp+(va+u)**2)-1,0,1,xtol=1e-14,rtol=1e-14)
    vi=u*vh;mu=Vp/p['tipSpeed']
    P0=p['solidity']*p['bladeCd']/8*p['rho']*A*p['tipSpeed']**3
    Pshaft=(drag*V+p['kappa']*T*vi+P0*(1+3*mu*mu))/1000
    Pe=Pshaft/p['motorEfficiency']+p['auxPower']
    Phs=(p['kappa']*W**1.5/math.sqrt(2*p['rho']*A)+P0)/1000
    Ph=Phs/p['motorEfficiency']+p['auxPower']
    En=p['batteryMass']*p['specificEnergy']/1000;Eavail=En*(p['soc']-p['reserve'])/100
    Ehover=Ph*p['hoverMinutes']/60;Efixed=Ehover+p['transitionEnergy'];Ec=max(0,Eavail-Efixed)
    R=Ec/Pe*p['speed'];Plim=8*p['motorPower'];Pbatt=En*p['maxC']
    limit=max(0,min(Plim,(Pbatt-p['auxPower'])*p['motorEfficiency']))*1000
    if limit<=P0:Tmax=0
    else:
        f=lambda t:p['kappa']*t**1.5/math.sqrt(2*p['rho']*A)+P0-limit
        hi=1
        while f(hi)<0: hi*=2
        Tmax=brentq(f,0,hi,xtol=1e-8,rtol=1e-13)
    power_ok=Phs<=Plim+1e-8 and Pshaft<=Plim+1e-8 and Ph<=Pbatt+1e-8 and Pe<=Pbatt+1e-8
    feasible=power_ok and mu<=.35 and Eavail>Efixed
    return dict(mass=mass,weight=W,area=A,q=q,wingLift=L,vertical=z,drag=drag,thrust=T,vi=vi,mu=mu,shaft=Pshaft,electrical=Pe,hoverShaft=Phs,hoverPower=Ph,nominalEnergy=En,usableEnergy=Eavail,hoverEnergy=Ehover,fixedEnergy=Efixed,cruiseEnergy=Ec,rawRange=R,maxHoverThrust=Tmax,powerOk=power_ok,feasible=feasible,tripEnergy=Efixed+Pe*p['tripDistance']/p['speed'],tripMargin=Eavail-Efixed-Pe*p['tripDistance']/p['speed'])

named=[
 ('Default winged',{},True),('Default wingless',{},False),
 ('Low-speed wing assist',{'speed':40},True),('Full wing support',{'speed':160},True),
 ('Thin air',{'rho':.7,'speed':120},True),
 ('Heavy battery',{'batteryMass':500,'diameter':2.5,'motorPower':60,'maxC':8,'speed':140},True),
 ('Battery power failure',{'maxC':1},True),('Shaft power failure',{'motorPower':5},False),
 ('Energy exhaustion',{'batteryMass':20,'hoverMinutes':10,'transitionEnergy':10},True),
 ('Tight reserve',{'soc':61,'reserve':60,'hoverMinutes':0,'transitionEnergy':0},True),
 ('Very small rotors',{'diameter':.8,'rho':.7},False),
 ('High-speed wingless model limit',{'tipSpeed':120,'speed':220,'motorPower':80,'maxC':12},False),
 ('Large disks heavy lift',{'emptyMass':1000,'personMass':150,'batteryMass':600,'diameter':3,'wingArea':2,'rho':.7,'tipSpeed':120,'solidity':.04,'bladeCd':.006,'motorPower':80,'specificEnergy':400,'maxC':12,'kappa':1,'hoverMinutes':0,'transitionEnergy':0},False),
]
cases=[dict(name=name,inputs=p,winged=w,kind='named') for name,p,w in named]
for key,(lo,hi) in LIMITS.items():
    for value in (lo,(lo+hi)/2,hi):
        p={key:value}
        if dict(D,**p)['soc']<=dict(D,**p)['reserve']: continue
        for w in (False,True): cases.append(dict(name=f'{key}={value}:winged={w}',inputs=p,winged=w,kind='one-factor-boundary'))
# Orthogonal extremes for the variables most strongly governing induced hover demand.
for mass in [150,1000]:
 for batt in [20,600]:
  for dia in [.8,3]:
   for rho in [.7,1.3]:
    for speed in [20,220]:
     for w in [False,True]:cases.append(dict(name='extreme corner',inputs=dict(emptyMass=mass,batteryMass=batt,diameter=dia,rho=rho,speed=speed),winged=w,kind='corner'))
rng=np.random.default_rng(20261110)
keys=list(LIMITS)
for i in range(args.random):
    p={k:float(rng.uniform(*LIMITS[k])) for k in keys}
    if p['reserve']>=p['soc']:p['reserve']=float(rng.uniform(0,p['soc']))
    cases.append(dict(name=f'random_{i}',inputs=p,winged=bool(i%2),kind='random'))
results=js({'cases':cases})
fields=['mass','weight','area','q','wingLift','vertical','drag','thrust','vi','mu','shaft','electrical','hoverShaft','hoverPower','nominalEnergy','usableEnergy','hoverEnergy','fixedEnergy','cruiseEnergy','rawRange','maxHoverThrust','tripEnergy','tripMargin']
max_error={k:0.0 for k in fields};failures=[];examples=[];feasible=0;screened=0;trip_boundary=[]
for i,(case,r) in enumerate(zip(cases,results)):
    if 'error' in r:failures.append(dict(index=i,case=case,error=r));continue
    ref=independent(case['inputs'],case['winged']);p=dict(D,**case['inputs'])
    for key in fields:
        err=abs(r[key]-ref[key])/max(1,abs(ref[key]));max_error[key]=max(max_error[key],err)
        if not math.isfinite(r[key]) or err>1e-8: failures.append(dict(index=i,case=case,field=key,actual=r[key],expected=ref[key],relative_scaled_error=err))
    for key in ['powerOk','feasible']:
        if r[key]!=ref[key]:failures.append(dict(index=i,case=case,field=key,actual=r[key],expected=ref[key]))
    if r['feasible']:feasible+=1
    else:screened+=1
    # Conservation and bounds, independent of agreement with Python implementation.
    invariant={
     'vertical_force':abs(r['wingLift']+r['thrust']*math.cos(r['tilt'])-r['weight'])/r['weight'],
     'horizontal_force':abs(r['thrust']*math.sin(r['tilt'])-r['drag'])/max(1,r['drag']),
     'momentum':abs(2*p['rho']*r['area']*r['vi']*math.hypot(r['inPlane'],r['axial']+r['vi'])-r['thrust'])/r['thrust'],
    }
    if any(v>1e-10 for v in invariant.values()):failures.append(dict(index=i,case=case,invariant=invariant))
    if r['range'] is not None:
        residual=abs(r['fixedEnergy']+r['electrical']*r['range']/r['speed']-r['usableEnergy'])
        if residual>1e-9*max(1,r['usableEnergy']):failures.append(dict(index=i,case=case,energy_closure=residual))
        if 1<=r['range']<=250:trip_boundary.append(dict(inputs={**case['inputs'],'tripDistance':r['range']},winged=case['winged'],kind='trip-boundary',name=case['name']))
    if case['kind']=='named':examples.append(dict(name=case['name'],inputs=case['inputs'],winged=case['winged'],mass_kg=r['mass'],wing_lift_N=r['wingLift'],cruise_kW=r['electrical'],hover_kW=r['hoverPower'],range_km=r['range'],raw_energy_only_range_km=r['rawRange'],trip_energy_kWh=r['tripEnergy'],trip_margin_kWh=r['tripMargin'],feasible=r['feasible'],violations=r['violations'],python_cruise_kW=ref['electrical'],python_hover_kW=ref['hoverPower'],python_range_km=ref['rawRange']))
boundary_results=js({'cases':trip_boundary})
boundary_misclassifications=[]
for case,r in zip(trip_boundary,boundary_results):
    if r['feasible'] and not r['tripOk'] and abs(r['tripMargin'])<1e-10:
        boundary_misclassifications.append(dict(case=case,tripMargin=r['tripMargin'],range=r['range'],tripDistance=case['inputs']['tripDistance']))
summary=dict(source_model_path=str(MODEL),source_model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),total_valid_cases=len(cases),random_cases=args.random,one_factor_boundary_cases=sum(c['kind']=='one-factor-boundary' for c in cases),corner_cases=sum(c['kind']=='corner' for c in cases),named_cases=len(named),feasible=feasible,screened_out=screened,solver_and_invariant_failures=len(failures),max_scaled_relative_errors=max_error,trip_energy_boundary_cases=len(trip_boundary),trip_boundary_false_failures=len(boundary_misclassifications),trip_boundary_example=boundary_misclassifications[:3],examples=examples,failures=failures[:20])
(HERE/(args.prefix+'audit_results.json')).write_text(json.dumps(summary,indent=2)+'\n')
(HERE/(args.prefix+'named_examples.json')).write_text(json.dumps(examples,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['examples','failures']},indent=2))
