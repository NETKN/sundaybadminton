import re,sys,os
ROOT=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(ROOT,'src','app.html')).read()
def rep(x,y,s):
    assert x in s, x[:70]
    return s.replace(x,y,1)
s=src
# ---------- storage layer -> Supabase ----------
a=s.index("function setSync(mode){"); b=s.index("function savePlayer(id){")
NEW1=r'''const SB={url:'https://srddkabtoeeqkhtzyybn.supabase.co/rest/v1',key:'sb_publishable_SuUBatDveFEWYKM34FkhqQ_D0Ty8r8O'};
let hasCode=false,unlocked=!!ls.get('bd.ok'),code=ls.get('bd.code')||'',syncMode='wait';
async function sb(path,opt){const r=await fetch(SB.url+path,Object.assign({headers:{apikey:SB.key,'Content-Type':'application/json'}},opt)),t=await r.text();let j=null;try{j=t?JSON.parse(t):null}catch(e){}
  if(!r.ok){const e=new Error((j&&j.message)||('http '+r.status));e.status=r.status;e.pg=j&&j.code;throw e}return j}
const rpc=(fn,body)=>sb('/rpc/'+fn,{method:'POST',body:JSON.stringify(body||{})});
let actN=0;
function setSync(mode){syncMode=mode;const el=$('#sync');el.className='sync '+mode;el.querySelector('span').textContent={cloud:'Server Online'+(actN?' · '+actN:''),offline:'ออฟไลน์ · เก็บในเครื่องก่อน',err:'บันทึกไม่สำเร็จ ลองใหม่',wait:'กำลังเชื่อมต่อ…'}[mode]}
const jobs=[];let pumping=false;
const touched={};
function enqueue(key,fn,body){if(!db)return;if(key){const i=jobs.findIndex(j=>j.key===key&&!j.active);if(i>=0){jobs[i]={key,fn,body};pump();return}}jobs.push({key,fn,body});pump()}
async function pump(){if(pumping)return;pumping=true;
  while(jobs.length){const j=jobs[0];j.active=true;let ok=false;
    for(let a=0;a<2&&!ok;a++){try{await rpc(j.fn,j.body);ok=true}
      catch(e){if(e.pg==='28P01'){unlocked=false;ls.set('bd.ok',0);toast('รหัสก๊วนถูกเปลี่ยน ใส่รหัสใหม่เพื่อแก้ไขข้อมูลเก่า');break}
        if(a===0)await new Promise(r=>setTimeout(r,600+Math.random()*600))}}
    jobs.shift();setSync(ok?'cloud':'err')}
  pumping=false}
/* everyone: add a player, change a photo, run the round, add a finished match. club code only: overwrite or delete stored documents */
function dbWrite(path,data,op){const i=path.indexOf('/'),tbl=path.slice(0,i),id=path.slice(i+1);touched[path]=performance.now();
  if(tbl==='app')return enqueue(path,'bd_put_session',{p_data:data});
  if(op==='addMatch')return enqueue(null,'bd_add_match',{p_day:id,p_match:data});
  if(unlocked)return enqueue(path,'bd_put',{p_code:code,p_tbl:tbl,p_id:id,p_data:data});
  if(op==='addPlayer')return enqueue(null,'bd_add_player',{p_id:id,p_data:data});
  if(op==='photo')return enqueue(path+'#photo','bd_set_photo',{p_id:id,p_photo:data.photo||''})}
function liveSend(c,k,side,val){touched['live/c'+c]=performance.now();enqueue('live/c'+c+'#'+side,'bd_put_live',{p_court:c,p_k:k,p_side:side,p_val:val})}
/* ---------- live sync: every open device re-reads what changed every few seconds ---------- */
const known={};let polling=false,pollFail=0;
const canon=o=>JSON.stringify(o,(k,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.keys(v).sort().reduce((a,x)=>{if(v[x]!==undefined)a[x]=v[x];return a},{}):v);
function pendingFor(tbl,id){const p=tbl+'/'+id;return jobs.some(j=>(j.key&&(j.key===p||j.key.indexOf(p+'#')===0))||(tbl==='days'&&j.fn==='bd_add_match'&&j.body.p_day===id)||(tbl==='players'&&j.fn==='bd_add_player'&&j.body.p_id===id))}
const holdSession=()=>!!sheet&&!['finish','player','code'].includes(sheet);
async function poll(){if(polling||!db||shufBusy||document.visibilityState!=='visible')return;polling=true;const t0=performance.now();
  try{const idx=await sb('/bd_docs?select=tbl,id,updated_at');
    const skip=r=>pendingFor(r.tbl,r.id)||(touched[r.tbl+'/'+r.id]||0)>t0||(r.tbl==='app'&&holdSession());
    const want=idx.filter(r=>known[r.tbl+'/'+r.id]!==r.updated_at&&!skip(r)).slice(0,25);
    if(want.length){const f=want.map(r=>'and(tbl.eq.'+r.tbl+',id.eq."'+r.id+'")').join(',');
      const rows=await sb('/bd_docs?select=tbl,id,data,updated_at&or='+encodeURIComponent('('+f+')'));applyRemote(rows.filter(r=>!skip(r)))}
    pollFail=0;if(syncMode==='offline')setSync('cloud')
  }catch(e){if(++pollFail>=3&&syncMode==='cloud')setSync('offline')}
  polling=false}
function applyRemote(rows){let ch=false,sch=false,lch=false;
  rows.forEach(r=>{known[r.tbl+'/'+r.id]=r.updated_at;const d=r.data||{};
    if(r.tbl==='players'){if(canon(S.players[r.id])!==canon(d)){S.players[r.id]=d;ch=true}}
    else if(r.tbl==='days'){const nd={matches:Array.isArray(d.matches)?d.matches:[],gone:d.gone||[]},od=S.days[r.id]||{};
      if(canon({matches:od.matches||[],gone:od.gone||[]})!==canon(nd)){S.days[r.id]=nd;ch=true}}
    else if(r.tbl==='app'&&r.id==='session'){const ns=d.s||null,os=S.session;
      if(ns&&os&&os.drawer&&ns.stage==='draw'&&ns.rid===os.rid&&ns.ids.includes(os.drawer)&&!ns.tickets.some(t=>t.by===os.drawer))ns.drawer=os.drawer;
      if(canon(os)!==canon(ns)){S.session=ns;ch=sch=true}}
    else if(r.tbl==='live'){if(canon(live[r.id])!==canon(d)){live[r.id]=d;lch=true}}});
  if(!ch&&!lch)return;
  if(ch){ls.set('bd.players',S.players);ls.set('bd.days',S.days);ls.set('bd.session',S.session)}
  const s=S.session,inRound=['draw','setup','play'].includes(view);
  if(sch){if(!s&&inRound){view='home';toast('round นี้ถูกปิดจากเครื่องอื่นแล้ว')}else if(s&&inRound&&view!==s.stage)view=s.stage}
  if(sheet==='finish'){const c=s&&s.courts&&s.courts[fin.c];
    if(!c||!c.teams||c.start!==fin.st){sheet=null;fin=null;toast('สนามนี้ถูกบันทึกหรือเปลี่ยนจากเครื่องอื่นแล้ว');render();return}
    const l=liveFor(fin.c);if(l){['sa','sb'].forEach(k=>{const el=$('#sc_'+k),v=l[k]|0;if(el&&document.activeElement!==el&&fin[k]!==v){fin[k]=v;el.value=v}});refreshFin()}
    liveStrip();return}
  if(!sheet&&(ch||view==='play'))render();else if(lch)liveStrip()}
/* presence: each open device says "still here" every 4 s; the server answers with how many did so in the last 10 s */
let pingFail=0;
function devId(){let id=ls.get('bd.dev');if(!id){id='d'+uid()+uid();ls.set('bd.dev',id)}return id}
async function ping(){if(!db||document.visibilityState!=='visible')return;const id=devId();
  try{actN=+(await rpc('bd_ping',{p_id:id}))||0;pingFail=0}catch(e){if(++pingFail>=3)actN=0}
  if(syncMode==='cloud')setSync('cloud')}
setInterval(ping,4000);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')ping()});
setInterval(poll,2500);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')poll()});
'''
s=s[:a]+NEW1+s[b:]
a=s.index("async function connect(){"); b=s.index("/* ---------- helpers ---------- */")
NEW2=r'''async function connect(){
  try{
    const [rows,hc]=await Promise.all([sb('/bd_docs?select=tbl,id,data,updated_at'),rpc('bd_has_code')]);
    db=true;hasCode=!!hc;
    unlocked=!hasCode?true:(code?!!(await rpc('bd_check',{p_code:code})):false);ls.set('bd.ok',unlocked&&hasCode?1:0);
    const remoteP={},remoteD={};let ss;
    rows.forEach(r=>{known[r.tbl+'/'+r.id]=r.updated_at;if(r.tbl==='live'){live[r.id]=r.data||{};return}if(r.tbl==='players')remoteP[r.id]=r.data;else if(r.tbl==='days')remoteD[r.id]={matches:Array.isArray(r.data.matches)?r.data.matches:[],gone:r.data.gone||[]};else if(r.tbl==='app'&&r.id==='session')ss=r.data});
    for(const id in S.players)if(!remoteP[id]&&!S.players[id].hidden){remoteP[id]=S.players[id];dbWrite('players/'+id,S.players[id],'addPlayer')}
    for(const k in S.days){const loc=S.days[k].matches||[];if(!remoteD[k])remoteD[k]={matches:[],gone:[]};
      const have=new Set(remoteD[k].matches.map(m=>m.id));const extra=loc.filter(m=>!have.has(m.id)&&!(remoteD[k].gone||[]).includes(m.id));
      if(extra.length){remoteD[k].matches=remoteD[k].matches.concat(extra).sort((a,b)=>a.t-b.t);extra.forEach(m=>dbWrite('days/'+k,m,'addMatch'))}}
    S.players=remoteP;S.days=remoteD;
    if(ss!==undefined){S.session=ss.s||null}else if(S.session){dbWrite('app/session',{s:S.session})}
    ls.set('bd.players',S.players);ls.set('bd.days',S.days);ls.set('bd.session',S.session);
    setSync('cloud');ping();
    if(!sheet){if(view==='home'||!S.session&&['draw','setup','play'].includes(view))view='home';render()}
  }catch(e){db=false;setSync('offline')}
}
window.addEventListener('online',()=>{if(!db)connect()});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&!sheet&&!db)connect()});

'''
s=s[:a]+NEW2+s[b:]
s=rep("let db=null; const queue={}, busy={};","let db=false; const queue={}, busy={};",s)
assert 'window.claude' not in s
s=rep("function savePlayer(id){ls.set('bd.players',S.players);dbWrite('players/'+id,S.players[id])}","function savePlayer(id,op){ls.set('bd.players',S.players);dbWrite('players/'+id,S.players[id],op)}",s)
s=rep("{id:draft.id,name:n,photo:draft.photo,win:'',lose:'',hidden:false}","{id:draft.id,name:(unlocked||draft.isNew)?n:(old.name||n),photo:draft.photo,win:'',lose:'',hidden:false}",s)
s=rep("savePlayer(draft.id);if(draft.isNew&&view==='pick')","savePlayer(draft.id,draft.isNew?'addPlayer':'photo');if(draft.isNew&&view==='pick')",s)
s=rep("""data-input="pName" autocomplete="off"></div>'+""","""data-input="pName" autocomplete="off"'+(unlocked||d.isNew?'':' readonly')+'></div>'+""",s)
s=rep("""(d.isNew?'':'<button class="btn danger block" data-a="delPlayer" data-confirm="1">ลบผู้เล่นคนนี้</button>'))}""","""(d.isNew?'':(unlocked?'<button class="btn danger block" data-a="delPlayer" data-confirm="1">ลบผู้เล่นคนนี้</button>':'<p class="small muted">เปลี่ยนรูปได้เลย ส่วนการแก้ชื่อหรือลบผู้เล่นต้องใช้รหัสก๊วน</p>')))}""",s)
s=rep("(S.days[k]||(S.days[k]={matches:[]})).matches.push(m);saveDay(k);","(S.days[k]||(S.days[k]={matches:[]})).matches.push(m);ls.set('bd.days',S.days);dbWrite('days/'+k,m,'addMatch');",s)
# ---------- edit lock ----------
s=rep("  const el=e.target.closest('[data-a]');if(!el||el.disabled)return;",
"""  const el=e.target.closest('[data-a]');if(!el||el.disabled)return;
  if(!unlocked&&ADMIN.has(el.dataset.a)){pendingA=el.dataset.a;e.preventDefault();codeMode='enter';codeErr='';codeAlt=false;openSheet('code');focusCode();return}""",s)
