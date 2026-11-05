/* Armazenamento local (IndexedDB) com sincronização opcional com uma planilha do Google (via Apps Script).
   Expõe a mesma interface do banco usado dentro do Claude: db.collection(nome).doc(id).set/update/delete, add, onSnapshot. */
window.CJN=true;
(function(){
  const COLS=['imoveis','locadores','locatarios','contratos','pagamentos'];
  const FIELDS={
    imoveis:['codigo','endereco','bairro','tipo','aluguel','status','foto'],
    locadores:['nome','doc','pix','assinatura'],
    locatarios:['nome','cpf','telefone','email','profissao'],
    contratos:['numero','imovelId','locadorId','locatarioId','entrada','saida','valor','status','pdf'],
    pagamentos:['contratoId','referencia','valor','vencimento','dataPagamento','forma']};
  const TYPES={imoveis:{aluguel:'n'},contratos:{entrada:'d',saida:'d',valor:'n'},
    pagamentos:{valor:'n',vencimento:'d',dataPagamento:'d',referencia:'m'},locadores:{doc:'c'},locatarios:{cpf:'c'}};
  const SEED=__SEED__;

  /* ---------- conversões (a planilha pode devolver números, datas ou textos) ---------- */
  const str=v=>v==null?'':String(v).trim();
  const num=v=>{if(typeof v==='number')return v;let t=str(v).replace(/[R$\s]/g,'');if(t.includes(','))t=t.replace(/\./g,'').replace(',','.');const x=parseFloat(t);return isNaN(x)?0:x};
  const toIso=v=>{const t=str(v);if(!t)return '';let m=t.match(/^(\d{4})-(\d{2})-(\d{2})/);if(m)return m[1]+'-'+m[2]+'-'+m[3];
    m=t.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);if(m)return (m[3].length===2?'20'+m[3]:m[3])+'-'+m[2].padStart(2,'0')+'-'+m[1].padStart(2,'0');return ''};
  const toYm=v=>{const t=str(v);let m=t.match(/^(\d{4})-(\d{2})/);if(m)return m[1]+'-'+m[2];m=t.match(/^(\d{1,2})\/(\d{4})$/);if(m)return m[2]+'-'+m[1].padStart(2,'0');return toIso(t).slice(0,7)};
  const toDoc=v=>{const t=str(v).replace(/\D/g,'');return t?(t.length<=11?t.padStart(11,'0'):t):str(v)};
  function norm(c,r){const ty=TYPES[c]||{},o={};for(const k of FIELDS[c]){const v=r[k]??'',t=ty[k];
    o[k]=t==='n'?num(v):t==='d'?toIso(v):t==='m'?toYm(v):t==='c'?toDoc(v):str(v)}return o}
  const js=o=>JSON.stringify(o,Object.keys(o).sort());
  const same=(a,b)=>a.size===b.size&&[...a].every(([k,v])=>b.has(k)&&js(b.get(k))===js(v));

  /* ---------- IndexedDB ---------- */
  const mem={},subs={};let idb=null,ready;
  COLS.forEach(c=>{mem[c]=new Map();subs[c]=new Set()});
  const open=()=>new Promise((res,rej)=>{const r=indexedDB.open('cjnproperty',1);
    r.onupgradeneeded=()=>{[...COLS,'meta'].forEach(n=>r.result.createObjectStore(n))};
    r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)});
  const done=t=>new Promise((res,rej)=>{t.oncomplete=()=>res();t.onerror=()=>rej(t.error);t.onabort=()=>rej(t.error)});
  const put=(c,id,d)=>{if(!idb)return Promise.resolve();const t=idb.transaction(c,'readwrite');t.objectStore(c).put(d,id);return done(t)};
  const del=(c,id)=>{if(!idb)return Promise.resolve();const t=idb.transaction(c,'readwrite');t.objectStore(c).delete(id);return done(t)};
  const loadAll=c=>new Promise((res,rej)=>{const out=new Map(),q=idb.transaction(c).objectStore(c).openCursor();
    q.onsuccess=()=>{const cur=q.result;if(cur){out.set(cur.key,cur.value);cur.continue()}else res(out)};q.onerror=()=>rej(q.error)});
  const metaGet=k=>new Promise(r=>{if(!idb)return r(undefined);const q=idb.transaction('meta').objectStore('meta').get(k);q.onsuccess=()=>r(q.result);q.onerror=()=>r(undefined)});
  const metaPut=(k,v)=>{if(!idb)return Promise.resolve();const t=idb.transaction('meta','readwrite');v==null?t.objectStore('meta').delete(k):t.objectStore('meta').put(v,k);return done(t)};

  /* ---------- estado da sincronização ---------- */
  let cfg=null,queue=[],state='local',lastSync=null,errMsg='',flushing=false,pulling=false;
  const hh=d=>d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  const stText=()=>({local:'Dados só neste aparelho',sync:'Sincronizando…',ok:'Sincronizado'+(lastSync?' às '+hh(lastSync):''),
    pending:queue.length+' alteração(ões) para enviar',offline:'Sem conexão. Envio depois.',error:'Erro: '+errMsg})[state]||'';
  function setState(s){state=s||(!cfg?'local':queue.length?'pending':'ok');
    const el=document.querySelector('.foot .fst');if(el){el.textContent=stText();el.classList.toggle('bad',state==='error')}}
  const fail=e=>{errMsg=e.message||String(e);setState(navigator.onLine?'error':'offline');
    if(cfg&&cfg.login&&/Sessão|Entre com|Entre de novo|Usuário sem acesso/.test(errMsg)){if(sess)sess.exp=0;gateShow(errMsg)}};

  const snap=c=>({docs:[...mem[c]].map(([id,d])=>({id,exists:true,data:()=>d})),size:mem[c].size,empty:!mem[c].size});
  const notify=c=>subs[c].forEach(f=>f(snap(c)));
  const rnd=()=>Math.random().toString(36).slice(2,12);

  function enqueue(op){
    if(!cfg)return;
    queue=queue.filter(o=>!(o.col===op.col&&o.id===op.id));queue.push(op);
    metaPut('queue',queue);setState();setTimeout(flush,400);
  }

  /* ---------- banco local ---------- */
  const docRef=(c,id)=>({id,
    async set(d){await ready;const n={...d};mem[c].set(id,n);await put(c,id,n);notify(c);enqueue({op:'set',col:c,id,data:n})},
    async update(d){await ready;const n={...(mem[c].get(id)||{}),...d};mem[c].set(id,n);await put(c,id,n);notify(c);enqueue({op:'set',col:c,id,data:n})},
    async delete(){await ready;mem[c].delete(id);await del(c,id);notify(c);enqueue({op:'delete',col:c,id})}});
  const colRef=c=>({doc:id=>docRef(c,id||rnd()),
    async add(d){const id=rnd();await docRef(c,id).set(d);return docRef(c,id)},
    onSnapshot(next){const f=s=>next(s);subs[c].add(f);ready.then(()=>f(snap(c)));return()=>subs[c].delete(f)}});
  const dbApi={collection:colRef,doc:p=>{const[c,id]=p.split('/');return docRef(c,id)}};
  /* Envio de arquivos: a planilha guarda no máximo ~50 mil caracteres por célula, então a foto é reduzida (JPEG) até caber. */
  const MAXC=46000;
  const readDU=f=>new Promise((ok,no)=>{const r=new FileReader();r.onload=()=>ok(r.result);r.onerror=()=>no(new Error('Não foi possível ler o arquivo'));r.readAsDataURL(f)});
  const loadImg=u=>new Promise((ok,no)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>no(new Error('Imagem inválida'));i.src=u});
  const assetsApi={async upload(f){
    if(/^image\//.test(f.type)){
      const img=await loadImg(await readDU(f));
      for(const mx of [720,600,480,400,320,260,200]){
        const k=Math.min(1,mx/Math.max(img.width,img.height)),c=document.createElement('canvas');
        c.width=Math.max(1,Math.round(img.width*k));c.height=Math.max(1,Math.round(img.height*k));
        const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);g.drawImage(img,0,0,c.width,c.height);
        for(const q of [.78,.66,.55,.45,.35]){const u=c.toDataURL('image/jpeg',q);if(u.length<=MAXC)return {url:u}}
      }
      throw new Error('Não foi possível reduzir a foto o bastante');
    }
    const u=await readDU(f);
    if(u.length<=MAXC)return {url:u};
    throw new Error('PDF grande demais para a planilha (máx. ~30 KB). Use um PDF menor ou o app do Claude.');
  }};
  window.claude={use:async n=>n==='db'?(await ready,dbApi):n==='assets'?assetsApi:null};


  /* ---------- login com usuário e senha (verificado no Apps Script) ---------- */
  const SK='cjn_sess',GK='cjn_gate';
  const lsGet=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
  const lsSet=(k,v)=>{try{v==null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}};
  let sess=null,gateEl=null;
  try{sess=JSON.parse(lsGet(SK)||'null')}catch(e){sess=null}
  const gateOn=()=>lsGet(GK)==='1';
  const validSess=()=>!!(sess&&sess.session&&sess.exp*1000>Date.now()+30000);
  const redraw=()=>{try{render()}catch(e){}};
  async function rawPost(url,body){
    const ctl=new AbortController(),t=setTimeout(()=>ctl.abort(),30000);
    try{
      const r=await fetch(url,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(body),redirect:'follow',signal:ctl.signal});
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Erro na planilha');
      return j;
    }catch(e){
      if(e.name==='AbortError')throw new Error('A planilha demorou para responder');
      if(e instanceof SyntaxError)throw new Error('Resposta inválida. Na implantação, deixe o acesso como "Qualquer pessoa".');
      if(e instanceof TypeError)throw new Error('Sem conexão ou endereço incorreto');
      throw e;
    }finally{clearTimeout(t)}
  }
  async function doLogin(url,user,pass){
    const j=await rawPost(url,{action:'login',user,pass});
    sess={session:j.session,user:j.user,exp:j.exp,at:Date.now()};lsSet(SK,JSON.stringify(sess));return sess;
  }
  function gateHide(){if(gateEl){gateEl.remove();gateEl=null}}
  function gateShow(msg){
    if(gateEl){const e=gateEl.querySelector('#gateErr');if(e&&msg&&!e.textContent)e.textContent=msg;return}
    const d=document.createElement('div');d.id='gate';
    d.style.cssText='position:fixed;inset:0;z-index:2000;background:var(--bg,#f4f6fa);color:var(--ink,#101a2e);display:grid;place-items:center;padding:24px;font:14px/1.5 var(--f-body,system-ui,sans-serif);overflow:auto';
    const inp='width:100%;font:inherit;padding:10px 12px;border:1px solid var(--line,#dbe1ec);border-radius:6px;background:var(--surface,#fff);color:inherit;box-sizing:border-box';
    d.innerHTML=`<form id="gateF" style="max-width:340px;width:100%;display:flex;flex-direction:column;gap:12px;text-align:center;align-items:stretch"><img src="icon-192.png" alt="" width="72" height="72" style="border-radius:16px;align-self:center"><h1 style="margin:0;font:700 26px var(--f-display,system-ui)">CJNProperty</h1><p style="margin:0;color:var(--muted,#5d6a82)">Entre com seu usuário e senha.</p>
      <input id="gUser" type="text" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="Usuário" required style="${inp}">
      <input id="gPass" type="password" autocomplete="current-password" placeholder="Senha" required style="${inp}">
      <button id="gGo" style="all:unset;cursor:pointer;background:var(--accent,#043C95);color:var(--accent-ink,#fff);padding:11px 14px;border-radius:6px;font-weight:600;text-align:center">Entrar</button>
      <p id="gateErr" style="margin:0;color:var(--bad,#b3261e);min-height:20px"></p><div id="gateExtra"></div></form>`;
    document.documentElement.appendChild(d);gateEl=d;
    const err=d.querySelector('#gateErr');err.textContent=msg||'';
    const u=d.querySelector('#gUser');if(sess&&sess.user)u.value=sess.user;
    (u.value?d.querySelector('#gPass'):u).focus();
    if(!navigator.onLine&&sess&&sess.at&&Date.now()-sess.at<30*864e5){
      const b=document.createElement('button');b.type='button';b.textContent='Continuar sem conexão';b.onclick=()=>gateHide();
      b.style.cssText='all:unset;cursor:pointer;border:1px solid var(--line,#dbe1ec);border-radius:6px;padding:8px 14px;font-weight:600';
      d.querySelector('#gateExtra').appendChild(b)}
    d.querySelector('#gateF').onsubmit=async e=>{
      e.preventDefault();
      const btn=d.querySelector('#gGo'),user=u.value.trim(),pass=d.querySelector('#gPass').value;
      btn.textContent='Entrando…';err.textContent='';
      try{
        await ready;
        if(!cfg||!cfg.url){lsSet(GK,null);gateHide();return}
        await doLogin(cfg.url,user,pass);
        await call({action:'ping'});
        gateHide();redraw();setState();syncNow();
      }catch(ex){btn.textContent='Entrar';err.textContent=ex.message||'Não foi possível entrar';d.querySelector('#gPass').value='';d.querySelector('#gPass').focus()}
    };
  }
  function logout(){sess=null;lsSet(SK,null);gateShow();redraw()}
  if(gateOn()&&!validSess())gateShow();

  /* ---------- planilha Google (Apps Script) ---------- */
  async function call(body){
    if(cfg.login&&!validSess()){gateShow('Sessão expirada. Entre novamente.');throw new Error('Sessão expirada. Entre novamente.')}
    return rawPost(cfg.url,{token:cfg.login?undefined:cfg.token,session:cfg.login?sess.session:undefined,...body});
  }
  async function flush(){
    if(!cfg||flushing||!queue.length)return;
    flushing=true;setState('sync');const batch=queue.slice();
    try{
      await call({action:'ops',ops:batch});
      queue=queue.filter(o=>!batch.includes(o));await metaPut('queue',queue);
      lastSync=new Date();errMsg='';setState();
    }catch(e){fail(e)}
    flushing=false;
  }
  async function pull(){
    if(!cfg||pulling||flushing||queue.length)return;
    pulling=true;setState('sync');
    try{
      const {data}=await call({action:'list'});
      const total=COLS.reduce((n,c)=>n+(data[c]||[]).length,0);
      if(!total&&COLS.some(c=>mem[c].size)){          /* planilha vazia: envia o que está no aparelho */
        COLS.forEach(c=>mem[c].forEach((d,id)=>queue.push({op:'set',col:c,id,data:d})));
        await metaPut('queue',queue);pulling=false;return flush();
      }
      for(const c of COLS){
        const nm=new Map();(data[c]||[]).forEach(r=>{const{id,...rest}=r;nm.set(String(id),norm(c,rest))});
        if(!same(mem[c],nm)){
          for(const id of [...mem[c].keys()])if(!nm.has(id))await del(c,id);
          for(const [id,d] of nm)await put(c,id,d);
          mem[c]=nm;notify(c);
        }
      }
      lastSync=new Date();errMsg='';setState();
    }catch(e){fail(e)}
    pulling=false;
  }
  const syncNow=async()=>{await flush();await pull()};

  function openCfg(){
    const layer=document.getElementById('layer');
    layer.innerHTML=`<div class="modal"><form id="cfgf"><h2>Planilha Google</h2>
      <p class="full sub">Cole o endereço do aplicativo web (termina em /exec) e entre com o usuário e a senha criados no Apps Script. Ficam guardados só neste aparelho. Ao conectar, os dados da planilha substituem os deste aparelho.</p>
      <label class="full">Endereço do aplicativo web<input id="cfgUrl" type="url" required value="${esc(cfg?.url||'')}" placeholder="https://script.google.com/macros/s/…/exec"></label>
      <label>Usuário<input id="cfgUser" type="text" autocomplete="username" autocapitalize="none" value="${esc(cfg?.login&&sess?sess.user:'')}"></label>
      <label>Senha<input id="cfgPass" type="password" autocomplete="current-password"></label>
      <label class="full">Código de acesso (só se não usar usuário e senha)<input id="cfgTok" type="password" autocomplete="off" value="${esc(cfg&&!cfg.login?cfg.token||'':'')}"></label>
      <div class="acts">${cfg?'<button type="button" class="btn danger sp" id="cfgOff">Desconectar</button>':''}<button type="button" class="btn ghost" id="cfgX">Cancelar</button><button class="btn" id="cfgGo">Conectar e sincronizar</button></div></form></div>`;
    const close=()=>{layer.innerHTML=''};
    layer.querySelector('#cfgX').onclick=close;
    const off=layer.querySelector('#cfgOff');
    if(off)off.onclick=async()=>{cfg=null;queue=[];sess=null;lsSet(SK,null);lsSet(GK,null);gateHide();await metaPut('cfg',null);await metaPut('queue',null);close();setState('local');redraw();toast('Planilha desconectada')};
    layer.querySelector('#cfgf').onsubmit=async e=>{
      e.preventDefault();
      const url=layer.querySelector('#cfgUrl').value.trim(),user=layer.querySelector('#cfgUser').value.trim(),pass=layer.querySelector('#cfgPass').value,token=layer.querySelector('#cfgTok').value;
      if(!/^https:\/\/script\.google(usercontent)?\.com\//.test(url)){toast('O endereço deve começar com https://script.google.com/');return}
      const keep=cfg&&cfg.login&&validSess()&&!pass&&!token&&cfg.url===url;
      if(!keep&&!(user&&pass)&&!token){toast('Informe usuário e senha (ou o código de acesso)');return}
      const btn=layer.querySelector('#cfgGo'),old=cfg,oldSess=sess;
      btn.disabled=true;btn.textContent='Testando…';
      try{
        if(keep){cfg={...cfg,url}}
        else if(user&&pass){await doLogin(url,user,pass);cfg={url,login:true}}
        else cfg={url,token};
        await call({action:'ping'});
        await metaPut('cfg',cfg);
        if(cfg.login)lsSet(GK,'1');else{lsSet(GK,null);sess=null;lsSet(SK,null)}
        close();redraw();toast(cfg.login&&sess?'Conectado como '+sess.user:'Conectado');await syncNow();
      }catch(ex){
        cfg=old;sess=oldSess;if(!oldSess)lsSet(SK,null);else lsSet(SK,JSON.stringify(oldSess));
        btn.disabled=false;btn.textContent='Conectar e sincronizar';toast(ex.message||'Não foi possível conectar')}
    };
  }

  /* ---------- backup em arquivo ---------- */
  async function exportar(){
    await ready;const out={versao:1,exportadoEm:new Date().toISOString()};
    COLS.forEach(c=>out[c]=Object.fromEntries(mem[c]));
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out)],{type:'application/json'}));
    a.download='cjnproperty-backup-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(a);a.click();a.remove();
  }
  async function importar(file){
    try{
      const j=JSON.parse(await file.text());if(!COLS.every(c=>j[c]&&typeof j[c]==='object'))throw 0;
      for(const c of COLS){
        for(const id of [...mem[c].keys()])if(!(id in j[c])){await del(c,id);enqueue({op:'delete',col:c,id})}
        mem[c]=new Map(Object.entries(j[c]));
        for(const [id,d] of mem[c]){await put(c,id,d);enqueue({op:'set',col:c,id,data:d})}
        notify(c);
      }
      toast('Backup restaurado');
    }catch(e){toast('Arquivo de backup inválido')}
  }
  function escolherBackup(){const i=document.createElement('input');i.type='file';i.accept='application/json,.json';i.onchange=()=>{if(i.files[0])importar(i.files[0])};i.click()}

  window.footHtml=()=>`<div class="foot"><div class="fst${state==='error'?' bad':''}">${esc(stText())}</div>${cfg&&cfg.login&&sess?`<button data-sh="logout">Sair (${esc(sess.user)})</button>`:''}<button data-sh="cfg">Planilha Google</button><button data-sh="export">Exportar backup</button><button data-sh="import">Importar backup</button></div>`;
  document.addEventListener('click',e=>{
    const a=e.target.closest('[data-sh]');
    if(a){const k=a.dataset.sh;if(k==='cfg')openCfg();else if(k==='logout')logout();else if(k==='export')exportar();else escolherBackup();return}
    const l=e.target.closest('a[href^="data:"]');
    if(l){e.preventDefault();fetch(l.href).then(r=>r.blob()).then(b=>window.open(URL.createObjectURL(b),'_blank'))}
  });

  /* ---------- inicialização ---------- */
  async function init(){
    try{idb=await open()}catch(e){idb=null}
    if(idb){for(const c of COLS)mem[c]=await loadAll(c);
      const seeded=await metaGet('seeded');
      if(!seeded&&COLS.every(c=>!mem[c].size)){for(const c of COLS)for(const [id,d] of Object.entries(SEED[c])){mem[c].set(id,d);await put(c,id,d)}}
      await metaPut('seeded',true);
      cfg=(await metaGet('cfg'))||null;queue=(await metaGet('queue'))||[];
      if(cfg&&cfg.login&&!gateOn())lsSet(GK,'1');
    }
  }
  ready=init();
  ready.then(()=>{if(cfg){setState();syncNow()}});
  setInterval(()=>{if(cfg&&!document.hidden)syncNow()},60000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&cfg)syncNow()});
  window.addEventListener('online',()=>{if(cfg)syncNow()});
  if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));
})();
