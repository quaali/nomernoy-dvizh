const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(new URL('../dist/index.html',`file://${__filename}`),'utf8').split('<script>')[1].split("document.addEventListener('click'")[0];
let sample=.5;const rng=Object.create(Math);rng.random=()=>sample;
const context={localStorage:{getItem:()=>null},Math:rng};vm.createContext(context);vm.runInContext(code,context);
const regions=Array.from(vm.runInContext('REGIONS',context));assert.equal(regions.length,172);assert.equal(new Set(regions).size,regions.length);
for(let n=1;n<=99;n++)assert(regions.includes(String(n).padStart(2,'0')));
for(const c of ['03','09','14','22','25','27','38','39','41','47','49','52','54','55','63','65','66','70','74','78','83','86','87','89','94','102','116','123','152','161','178','196','224','252','702','725','754','774','778','790','797','799','977'])assert(regions.includes(c));
for(let i=0;i<regions.length;i++){sample=(i+.5)/regions.length;assert.equal(vm.runInContext("rollPart('region')",context),regions[i]);}
assert(regions.every(c=>/^\d{2,3}$/.test(c)&&c!=='00'),'invalid region format');
console.log('PASS: all 99 two-digit codes, 73 additional series, no duplicates, each code reachable with the same random interval.');