s=rep("const armed=new WeakMap();","const armed=new WeakMap();\nconst ADMIN=new Set(['delMatch','delRound','wipeAll','delPlayer','setCode','openReset']);let pendingA='';",s)
s=rep("  if(k==='photo'&&draft&&t.files&&t.files[0])","""  if(k==='import'&&t.files&&t.files[0]){if(!unlocked){codeMode='enter';codeErr='';codeAlt=false;openSheet('code');focusCode();return}
    try{importData(JSON.parse(await t.files[0].text()))}catch(err){toast('ไฟล์นี้อ่านไม่ได้ ต้องเป็นไฟล์สำรองของแอปนี้')}t.value=''}
  if(k==='photo'&&draft&&t.files&&t.files[0])""",s)
s=rep("({player:shPlayer,finish:shFinish,next:shNext,swap:shSwap,pair:shPair}[sheet])()","({player:shPlayer,finish:shFinish,next:shNext,swap:shSwap,pair:shPair,code:shCode}[sheet])()",s)
s=rep("function shSwap(){", r'''let codeMode='enter',codeErr='',codeAlt=false;
const lockLeft=()=>Math.max(0,Math.ceil(((+ls.get('bd.lock')||0)-Date.now())/1000));
const mmss=n=>Math.floor(n/60)+':'+String(n%60).padStart(2,'0');
setInterval(()=>{const el=$('#lockT');if(!el)return;const n=lockLeft();if(n>0)el.textContent=mmss(n);else{codeErr='';renderSheet();focusCode()}},1000);
function focusCode(){const i=$('#codeIn');if(i){try{i.focus()}catch(e){}}}
function otpPaint(){const i=$('#codeIn'),w=$('#otp');if(!i||!w)return;const v=i.value;w.querySelectorAll('.bx').forEach((b,k)=>{b.textContent=v[k]||'';b.classList.toggle('fill',k<v.length);b.classList.toggle('on',k===Math.min(v.length,3)&&document.activeElement===i)})}
function shCode(){const set=codeMode==='set',otp=!codeAlt,lk=set?0:lockLeft(),dis=lk?' disabled':'';
  const intro='<p class="small muted otp-intro">'+(set?'รหัสนี้ใช้ปลดล็อกการแก้ไขและลบข้อมูลเก่าในแต่ละเครื่อง บอกเฉพาะคนที่ดูแลข้อมูล':'แก้ไขหรือลบข้อมูลจำเป็นต้องกรอกรหัสก่อน (ใส่แค่ครั้งเดียว)')+'</p>';
  const field=otp?'<div class="otp-wrap"><div class="otp-label">'+(set?'ตั้งรหัสใหม่ 4 หลัก':'ระบุรหัสก๊วน')+'</div>'+
      '<div class="otp'+(lk?' locked':codeErr?' err':'')+'" id="otp"><span class="bx"></span><span class="bx"></span><span class="bx"></span><span class="bx"></span>'+
      '<input id="codeIn" data-otp="1" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="4" autocomplete="off" aria-label="'+(set?'รหัสใหม่ 4 หลัก':'รหัสก๊วน 4 หลัก')+'"'+dis+'></div>'+
      '<div class="otp-msg'+(codeErr||lk?' bad':'')+'">'+(lk?'กรอกผิดครบ 5 ครั้ง · ลองใหม่ได้ใน <b class="num" id="lockT">'+mmss(lk)+'</b>':codeErr?esc(codeErr):(set?'ใช้ตัวเลข 4 ตัว':'กรอกครบ 4 หลักแล้วระบบตรวจให้ทันที'))+'</div></div>'
    :'<div class="field"><label class="label" for="codeIn">'+(set?'รหัสใหม่':'รหัสก๊วน')+'</label><input type="text" id="codeIn" maxlength="40" autocomplete="off" autocapitalize="off" spellcheck="false"'+dis+'></div>'+(lk?'<div class="otp-msg bad">กรอกผิดครบ 5 ครั้ง · ลองใหม่ได้ใน <b class="num" id="lockT">'+mmss(lk)+'</b></div>':codeErr?'<div class="small" style="color:var(--lose)">'+esc(codeErr)+'</div>':'');
  const alt='<button class="lnk" data-a="codeText">'+(otp?(set?'อยากตั้งรหัสเป็นข้อความ (ตัวอักษรปนตัวเลข)? พิมพ์แบบข้อความ':'รหัสไม่ใช่ตัวเลข 4 หลัก? พิมพ์รหัสแบบข้อความ'):'กลับไปกรอกแบบ 4 หลัก')+'</button>';
  return sh(set?(hasCode?'เปลี่ยนรหัสก๊วน':'ตั้งรหัสก๊วน'):'ใส่รหัสก๊วน',intro+field+alt,
    (set||!otp)?'<button class="btn pri block" data-a="submitCode"'+dis+'>'+(set?'บันทึกรหัส':'ปลดล็อก')+'</button>':'')}
document.addEventListener('input',e=>{const t=e.target;if(t.id!=='codeIn'||!t.dataset.otp)return;t.value=t.value.replace(/\D/g,'').slice(0,4);const w=$('#otp');if(w)w.classList.remove('err');otpPaint();
  if(t.value.length===4&&codeMode==='enter')A.submitCode()});
document.addEventListener('focusin',e=>{if(e.target.id==='codeIn')otpPaint()});document.addEventListener('focusout',e=>{if(e.target.id==='codeIn')otpPaint()});
function importData(obj){if(!obj||typeof obj!=='object'||(!obj.players&&!obj.days))throw new Error('bad');let np=0,nm=0;
  for(const id in obj.players||{}){const p=obj.players[id];if(!p||!p.name)continue;S.players[id]=Object.assign({},p,{id});savePlayer(id);np++}
  for(const k in obj.days||{}){if(!/^\d{4}-\d{2}-\d{2}$/.test(k))continue;const cur=S.days[k]||(S.days[k]={matches:[],gone:[]}),have=new Set(cur.matches.map(m=>m.id));
    (obj.days[k].matches||[]).forEach(m=>{if(m&&m.id&&!have.has(m.id)&&!(cur.gone||[]).includes(m.id)){cur.matches.push(m);nm++}});cur.matches.sort((a,b)=>a.t-b.t);saveDay(k)}
  toast('นำเข้าแล้ว: ผู้เล่น '+np+' คน · match ใหม่ '+nm+' รายการ');render()}
function shSwap(){''',s)
s=rep("  openReset(){", r'''  openCode(){codeMode='enter';codeErr='';codeAlt=false;openSheet('code');focusCode()},
  setCode(){codeMode='set';codeErr='';codeAlt=false;openSheet('code');focusCode()},
  codeText(){codeAlt=!codeAlt;codeErr='';renderSheet();focusCode()},
  syncTap(){if(syncMode==='offline'||syncMode==='err'){setSync('wait');connect()}},
  async submitCode(){const v=($('#codeIn').value||'').trim();if(!db){codeErr='ตอนนี้ออฟไลน์อยู่ ต่ออินเทอร์เน็ตแล้วลองใหม่';renderSheet();focusCode();return}
    try{if(codeMode==='set'){if(codeAlt?v.length<4:!/^\d{4}$/.test(v)){codeErr=codeAlt?'ตั้งรหัสอย่างน้อย 4 ตัว':'รหัสต้องเป็นตัวเลข 4 หลัก';renderSheet();focusCode();return}
        await rpc('bd_set_code',{p_old:code,p_new:v});code=v;hasCode=true;unlocked=true;ls.set('bd.code',v);ls.set('bd.ok',1);setSync('cloud');toast('ตั้งรหัสก๊วนแล้ว');closeSheet()}
      else{if(lockLeft()>0){renderSheet();return}if(!v)return;const r=await rpc('bd_check2',{p_code:v,p_dev:devId()});
        if(!r||!r.ok){if(r&&r.wait>0){ls.set('bd.lock',Date.now()+r.wait*1000);codeErr=''}else codeErr='รหัสไม่ถูกต้อง'+(r&&r.left>0?' · เหลืออีก '+r.left+' ครั้ง':'');renderSheet();focusCode();return}
        ls.set('bd.lock',0);
        code=v;unlocked=true;ls.set('bd.code',v);ls.set('bd.ok',1);setSync('cloud');toast('ปลดล็อกแล้ว เครื่องนี้แก้ไขและลบข้อมูลได้');closeSheet();if(pendingA==='openReset')A.openReset();pendingA=''}}
    catch(e){codeErr=e.pg==='28P01'?'รหัสเดิมในเครื่องนี้ไม่ถูกต้อง ปิดแล้วใส่รหัสก๊วนก่อน':'ทำรายการไม่สำเร็จ ลองใหม่';renderSheet();focusCode()}},
  exportData(){const blob=new Blob([JSON.stringify({app:'sundaybadminton',exported:new Date().toISOString(),players:S.players,days:S.days})],{type:'application/json'}),a=document.createElement('a');
    a.href=URL.createObjectURL(blob);a.download='sundaybadminton-backup-'+dayKey()+'.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);toast('บันทึกไฟล์สำรองแล้ว')},
  openReset(){''',s)
