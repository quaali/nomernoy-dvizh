const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(new URL('../dist/index.html',`file://${__filename}`),'utf8').split('<script>')[1].split("document.addEventListener('click'")[0];
let seed=123456789;const rng=Object.create(Math);rng.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const context={localStorage:{getItem:()=>null},Math:rng};vm.createContext(context);vm.runInContext(code,context);
const result=vm.runInContext(`
const counts={digits:{triple:0,pair:0,plain:0},letters:{triple:0,pair:0,amr:0,plain:0}};
for(const part of ['digits','letters'])for(let i=0;i<100000;i++){
 const value=rollPart(part);if(value.length!==3)throw Error('Invalid length');
 if(part==='digits'&&(!/^[0-9]{3}$/.test(value)||value==='000'))throw Error('Invalid digits');
 if(part==='letters'&&[...value].some(c=>!ABC.includes(c)))throw Error('Invalid letters');
 const distinct=new Set(value).size;
 counts[part][value==='АМР'?'amr':distinct===1?'triple':distinct===2?'pair':'plain']++;
}
counts`,context);
for(const [part,expected] of Object.entries({digits:{triple:.01,pair:.20,plain:.79},letters:{triple:.01,pair:.20,amr:.005,plain:.785}}))for(const [bucket,chance] of Object.entries(expected))assert(Math.abs(result[part][bucket]/100000-chance)<.006,`${part} ${bucket} frequency mismatch`);
for(const part of ['digits','letters'])assert.equal(vm.runInContext(`new Set(Object.values(SPIN_POOLS.${part}).flat()).size`,context),part==='digits'?999:1727,'missing or duplicate outcomes');
console.log('PASS: 100,000 draws per part, weighted frequencies, all valid combinations and no 000.');console.log(JSON.stringify(result));
