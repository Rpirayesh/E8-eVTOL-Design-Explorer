
"use strict";
// SI internally: N, m, s, W; reported power kW, energy kWh, range km.
const N = 8;
const G = 9.80665;
const DEFAULTS = Object.freeze({speed:120,emptyMass:330,personMass:95,batteryMass:180,diameter:1.8,wingMass:60,wingArea:10,aspectRatio:7,oswald:0.8,clMax:1.5,stallMargin:1.2,wingCd0:0.025,flatPlate:0.65,rho:1.225,tipSpeed:170,solidity:0.08,bladeCd:0.012,kappa:1.15,motorEfficiency:0.92,motorPower:25,auxPower:1,specificEnergy:220,soc:90,reserve:20,maxC:5,hoverMinutes:2,transitionEnergy:2,tripDistance:40});
const LIMITS = Object.freeze({speed:[20,220],emptyMass:[150,1000],personMass:[50,150],batteryMass:[20,600],diameter:[0.8,3],wingMass:[0,200],wingArea:[2,25],aspectRatio:[3,15],oswald:[0.5,1],clMax:[0.6,2.5],stallMargin:[1,1.5],wingCd0:[0.01,0.08],flatPlate:[0.1,3],rho:[0.7,1.3],tipSpeed:[120,220],solidity:[0.04,0.18],bladeCd:[0.006,0.03],kappa:[1,1.6],motorEfficiency:[0.7,0.98],motorPower:[5,80],auxPower:[0,5],specificEnergy:[100,400],soc:[30,100],reserve:[0,60],maxC:[1,12],hoverMinutes:[0,10],transitionEnergy:[0,10],tripDistance:[1,250]});
function validate(p) {
  for (const [k,[min,max]] of Object.entries(LIMITS)) if (!Number.isFinite(p[k]) || p[k]<min || p[k]>max) throw new RangeError(`${k} must be between ${min} and ${max}.`);
  if(p.reserve>=p.soc) throw new RangeError('Reserve must be smaller than starting state of charge.');
  return p;
}
// Positive, monotonic momentum-theory root. Hover induced velocity is an upper bound
// for nonnegative axial inflow. Bisection avoids fixed-point instability near hover.
function inducedVelocity(thrust,rho,area,axial,inPlane) {
  if(thrust===0) return 0;
  if(thrust<0||rho<=0||area<=0||axial<0||inPlane<0) throw new RangeError('Invalid inflow state.');
  let lo=0,hi=Math.sqrt(thrust/(2*rho*area));
  for(let i=0;i<64;i++) {const v=(lo+hi)/2; const t=2*rho*area*v*Math.hypot(inPlane,axial+v); if(t>thrust)hi=v;else lo=v;}
  return (lo+hi)/2;
}
function calculate(p,winged=true,speed=p.speed) {
  validate({...p,speed});
  const mass=p.emptyMass+2*p.personMass+p.batteryMass+(winged?p.wingMass:0);
  const weight=mass*G,area=N*Math.PI*p.diameter**2/4,velocity=speed/3.6,q=0.5*p.rho*velocity**2;
  const clLimit=p.clMax/p.stallMargin**2;
  const wingLift=winged?Math.min(weight,q*p.wingArea*clLimit):0;
  const cl=winged?wingLift/(q*p.wingArea):0;
  const bodyDrag=q*p.flatPlate;
  const wingZeroDrag=winged?q*p.wingArea*p.wingCd0:0;
  const wingInducedDrag=winged?q*p.wingArea*cl**2/(Math.PI*p.oswald*p.aspectRatio):0;
  const drag=bodyDrag+wingZeroDrag+wingInducedDrag,vertical=weight-wingLift;
  const thrust=Math.hypot(vertical,drag),tilt=Math.atan2(drag,vertical);
  const axial=velocity*Math.sin(tilt),inPlane=velocity*Math.cos(tilt);
  const vi=inducedVelocity(thrust,p.rho,area,axial,inPlane);
  const mu=inPlane/p.tipSpeed;
  const profileHover=p.solidity*p.bladeCd/8*p.rho*area*p.tipSpeed**3;
  // Screening approximation, not the full NDARC profile/in-plane-force model.
  const profile=profileHover*(1+3*mu**2);
  const induced=p.kappa*thrust*vi,useful=drag*velocity;
  const shaft=(induced+useful+profile)/1000;
  const electrical=shaft/p.motorEfficiency+p.auxPower;
  const hoverVi=Math.sqrt(weight/(2*p.rho*area));
  const hoverShaft=(p.kappa*weight*hoverVi+profileHover)/1000;
  const hoverPower=hoverShaft/p.motorEfficiency+p.auxPower;
  const nominalEnergy=p.batteryMass*p.specificEnergy/1000;
  const usableEnergy=nominalEnergy*(p.soc-p.reserve)/100;
  const hoverEnergy=hoverPower*p.hoverMinutes/60;
  const fixedEnergy=hoverEnergy+p.transitionEnergy;
  const cruiseEnergy=Math.max(0,usableEnergy-fixedEnergy);
  const rawRange=cruiseEnergy/electrical*speed;
  const batteryLimit=nominalEnergy*p.maxC;
  const shaftLimit=N*p.motorPower;
  const violations=[];
  if(hoverShaft>shaftLimit+1e-8)violations.push('Hover exceeds the installed shaft-power limit.');
  if(shaft>shaftLimit+1e-8)violations.push('Cruise exceeds the installed shaft-power limit.');
  if(hoverPower>batteryLimit+1e-8)violations.push('Hover exceeds the battery discharge-power limit.');
  if(electrical>batteryLimit+1e-8)violations.push('Cruise exceeds the battery discharge-power limit.');
  if(mu>0.35)violations.push('Edgewise advance ratio exceeds the model screen (μ > 0.35).');
  if(usableEnergy<=fixedEnergy)violations.push('Hover and transition consume the available mission energy.');
  const powerOk=hoverShaft<=shaftLimit+1e-8&&shaft<=shaftLimit+1e-8&&hoverPower<=batteryLimit+1e-8&&electrical<=batteryLimit+1e-8;
  const feasible=violations.length===0;
  const tripCruiseEnergy=electrical*p.tripDistance/speed;
  const tripEnergy=fixedEnergy+tripCruiseEnergy;
  const rawTripMargin=usableEnergy-tripEnergy;
  const energyTolerance=1e-10*Math.max(1,usableEnergy,tripEnergy);
  const tripMargin=Math.abs(rawTripMargin)<=energyTolerance?0:rawTripMargin;
  const hoverAvailableShaft=Math.max(0,Math.min(shaftLimit,(batteryLimit-p.auxPower)*p.motorEfficiency));
  const maxHoverThrust=(Math.max(0,hoverAvailableShaft*1000-profileHover)*Math.sqrt(2*p.rho*area)/p.kappa)**(2/3);
  return {winged,speed,mass,weight,area,q,cl,clLimit,wingLift,vertical,drag,bodyDrag,wingZeroDrag,wingInducedDrag,thrust,tilt,axial,inPlane,vi,mu,profile,profileHover,induced,useful,shaft,electrical,hoverShaft,hoverPower,hoverVi,nominalEnergy,usableEnergy,hoverEnergy,fixedEnergy,cruiseEnergy,rawRange,range:feasible?rawRange:null,endurance:feasible?cruiseEnergy/electrical*60:null,batteryLimit,shaftLimit,powerOk,feasible,violations,tripCruiseEnergy,tripEnergy,tripMargin,tripOk:feasible&&tripMargin>=0,maxHoverThrust,stallSpeed:winged?Math.sqrt(2*weight/(p.rho*p.wingArea*p.clMax))*3.6:null,span:winged?Math.sqrt(p.wingArea*p.aspectRatio):null};
}
function sweep(p) {return Array.from({length:101},(_,i)=>{const speed=20+2*i;return {speed,winged:calculate(p,true,speed),wingless:calculate(p,false,speed)};});}
// Lightweight checks run in the delivered app; broader regression tests live in tests/.
function selfChecks() {
  const p={...DEFAULTS},a=calculate(p,true),b=calculate(p,false),r=inducedVelocity(5000,1.225,20,0,0);
  const boundaryBase=calculate({...p,rho:0.7},true);
  const boundary=calculate({...p,rho:0.7,tripDistance:boundaryBase.range},true);
  return [
    ['Hover analytical solution',Math.abs(r-Math.sqrt(5000/(2*1.225*20)))<1e-10],
    ['Vertical force balance',Math.abs(a.wingLift+a.vertical-a.weight)<1e-8],
    ['Horizontal force balance',Math.abs(a.thrust*Math.sin(a.tilt)-a.drag)<1e-8],
    ['Cruise momentum residual',Math.abs(2*p.rho*a.area*a.vi*Math.hypot(a.inPlane,a.axial+a.vi)-a.thrust)<1e-7],
    ['Mission energy conservation',Math.abs(a.fixedEnergy+a.tripCruiseEnergy-a.tripEnergy)<1e-10],
    ['Wingless rotor lift equals weight',Math.abs(b.vertical-b.weight)<1e-8],
    ['Wing mass included',Math.abs(a.mass-b.mass-p.wingMass)<1e-10],
    ['Losses increase electrical power',a.electrical>a.shaft&&b.electrical>b.shaft],
    ['Exact-range mission boundary',boundary.tripOk&&boundary.tripMargin===0]
  ];
}


module.exports={N,G,DEFAULTS,LIMITS,validate,inducedVelocity,calculate,sweep,selfChecks};
