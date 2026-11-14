// Click-tests built PAR quiz pages: all right = 100, all wrong = 0, resume, no console errors, no horizontal overflow.
const {chromium}=require(process.env.PW||'playwright');const fs=require('fs'),path=require('path');
(async()=>{const root=path.resolve(__dirname,'..','..');const codes=process.argv.slice(2);const b=await chromium.launch();let bad=0;
for(const code of codes){const file='file://'+root+'/'+code+'/quiz/index.html';
 for(const vw of [900,390]){const pg=await b.newPage({viewport:{width:vw,height:800}});const errs=[];
  pg.on('console',m=>{if(m.type()==='error'&&!/fonts|ERR_|Failed to load/.test(m.text()))errs.push(m.text())});pg.on('pageerror',e=>errs.push(String(e)));
  await pg.addInitScript(()=>{window.__msgs=[];const o=window.parent.postMessage;window.parent.postMessage=(m)=>{window.__msgs.push(m)}});
  for(const mode of ['right','wrong']){await pg.goto(file);
   const key=await pg.evaluate(()=>Q.map(q=>q.a));
   for(let n=0;n<10;n++){const cnt=await pg.locator('.opt').count();
    let idx;const t=await pg.evaluate((n)=>Q[n].t,n);
    // find button by data-k
    const want=mode==='right'?key[n]:(key[n]+1)%(t==='mc'?4:3);
    await pg.locator('.opt[data-k="'+want+'"]').click();await pg.locator('#nx').click();}
   const pct=await pg.locator('.big').innerText();const msgs=await pg.evaluate(()=>window.__msgs.filter(m=>m.type==='quizResult'));
   const exp=mode==='right'?'100%':'0%';const band=await pg.locator('.band').innerText();
   const ok=pct===exp&&msgs.length===1&&msgs[0].score===(mode==='right'?10:0)&&msgs[0].maxScore===10&&msgs[0].programme==='Ritam Wellness for Parents'&&msgs[0].code===code;
   if(!ok){bad++;console.log('FAIL',code,vw,mode,pct,JSON.stringify(msgs).slice(0,200))}
   const ov=await pg.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);if(ov){bad++;console.log('OVERFLOW',code,vw)}
   if(mode==='right'&&band!=='Well grasped'){bad++;console.log('BAND',band)}}
  if(errs.length){bad++;console.log('ERRORS',code,vw,errs)}
  await pg.close()}
 console.log(code,'tested')}
await b.close();process.exit(bad?1:0)})();
