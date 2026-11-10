import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {DEFAULTS,LIMITS,calculate}=require('../model-extracted.cjs');
const file=process.argv[2]??new URL('../../E8_eVTOL_Explorer_Offline.html',import.meta.url).pathname;
const label=fs.readFileSync(file,'utf8').includes('STUDENT EDITION 1.1')?'revised':'original';
const html=fs.readFileSync(file,'utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
assert.equal(scripts.length,1);
const code=new vm.Script(scripts[0][1],{filename:file+':inline'});
const failures=[],checks=[];let operationCount=0;
const check=(name,fn)=>{try{fn();checks.push({name,pass:true});}catch(e){failures.push({name,error:e.message});checks.push({name,pass:false});}};
function boot({stored=null,getThrows=false,setThrows=false}={}){
 const nodes=new Map(),blobs=[],downloads=[],storage=new Map(),timers=new Map();let networkCalls=0,timerId=0;
 if(stored!==null)storage.set('e8-offline-student-v1',stored);
 class El{
  constructor(id){this.id=id;this.value='';this.innerHTML='';this.textContent='';this.handlers={};this.attrs={};this.dataset={};this.hidden=false;this.classes=new Set();this.classList={add:x=>this.classes.add(x),remove:x=>this.classes.delete(x),toggle:(x,on)=>on?this.classes.add(x):this.classes.delete(x)};this.style={setProperty(){}};}
  addEventListener(k,f){(this.handlers[k]??=[]).push(f);}
  set innerHTML(value){this._html=value;if(this.id==='chart')this.svg=new El('svg');}
  get innerHTML(){return this._html;}
  fire(k,more={}){operationCount++;for(const f of this.handlers[k]??[])f({currentTarget:this,...more});}
  setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
  getAttribute(k){return this.attrs[k]??null;}
  querySelector(sel){if(sel==='svg'){return this.svg??=new El('svg');}return null;}
  getBoundingClientRect(){return {left:0,top:0,width:520,height:245};}
  getScreenCTM(){return {inverse(){return {};}};}
  createSVGPoint(){return {x:0,y:0,matrixTransform(){return {x:this.x,y:this.y};}};}
  click(){if(this.download)downloads.push(this.download);this.fire('click');}
  remove(){}
 }
 const get=id=>{if(!nodes.has(id))nodes.set(id,new El(id));return nodes.get(id);};
 const tabs=['overview','equations','validation'].map(id=>{const n=new El(id+'-tab');n.dataset.panel=id;return n;});
 const document={getElementById:get,querySelectorAll:s=>s==='.tab'?tabs:[],createElement:()=>new El('link'),body:{appendChild(){}}};
 const network=()=>{networkCalls++;throw new Error('Unexpected network use');};
 const context=vm.createContext({document,localStorage:{getItem:k=>{if(getThrows)throw Error('get denied');return storage.get(k)??null;},setItem:(k,v)=>{if(setThrows)throw Error('set denied');storage.set(k,v);}},fetch:network,XMLHttpRequest:network,WebSocket:network,Blob,URL:{createObjectURL:b=>{blobs.push(b);return 'blob:offline-export';},revokeObjectURL(){}},setTimeout:f=>{timers.set(++timerId,f);return timerId;},clearTimeout:id=>timers.delete(id)});
 code.runInContext(context,{timeout:5000});
 return {get,tabs,storage,blobs,downloads,networkCalls:()=>networkCalls,
  input(k,v,commit=false){get(k).value=String(v);get(k).fire(commit?'change':'input');},
  snapshot(){return JSON.parse(storage.get('e8-offline-student-v1')??'null');}};
}
check('Offline packaging has one inline script and no external resource dependency',()=>{
 assert.ok(!/\bfetch\s*\(|\bimport\s+|type=["']module/.test(html));
 assert.ok(!/<(?:script|link|img|iframe)[^>]+(?:src|href)=["']https?:/i.test(html));
 assert.ok(!/@import\s|url\(["']?https?:/i.test(html));assert.match(html,/connect-src 'none'/);
});
if(label==='revised')check('Responsive CSV export button stays visible and has explicit accessible name',()=>{
 assert.match(html,/<button[^>]+id="export"[^>]+aria-label="Export study as CSV"/);
 assert.ok(!/\.page-head>\.outline-button\{display:none\}/.test(html));
});
if(label==='revised')check('CSV export refuses a pending invalid edit, then succeeds after correction',()=>{
 const app=boot();app.input('speed',999);app.get('export').click();assert.equal(app.blobs.length,0);assert.match(app.get('toast').textContent,/Correct the highlighted/);
 app.input('speed',160);app.get('export').click();assert.equal(app.blobs.length,1);assert.equal(app.downloads.at(-1),'E8_design_study.csv');
});
for(const scenario of [{},{getThrows:true},{setThrows:true},{getThrows:true,setThrows:true},{stored:'not JSON'},{stored:'null'},{stored:'[]'},{stored:'{"inputs":{"speed":0}}'},{stored:'{"inputs":{"rho":"1.225"}}'},{stored:'{"inputs":{"reserve":60,"soc":30}}'}]){
 check('Storage scenario '+JSON.stringify(scenario),()=>{const app=boot(scenario);assert.match(app.get('metrics').innerHTML,/46\.2/);assert.equal((app.get('reference-table').innerHTML.match(/✓ Pass/g)??[]).length,5);assert.equal(app.networkCalls(),0);});
}
check('Every numeric field accepts both permitted bounds (subject to SOC constraint)',()=>{
 const app=boot();
 for(const [k,[lo,hi]]of Object.entries(LIMITS))for(const v of [lo,hi]){
  app.get('reset').click();if(k==='soc')app.input('reserve',0);app.input(k,v);
  assert.equal(app.snapshot().inputs[k],v,k+': '+v);assert.equal(app.get(k).attrs['aria-invalid'],undefined);
  for(const target of ['metrics','chart','comparison-body','energy'])assert.ok(!/NaN|Infinity|undefined/.test(app.get(target).innerHTML),target);
 }
});
check('Invalid inputs preserve last valid assumptions and clearly mark pending edits',()=>{
 const app=boot();
 for(const [k,[lo,hi]]of Object.entries(LIMITS))for(const value of ['',NaN,Infinity,lo-1,hi+1,'abc']){
  app.get('reset').click();const before=app.snapshot();app.input(k,value);
  assert.deepEqual(app.snapshot(),before,k+': invalid mutated model');assert.equal(app.get(k).attrs['aria-invalid'],'true');
  assert.match(app.get('save-status').textContent,/last valid/);app.input(k,value,true);assert.equal(app.get(k).value,before.inputs[k]);
 }
});
check('Configuration, chart metric and view buttons stay consistent',()=>{
 const app=boot();
 for(let i=0;i<100;i++){
  app.get('wingless-button').click();assert.equal(app.snapshot().winged,false);assert.match(app.get('metrics').innerHTML,/All vertical support/);
  app.get('winged-button').click();assert.equal(app.snapshot().winged,true);
  app.get(i%2?'chart-power':'chart-range').click();assert.match(app.get('chart-title').textContent,i%2?/Power/:/Range/);
  const tab=app.tabs[i%3];tab.click();for(const other of app.tabs)assert.equal(app.get(other.dataset.panel).hidden,other!==tab);
 }
});
check('Chart click speed conversion clamps and rounds correctly',()=>{
 const app=boot();
 for(const [clientX,speed]of [[-10,20],[43,20],[272.5,120],[502,220],[800,220]]){
  app.get('chart').querySelector('svg').fire('click',{clientX,clientY:100});assert.equal(app.snapshot().inputs.speed,speed);
 }
});
let seed=77431;const random=()=>((seed=(1664525*seed+1013904223)>>>0)/2**32);
check('1,000 mixed repeated valid edits and resets remain finite and deterministic',()=>{
 const app=boot(),keys=Object.keys(LIMITS);
 for(let i=0;i<1000;i++){
  if(i%43===0)app.get('reset').click();const k=keys[Math.floor(random()*keys.length)],[lo,hi]=LIMITS[k];let v=lo+random()*(hi-lo);
  if(k==='soc')v=Math.max(v,app.snapshot().inputs.reserve+.01);if(k==='reserve')v=Math.min(v,app.snapshot().inputs.soc-.01);
  app.input(k,v);
  assert.equal(app.snapshot().inputs[k],v);
  for(const target of ['metrics','chart','comparison-body','energy'])assert.ok(!/NaN|Infinity|undefined/.test(app.get(target).innerHTML),target);
  assert.equal(app.networkCalls(),0);
 }
});
async function exportCheck(){
 const app=boot();let mismatches=0;
 for(let i=0;i<40;i++){
  app.input('speed',20+5*i);if(i%2)app.get('wingless-button').click();else app.get('winged-button').click();app.get('export').click();
  const text=await app.blobs.at(-1).text(),rows=text.split('\r\n').map(line=>{let cells=[],x='',quoted=false;for(let c=0;c<line.length;c++){const ch=line[c];if(ch==='"'){if(quoted&&line[c+1]==='"'){x+='"';c++;}else quoted=!quoted;}else if(ch===','&&!quoted){cells.push(x);x='';}else x+=ch;}cells.push(x);return cells;});
  const state=app.snapshot(),header=rows.findIndex(r=>r[0]==='Configuration');
  for(const w of [true,false]){const row=rows[header+(w?1:2)],r=calculate(state.inputs,w);assert.equal(row[0],w?'Winged':'Wingless');assert.equal(Number(row[1]),r.mass);assert.equal(Number(row[4]),r.electrical);assert.equal(Number(row[5]),r.hoverPower);assert.equal(row[6],r.range===null?'':String(r.range));assert.equal(Number(row[7]),r.tripEnergy);assert.equal(row[9],String(r.feasible));}
  assert.equal(rows[0][0],'E8 design study');assert.equal(app.downloads.at(-1),'E8_design_study.csv');assert.equal(app.networkCalls(),0);
  assert.equal(rows.filter(row=>/^\d+$/.test(row[0])&&row.length===5).length,101);
 }
 checks.push({name:'40 CSV exports match current assumptions, configuration results and 101-point sweeps',pass:true});
}
await exportCheck().catch(e=>failures.push({name:'CSV',error:e.message}));
const report={source:file,checkGroups:checks.length,passed:checks.filter(x=>x.pass).length,failed:failures.length,operations:operationCount,checks,failures,
 browserVerification:{actualFile:'Not completed',native:'Chromium launched; Sky text input failed due to unavailable AT-SPI provider.',cloud:'file: URL explicitly rejected; only http/https permitted. No workaround attempted.'},
 defects:label==='original'?[{severity:'medium',name:'CSV export hidden for 621–820px viewport widths',evidence:'.page-head>.outline-button{display:none} at max-width:820, restored only at max-width:620',repro:'Open at 700 CSS px width: sole Export study button is hidden.'}]:[]};
fs.writeFileSync(new URL('findings-'+label+'.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(failures.length)process.exitCode=1;