# ---------- UI: sync chip tappable, settings panel, code banner ----------
s=rep('<div class="sync" id="sync"><i></i><span>กำลังเชื่อมต่อ…</span></div>','<button class="sync" id="sync" data-a="syncTap"><i></i><span>กำลังเชื่อมต่อ…</span></button>',s)
s=rep(".sync{font-size:12px;",".sync{background:none;border:0;padding:6px 0;cursor:pointer;font-family:inherit;font-size:12px;",s)
s=rep("""const rsB='<button class="btn sm mini" data-a="openReset">รีเซ็ตข้อมูล</button>';""",
"""const rsB='<button class="btn sm mini" data-a="openReset">ตั้งค่า · รีเซ็ตข้อมูล</button>';
  const lockB=db&&!hasCode?'<button class="btn sm danger" data-a="setCode">ยังไม่ได้ตั้งรหัสก๊วน · ตั้งเลย</button>':(db&&!unlocked?'<button class="btn sm mini" data-a="openCode">ใส่รหัสก๊วน</button>':'');""",s)
s=rep("""acts:go+'<div class="tabs">'+sumB+plB+'</div>'+bdB+rsB};""","""acts:go+'<div class="tabs">'+sumB+plB+'</div>'+bdB+(lockB?'<div class="tabs">'+lockB+rsB+'</div>':rsB)};""",s)
s=rep("""bdB+'<div class="foot">'+rsB+'</div>'}}""","""bdB+'<div class="foot">'+lockB+rsB+'</div>'}}""",s)
tools="""'<button class="btn sm" data-a="setCode">'+(hasCode?'เปลี่ยนรหัสก๊วน':'ตั้งรหัสก๊วน')+'</button><button class="btn sm" data-a="exportData">สำรองข้อมูล</button><label class="btn sm">นำเข้าข้อมูล<input type="file" accept="application/json,.json" data-change="import" id="impFile" style="position:absolute;opacity:0;width:1px;height:1px"></label>'"""
s=rep("""    '<section class="panel stack"><h2>ลบทั้งหมด</h2>""","""    '<section class="panel stack"><h2>รหัสก๊วนและข้อมูลสำรอง</h2><p class="small muted">'+(hasCode?'ตั้งรหัสก๊วนแล้ว การลบหรือแก้ไขข้อมูลเก่าและ profile ผู้เล่นต้องใช้รหัส':'ยังไม่ได้ตั้งรหัสก๊วน ตอนนี้ใครมีลิงก์ก็ลบและแก้ไขข้อมูลได้ทั้งหมด')+'</p><div class="row">'+"""+tools+"""+'</div></section>'+
    '<section class="panel stack"><h2>ลบทั้งหมด</h2>""",s)
