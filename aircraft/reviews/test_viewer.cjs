// Local software test; requires Playwright and an installed Chromium browser.
const fs=require('fs');const path=require('path');const assert=require('assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),errors=[],external=[];let operations=0;
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},offline:true});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url())});
 await page.goto('file://'+path.join(root,'viewer/E8_3D_Viewer_Offline.html'));
 await page.waitForFunction(()=>document.getElementById('tag').textContent.includes('visible components'));
 assert.match(await page.locator('#tag').textContent(),/Winged/);operations++;
 const full=await page.locator('#tag').textContent();
 await page.locator('#wing').uncheck();await page.waitForFunction(()=>document.getElementById('tag').textContent.startsWith('Wingless'));operations++;
 assert.notEqual(full,await page.locator('#tag').textContent());
 for(const tilt of [0,15,30,45,60,75,90]){
  await page.locator('#tilt').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}))},tilt);
  await page.waitForFunction(v=>document.getElementById('tiltValue').textContent.startsWith(v+'°'),tilt);operations++;
 }
 for(const view of ['iso','top','side','front']){await page.locator(`[data-view="${view}"]`).click();operations++}
 for(const layer of ['airframe','canopy','structure','aero','rotor','motor','battery','systems','cabin','gear']){
  await page.locator(`[data-layer="${layer}"]`).uncheck();await page.locator(`[data-layer="${layer}"]`).check();operations+=2;
 }
 for(let i=0;i<20;i++){
  await page.locator('#explode').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}))},i%2?100:0);
  await page.locator('#tilt').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}))},i%2?90:0);operations+=2;
 }
 await page.locator('#reset').click();await page.waitForFunction(()=>document.getElementById('tag').textContent.startsWith('Winged')&&document.getElementById('tiltValue').textContent.startsWith('0°'));operations++;
 assert.equal(await page.locator('[data-layer]:checked').count(),10);
 await page.screenshot({path:path.join(root,'images/Offline_Viewer_Desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.locator('[data-view="top"]').click();operations++;
 await page.waitForFunction(()=>document.getElementById('view').width>0);
 const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,canvas:document.getElementById('view').getBoundingClientRect().width}));
 assert.ok(layout.scroll<=layout.width+1,'Mobile horizontal overflow');
 await page.screenshot({path:path.join(root,'images/Offline_Viewer_Mobile.png'),fullPage:true});
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(external.length,0,'Unexpected external network calls');
 const result={status:'pass',real_browser:true,browser:'Chromium',offline:true,operations,external_requests:external,page_errors:errors,desktop:{width:1440,height:1000},mobile:layout,limits:'One Chromium version on Linux; geometry and aircraft physics are outside this software test'};
 fs.writeFileSync(path.join(root,'reviews/viewer_results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
