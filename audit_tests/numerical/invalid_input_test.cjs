const fs=require('node:fs');
const M=require(require('node:path').resolve(process.argv[2]));
const failures=[];let rejected=0,total=0;
for(const [key,[lo,hi]]of Object.entries(M.LIMITS)){
 const values=[NaN,Infinity,-Infinity,'','1',null,true,{},[],undefined,lo-1,hi+1];
 for(const value of values){
  total++;try{M.calculate({...M.DEFAULTS,[key]:value});failures.push({key,type:typeof value,value:String(value),reason:'not rejected'});}catch(e){if(e instanceof RangeError)rejected++;else failures.push({key,type:typeof value,value:String(value),reason:e.name});}
 }
}
for(const values of [{soc:30,reserve:30},{soc:30,reserve:40},{soc:60,reserve:60}]){
 total++;try{M.calculate({...M.DEFAULTS,...values});failures.push({values,reason:'invalid reserve accepted'});}catch(e){if(e instanceof RangeError)rejected++;else failures.push({values,reason:e.name});}
}
const out={total,rejected,failures};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n');
process.stdout.write(JSON.stringify(out,null,2)+'\n');if(failures.length)process.exitCode=1;