s=rep("""acts:'<div class="small muted">'+note+'</div>'+(pages>1?""","""acts:'<div class="tabs3">'+"""+tools+"""+'</div>'+(pages>1?""",s)
s=rep("/* ---------- side rail + fit-to-screen","/* the code sheet opens from the top so the phone keyboard never covers the boxes */\n@media not ((orientation:landscape) and (max-height:560px)){.veil:has(#codeIn){align-items:flex-start}\n.veil:has(#codeIn) .sheet{border-radius:0 0 20px 20px;padding:calc(env(safe-area-inset-top,0px) + 16px) 16px 18px;max-height:60%}}\n.otp-intro{text-align:center;margin:0}\n.otp-wrap{display:flex;flex-direction:column;align-items:center;gap:10px;padding:10px 0 4px}\n.otp-label{font-family:var(--f-display);font-weight:700;font-size:17px}\n.otp{position:relative;display:flex;gap:12px}\n.otp .bx{width:58px;height:68px;border:2px solid var(--line);border-radius:14px;background:var(--surface);display:grid;place-items:center;font-family:var(--f-display);font-weight:700;font-size:30px;color:var(--ink);transition:border-color .12s,box-shadow .12s}\n.otp .bx.fill{border-color:var(--court);background:color-mix(in srgb,var(--ticket) 75%,var(--surface))}\n.otp .bx.on{border-color:var(--court);box-shadow:0 0 0 4px color-mix(in srgb,var(--court) 22%,transparent)}\n.otp.locked .bx{background:var(--ground);border-style:dashed;opacity:.7}\n.otp.err .bx{border-color:var(--lose);animation:otpx .32s}\n@keyframes otpx{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}\n.otp input{position:absolute;inset:0;width:100%;height:100%;opacity:0;font-size:16px;border:0;padding:0;margin:0;cursor:pointer}\n.otp-msg{font-size:12px;color:var(--muted);min-height:16px}.otp-msg.bad{color:var(--lose);font-weight:600}\n.lnk{background:none;border:0;padding:6px;font:inherit;font-size:12px;color:var(--muted);text-decoration:underline;cursor:pointer;align-self:center}\n.sync.cloud i{background:#74f93b;box-shadow:0 0 6px 2px #74f93b;animation:pulse 1.6s ease-in-out infinite}\n@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 8px 3px #74f93b}50%{opacity:.35;box-shadow:0 0 2px 0 #74f93b}}\n.foot{gap:8px;flex-wrap:nowrap}\n.foot .btn{white-space:nowrap;min-width:0}\n.tabs .btn.mini{min-height:32px;font-size:12px;padding:2px 4px}\n.tabs3{display:grid;grid-template-columns:1fr;gap:4px}\n.tabs3 .btn{min-height:32px;font-size:12px;padding:2px 4px}\nlabel.btn{cursor:pointer;position:relative}\n/* ---------- side rail + fit-to-screen",s)
s=rep("<title>จับคู่ก๊วนแบด</title>","<title>Sunday Badminton</title>",s)
s=s.replace('<div class="name">จับคู่ก๊วนแบด</div>','<div class="name">Sunday Badminton</div>')
# ---------- wrap as a standalone document ----------
i=s.index('<header class="bar">')
head,body=s[:i],s[i:]
doc='''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sunday Badminton">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#0F6B55">
<link rel="apple-touch-icon" href="icon.png?v=2">
<link rel="icon" type="image/png" href="icon.png?v=2">
<style>html{-webkit-text-size-adjust:100%}:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}</style>
'''+head+'</head>\n<body>\n'+body+'\n</body>\n</html>\n'
import time
BUILD=str(int(time.time()))
upd="""<script>
/* pick up a newer deploy even when the phone has an older copy cached */
(function(){var B='__BUILD__';fetch('index.html?_='+Date.now(),{cache:'no-store'}).then(function(r){return r.text()}).then(function(t){var m=t.match(/var B='([0-9]+)'/);if(m&&+m[1]>+B&&sessionStorage.getItem('bd.upd')!==m[1]){sessionStorage.setItem('bd.upd',m[1]);location.replace(location.pathname+'?v='+m[1])}}).catch(function(){})})();
</script>""".replace('__BUILD__',BUILD)
doc=doc.replace('\n</body>',upd+'\n</body>')
open(os.path.join(ROOT,'index.html'),'w').write(doc)
open('/tmp/site.js','w').write(re.search(r'<script>(.*?)</script>',doc,re.S).group(1))
print('built',len(doc))
