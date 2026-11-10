const fs=require('node:fs');
const M=require(require('node:path').resolve(process.argv[2]));
const request=JSON.parse(fs.readFileSync(0,'utf8'));
if(request.metadata){process.stdout.write(JSON.stringify({defaults:M.DEFAULTS,limits:M.LIMITS}));process.exit();}
const results=request.cases.map(c=>{try{return M.calculate({...M.DEFAULTS,...c.inputs},c.winged);}catch(e){return {error:e.name,message:e.message};}});
process.stdout.write(JSON.stringify(results));
