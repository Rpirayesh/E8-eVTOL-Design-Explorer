// Executes the exact distributed viewer script with a small DOM adapter and real native Canvas.
// This is not a browser or accessibility/layout test. Optional real-browser test: test_viewer.cjs.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {createCanvas}=require('@napi-rs/canvas');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'viewer/E8_3D_Viewer_Offline.html'),'utf8');
const source=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];assert.equal(source.length,1);
const all=[],nodes=new Map(),timers=new Map();let timerId=0,ops=0,network=0;
class Element{
 constructor(id=''){this.id=id;this.handlers={};this.dataset={};this.children=[];this.value='';this.checked=false;this.textContent='';this.innerHTML='';all.push(this)}
 append(...children){this.children.push(...children)}
 addEventListener(name,fn){(this.handlers[name]??=[]).push(fn)}
 fire(name,extra={}){ops++;for(const fn of this.handlers[name]??[])fn({target:this,preventDefault(){},pointerId:1,clientX:0,clientY:0,...extra});if(name==='click'&&this.onclick)this.onclick();flush()}
}
for(const id of ['view','layers','stats','wing','tilt','tiltValue','explode','disks','reset','tag','selection'])nodes.set(id,new Element(id));
nodes.get('wing').checked=true;nodes.get('tilt').value='0';nodes.get('explode').value='0';
const canvas=createCanvas(1150,650);Object.assign(canvas,{clientWidth:1150,clientHeight:650,handlers:{},addEventListener:Element.prototype.addEventListener,fire:Element.prototype.fire,setPointerCapture(){}});nodes.set('view',canvas);
const views=['iso','top','side','front'].map(v=>{const el=new Element();el.dataset.view=v;return el});
const document={getElementById:id=>nodes.get(id),createElement:()=>new Element(),createTextNode:text=>({textContent:text}),querySelectorAll:sel=>sel==='[data-view]'?views:all.filter(x=>x.dataset.layer)};
function flush(){let callbacks=[...timers.values()];timers.clear();for(const fn of callbacks)fn()}
const context=vm.createContext({document,devicePixelRatio:1,console,Math,requestAnimationFrame:fn=>{timers.set(++timerId,fn);return timerId},cancelAnimationFrame:id=>timers.delete(id),ResizeObserver:class{constructor(fn){this.fn=fn}observe(){this.fn()}},fetch(){network++;throw Error('Unexpected network')},XMLHttpRequest:class{constructor(){network++;throw Error('Unexpected network')}}});
new vm.Script(source[0][1],{filename:'distributed-viewer.js'}).runInContext(context);flush();
assert.match(nodes.get('tag').textContent,/Winged.*167 visible/);
const hash=()=>crypto.createHash('sha256').update(canvas.toBuffer('image/png')).digest('hex');const first=hash();
for(const v of views)v.fire('click');
nodes.get('wing').checked=false;nodes.get('wing').fire('input');assert.match(nodes.get('tag').textContent,/Wingless/);
for(const tilt of [0,15,30,45,60,75,90]){nodes.get('tilt').value=String(tilt);nodes.get('tilt').fire('input');assert.ok(nodes.get('tiltValue').textContent.startsWith(tilt+'°'))}
for(const el of all.filter(x=>x.dataset.layer)){el.checked=false;el.fire('change');el.checked=true;el.fire('change')}
for(let i=0;i<50;i++){nodes.get('tilt').value=String(i%2?90:0);nodes.get('explode').value=String(i%2?100:0);nodes.get('explode').fire('input')}
nodes.get('disks').checked=true;nodes.get('disks').fire('input');
canvas.fire('pointerdown',{clientX:100,clientY:100});canvas.fire('pointermove',{clientX:140,clientY:120});canvas.fire('pointerup');canvas.fire('wheel',{deltaY:-100});
nodes.get('reset').fire('click');assert.equal(nodes.get('wing').checked,true);assert.equal(nodes.get('tilt').value,0);assert.equal(nodes.get('explode').value,0);assert.equal(hash(),first);
fs.writeFileSync(path.join(root,'images/Viewer_Canvas_Desktop.png'),canvas.toBuffer('image/png'));
canvas.clientWidth=390;canvas.clientHeight=460;views[1].fire('click');assert.equal(canvas.width,390);assert.equal(canvas.height,460);
fs.writeFileSync(path.join(root,'images/Viewer_Canvas_Mobile.png'),canvas.toBuffer('image/png'));
const transforms=vm.runInContext(`(()=>{const p=mesh.find(x=>x.rotor===0);return [0,45,90].map(a=>transform([p.pivot_mm[0]/1000,p.pivot_mm[1]/1000,p.pivot_mm[2]/1000+.4],p,a,0))})()`,context);
assert.ok(Math.abs(transforms[2][0]-(-4.45-.4))<1e-10);assert.ok(Math.abs(transforms[2][2]-2.1)<1e-10);assert.equal(network,0);
const results={status:'pass',script:'Exact inline script from distributed HTML',operations:ops,network_calls:network,canvas_sizes:[[1150,650],[390,460]],components:167,tilt_hub_coordinates_m:transforms,renderer:'@napi-rs/canvas',real_browser:false,limits:'Small DOM adapter; no native browser layout, accessibility or cross-browser verification. Chromium launch attempted but blocked by the execution environment Unix-socket restriction. Optional Playwright browser test is included for local reproduction.'};
fs.writeFileSync(path.join(root,'reviews/viewer_results.json'),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results));
