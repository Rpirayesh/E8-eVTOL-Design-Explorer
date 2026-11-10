"""Check exact, inside, and outside maximum-range trip classifications.

Usage: python3 boundary_regression.py --model /absolute/model.cjs
Distance perturbation is 0.0001 km (0.1 m), much larger than roundoff tolerance.
"""
from pathlib import Path
import argparse,json,subprocess
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--output',default='boundary_regression_results.json');args=ap.parse_args()
def js(cases):
 r=subprocess.run(['node',str(HERE/'run_model.cjs'),args.model],input=json.dumps({'cases':cases}),capture_output=True,text=True,check=True)
 return json.loads(r.stdout)
base=[]
for empty in [150,330,600,1000]:
 for battery in [50,180,300,600]:
  for speed in [40,80,120,160,200,220]:
   for winged in [False,True]:
    for rho in [.7,1.225,1.3]:
     base.append(dict(inputs=dict(emptyMass=empty,batteryMass=battery,speed=speed,rho=rho),winged=winged))
results=js(base);checks=[]
for c,r in zip(base,results):
 if r.get('feasible') and r['range'] is not None and 1.0001<=r['range']<=249.9999:
  for kind,delta,expected in [('exact',0,True),('inside',-.0001,True),('outside',.0001,False)]:
   checks.append(dict(inputs={**c['inputs'],'tripDistance':r['range']+delta},winged=c['winged'],kind=kind,expected_trip_ok=expected))
tested=js(checks);failures=[];classification_failures=0;exact_not_normalized=0
for c,r in zip(checks,tested):
 if r['tripOk']!=c['expected_trip_ok']:classification_failures+=1
 if c['kind']=='exact' and r['tripMargin']!=0:exact_not_normalized+=1
 if r['tripOk']!=c['expected_trip_ok'] or (c['kind']=='exact' and r['tripMargin']!=0):
  failures.append(dict(case=c,actual_trip_ok=r['tripOk'],trip_margin_kWh=r['tripMargin'],range_km=r['range']))
out=dict(base_operating_points=len(base),eligible_feasible_points=len(checks)//3,classification_cases=len(checks),exact_range_cases=len(checks)//3,inside_cases=len(checks)//3,outside_cases=len(checks)//3,distance_perturbation_km=.0001,failures=len(failures),classification_failures=classification_failures,exact_not_normalized=exact_not_normalized,failure_examples=failures[:5])
(HERE/args.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if failures:raise SystemExit(1)
