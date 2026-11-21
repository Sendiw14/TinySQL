// WCAG 2.x contrast ratios for the ADR-11 starter token pairings. Run: node scripts/contrast.mjs
const t = { canvas:'#F7F9FC', surface:'#FFFFFF', elevated:'#F0F4F9', ink:'#111827', ink2:'#4B5563', hairline:'#DBE3ED',
  accent:'#1858C8', muted:'#EAF2FF', success:'#166534', warning:'#925400', destructive:'#B42318', focus:'#1746A2', control:'#76839A' };
// hairline is decorative-only (dividers); WCAG 1.4.11 needs 3:1 only for meaningful UI, so it is checked as 'control' instead.
const lum = h => { const c = [1,3,5].map(i => parseInt(h.slice(i,i+2),16)/255).map(v => v<=0.03928 ? v/12.92 : ((v+0.055)/1.055)**2.4);
  return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]; };
const ratio = (a,b) => { const [x,y]=[lum(a),lum(b)].sort((p,q)=>q-p); return (x+0.05)/(y+0.05); };
// [foreground, background, required minimum]
const pairs = [];
for (const bg of ['canvas','surface','elevated','muted'])
  for (const [fg,min] of [['ink',4.5],['ink2',4.5],['accent',4.5],['success',4.5],['warning',4.5],['destructive',4.5],['focus',3],['control',3]])
    pairs.push([fg,bg,min]);
let fail = 0;
for (const [fg,bg,min] of pairs) { const r = ratio(t[fg],t[bg]); const ok = r>=min; if(!ok) fail++;
  console.log(`${ok?'PASS':'FAIL'} ${fg.padEnd(11)} on ${bg.padEnd(8)} ${r.toFixed(2)}:1 (min ${min})`); }
process.exitCode = fail ? 1 : 0;
