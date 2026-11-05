import re,sys
CSS='''.rwrap{width:100%;max-width:720px;max-height:100%;overflow:auto;display:flex;flex-direction:column;gap:12px}
.recibo{background:#fff;color:#14182c;border-radius:6px;padding:32px 36px;font-family:var(--f-body);line-height:1.6;border-top:6px solid #043C95;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.recibo header{display:flex;align-items:center;gap:16px;border-bottom:1px solid #d9deea;padding-bottom:16px;margin-bottom:18px}
.recibo header img{height:56px;width:auto;display:block}
.recibo h3{margin:0;font:700 20px var(--f-display);color:#043C95;letter-spacing:.02em}
.recibo .rn{font:500 12px var(--f-mono);color:#5d6a82}
.recibo .rv{margin-left:auto;font:600 22px var(--f-mono);color:#043C95;white-space:nowrap}
.recibo p{margin:0 0 14px}
.recibo dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:18px 0;padding:12px 14px;background:#f1f4fa;border-radius:6px}
.recibo dt{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#5d6a82}
.recibo dd{margin:0;font:500 14px var(--f-mono)}
.recibo .ass{margin-top:46px;text-align:center;display:flex;flex-direction:column;gap:2px;align-items:center}
.recibo .ass .ln{width:min(320px,80%);border-top:1px solid #14182c;margin-bottom:6px}
.recibo .ass span{font-size:12px;color:#5d6a82}
.recibo .ass .sig{height:56px;max-width:240px;object-fit:contain;margin:-40px 0 -16px;position:relative;z-index:1}
.sigbox{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.sigbox .pv{min-width:160px;height:64px;border:1px dashed var(--line);border-radius:6px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;color:#5d6a82}.sigbox .pv img{max-height:60px;max-width:220px}
.recibo.via2{display:none}
.rwrap[data-vias=lt] .recibo:not(.via2){display:none!important}
.rwrap[data-vias=lt] .recibo.via2{display:block!important;margin-top:0!important}
.rwrap[data-vias=lt] .recibo.via2::before{display:none}
.rwrap[data-vias=loc] .recibo.via2{display:none!important}
.recibo footer{margin-top:28px;font-size:11px;color:#5d6a82;text-align:center}
.rwrap .racts{display:flex;gap:8px;flex-wrap:wrap;align-items:end;justify-content:space-between;background:var(--surface);padding:12px;border-radius:8px;border:1px solid var(--line)}
.rwrap .racts .bar{align-items:end}
a.btn{text-decoration:none;display:inline-block}
@media print{body{background:#fff!important;padding:0}.shell,.toast,.noprint{display:none!important}.modal{position:static;background:none;padding:0;display:block}.rwrap{max-width:none;overflow:visible}.recibo{border-radius:0;padding:10px 0 0;font-size:12px;line-height:1.45;break-inside:avoid}.recibo header{padding-bottom:10px;margin-bottom:10px}.recibo header img{height:40px}.recibo dl{margin:10px 0;padding:8px 12px}.recibo .ass{margin-top:30px}.recibo .ass .sig{height:44px;margin:-26px 0 -12px}.recibo footer{margin-top:14px}.recibo.via2{display:block;margin-top:26px;position:relative}.recibo.via2::before{content:'';position:absolute;top:-14px;left:0;right:0;border-top:1px dashed #888}}
@media (max-width:760px){.recibo{padding:20px 16px}.recibo header{flex-wrap:wrap}.recibo .rv{margin-left:0;width:100%}}
'''
JS=r'''
/* ---------- recibos ---------- */
function extenso(v){
  const un=['zero','um','dois','três','quatro','cinco','seis','sete','oito','nove','dez','onze','doze','treze','quatorze','quinze','dezesseis','dezessete','dezoito','dezenove'];
  const dz=['','','vinte','trinta','quarenta','cinquenta','sessenta','setenta','oitenta','noventa'];
  const ce=['','cento','duzentos','trezentos','quatrocentos','quinhentos','seiscentos','setecentos','oitocentos','novecentos'];
  const a999=n=>{if(n===100)return 'cem';const c=Math.floor(n/100),r=n%100,p=[];if(c)p.push(ce[c]);
    if(r){if(r<20)p.push(un[r]);else{const d=Math.floor(r/10),u=r%10;p.push(u?dz[d]+' e '+un[u]:dz[d])}}return p.join(' e ')};
  const grupo=n=>{const mi=Math.floor(n/1e6),mil=Math.floor((n%1e6)/1000),r=n%1000,parts=[],vals=[];
    if(mi){parts.push(a999(mi)+(mi===1?' milhão':' milhões'));vals.push(1e6)}
    if(mil){parts.push(mil===1?'mil':a999(mil)+' mil');vals.push(1000)}
    if(r){parts.push(a999(r));vals.push(r)}
    let t=parts[0]||'';for(let i=1;i<parts.length;i++){const last=i===parts.length-1&&(vals[i]<100||vals[i]%100===0);t+=(last?' e ':', ')+parts[i]}return t};
  const total=Math.round((+v||0)*100),reais=Math.floor(total/100),cent=total%100,out=[];
  if(reais)out.push(grupo(reais)+(reais%1e6===0?' de reais':reais===1?' real':' reais'));
  if(cent)out.push(grupo(cent)+(cent===1?' centavo':' centavos'));
  return out.length?out.join(' e '):'zero real';
}
function imgSrc(u){const m=String(u||'').match(/drive\.google\.com\/file\/d\/([^/?#]+)/)||String(u||'').match(/drive\.google\.com\/(?:open|uc)\?[^#]*id=([^&#]+)/);return m?`https://drive.google.com/thumbnail?id=${m[1]}&sz=w800`:u}

function sigSet(u){const h=document.getElementById('f_assinatura'),pv=document.getElementById('sigPv');if(h)h.value=u||'';if(pv)pv.innerHTML=u?`<img src="${u}" alt="Assinatura">`:'Sem assinatura'}
async function sigLoad(inp){
  const f=inp.files&&inp.files[0];if(!f)return;
  try{
    const url=URL.createObjectURL(f),img=new Image();img.src=url;await img.decode();
    let w=img.naturalWidth,h=img.naturalHeight;
    const cv=document.createElement('canvas'),cx=cv.getContext('2d',{willReadFrequently:true});
    cv.width=w;cv.height=h;cx.drawImage(img,0,0);URL.revokeObjectURL(url);
    let d=cx.getImageData(0,0,w,h),a=d.data,opaque=true;
    for(let i=3;i<a.length;i+=4)if(a[i]<250){opaque=false;break}
    if(opaque)for(let i=0;i<a.length;i+=4)if(a[i]>235&&a[i+1]>235&&a[i+2]>235)a[i+3]=0;
    let x0=w,y0=h,x1=-1,y1=-1;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(a[(y*w+x)*4+3]>20){if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
    if(x1<0){toast('A imagem não tem assinatura visível');inp.value='';return}
    cx.putImageData(d,0,0);
    const cw=x1-x0+1,ch=y1-y0+1;
    let sc=Math.min(1,360/cw,140/ch),out='';
    for(let k=0;k<8;k++){
      const c2=document.createElement('canvas');c2.width=Math.max(1,Math.round(cw*sc));c2.height=Math.max(1,Math.round(ch*sc));
      c2.getContext('2d').drawImage(cv,x0,y0,cw,ch,0,0,c2.width,c2.height);
      out=c2.toDataURL('image/png');if(out.length<=42000)break;sc*=.75;
    }
    if(out.length>42000){toast('Imagem muito detalhada. Use uma assinatura mais simples.');inp.value='';return}
    sigSet(out);toast('Assinatura carregada. Clique em Salvar.');
  }catch(err){toast('Não foi possível ler a imagem')}
}
function reciboInfo(p){
  const c=by('contratos',p.contratoId);
  return {c,im:by('imoveis',c?.imovelId),lt:by('locatarios',c?.locatarioId),ld:by('locadores',c?.locadorId),
    num:'REC-'+String(p.referencia||'').replace('-','')+'-'+String(c?.numero||p.contratoId||'').slice(0,4).toUpperCase()};
}
function reciboTexto(p){
  const {im,lt,ld,num}=reciboInfo(p),v=+p.valor||0;
  return `Recibo ${num}\nRecebi de ${lt?.nome||'—'} a importância de ${brl(v)} (${extenso(v)}), referente ao aluguel de ${mesLabel(p.referencia)} do imóvel ${im?.endereco||'—'}.\nPago em ${dt(p.dataPagamento)}${p.forma?' via '+p.forma:''}.\n${ld?.nome||''}`;
}

/* Várias formas no mesmo pagamento: guardadas no campo "forma" como texto legível, ex.: "Pix 500,00 + Dinheiro 300,00". Uma forma só continua como "Pix". */
function formasFmt(rows){if(rows.length===1)return rows[0].n||'';return rows.map(r=>r.n+' '+(+r.v||0).toFixed(2).replace('.',',')).join(' + ')}
function formasParse(f,tot){const t=String(f||'').trim();if(!t)return [];
  if(!t.includes(' + ')&&!/\s\d[\d.]*,\d{2}$/.test(t))return [{n:t,v:tot}];
  return t.split(' + ').map(x=>{const m=x.trim().match(/^(.*?)\s+(\d[\d.]*,\d{2})$/);return m?{n:m[1],v:parseFloat(m[2].replace(/\./g,'').replace(',','.'))}:{n:x.trim(),v:0}})}
function openPagar(id){
  const p=by('pagamentos',id);if(!p)return;
  const {lt}=reciboInfo(p),layer=document.getElementById('layer');
  layer.innerHTML=`<div class="modal"><form id="payf"><h2>Registrar pagamento</h2>
    <p class="full sub">${esc(lt?.nome||'—')} · ${esc(mesLabel(p.referencia))} · ${brl(p.valor)} · vence ${dt(p.vencimento)}</p>
    <label>Data do pagamento<input id="pgData" type="date" required value="${today()}"></label>
    <div class="full" id="pgFormas"></div>
    <div class="acts"><button type="button" class="btn ghost" id="pgX">Cancelar</button><button class="btn">Registrar e ver recibo</button></div></form></div>`;
  const close=()=>layer.innerHTML='';
  const FORMAS=['Pix','Dinheiro','Transferência','Cartão','Boleto'],tot=+p.valor||0,box=layer.querySelector('#pgFormas');
  let rows=formasParse(p.forma,tot);if(!rows.length)rows=[{n:'',v:tot}];
  const drawF=()=>{const multi=rows.length>1,soma=rows.reduce((a,r)=>a+(+r.v||0),0),dif=Math.round((tot-soma)*100)/100;
    box.innerHTML=`<div style="display:flex;flex-direction:column;gap:8px"><span class="sub">Forma de pagamento</span>`+rows.map((r,i)=>`<div style="display:flex;gap:8px;align-items:center">
      <select data-fn="${i}" style="flex:1;min-width:0">${(multi?FORMAS:['',...FORMAS]).map(o=>`<option ${o===r.n?'selected':''}>${o}</option>`).join('')}</select>
      ${multi?`<input data-fv="${i}" type="number" step="0.01" min="0" value="${(+r.v||0).toFixed(2)}" style="width:120px" aria-label="Valor desta forma">
      <button type="button" class="btn ghost" data-fx="${i}" aria-label="Remover forma">×</button>`:''}</div>`).join('')
      +`<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><button type="button" class="btn ghost" id="pgAdd">+ Adicionar outra forma</button>`
      +(multi?`<span class="sub" style="color:${dif===0?'var(--ok)':'var(--bad)'}">Soma ${brl(soma)} de ${brl(tot)}${dif>0?' · faltam '+brl(dif):dif<0?' · passou '+brl(-dif):' ✓'}</span>`:'')+`</div></div>`;
    box.querySelectorAll('[data-fn]').forEach(el=>el.onchange=()=>{rows[+el.dataset.fn].n=el.value});
    box.querySelectorAll('[data-fv]').forEach(el=>el.onchange=()=>{rows[+el.dataset.fv].v=parseFloat(el.value)||0;setTimeout(drawF,0)});
    box.querySelectorAll('[data-fx]').forEach(el=>el.onclick=()=>{rows.splice(+el.dataset.fx,1);if(rows.length===1)rows[0].v=tot;drawF()});
    box.querySelector('#pgAdd').onclick=()=>{if(rows.length===1){rows[0].v=tot;rows.push({n:'Pix',v:0})}else{const rest=Math.max(0,Math.round((tot-soma)*100)/100);rows.push({n:'Pix',v:rest})}
      if(rows.length===2&&!rows[0].n)rows[0].n='Dinheiro';drawF()}};
  drawF();
  layer.querySelector('#pgX').onclick=close;
  layer.querySelector('.modal').addEventListener('mousedown',e=>{if(e.target.classList.contains('modal'))close()});
  layer.querySelector('#payf').onsubmit=async e=>{
    e.preventDefault();
    const dataPagamento=layer.querySelector('#pgData').value;
    if(!dataPagamento){toast('Informe a data do pagamento');return}
    if(rows.length>1){const soma=Math.round(rows.reduce((a,r)=>a+(+r.v||0),0)*100);if(soma!==Math.round(tot*100)){toast('A soma das formas deve ser igual ao valor do pagamento');return}
      if(rows.some(r=>!r.n||!(+r.v>0))){toast('Informe forma e valor em todas as linhas');return}}
    const forma=formasFmt(rows);
    try{await db.collection('pagamentos').doc(id).update({dataPagamento,forma});close();toast('Pagamento registrado');openRecibo(id,{dataPagamento,forma})}
    catch(err){toast('Sem permissão para alterar')}
  };
  layer.querySelector('#pgData').focus();
}

/* ---------- PDF do recibo (gerado no próprio aparelho, sem bibliotecas) ---------- */
async function reciboPdf(p,vias){
  vias=vias||RECVIAS;
  const {im,lt,ld,num}=reciboInfo(p),v=+p.valor||0;
  const img=new Image();img.src=LOGO;await img.decode();
  const iw=img.naturalWidth,ih=img.naturalHeight,cv=document.createElement('canvas');cv.width=iw;cv.height=ih;
  const cx=cv.getContext('2d');cx.fillStyle='#fff';cx.fillRect(0,0,iw,ih);cx.drawImage(img,0,0);
  const jb=atob(cv.toDataURL('image/jpeg',.92).split(',')[1]);
  const W=595.28,H=841.89,M=56,meas=document.createElement('canvas').getContext('2d');
  const enc=t=>String(t==null?'':t).replace(/[—–]/g,'-').replace(/[“”]/g,'"').replace(/[‘’]/g,"'").replace(/[^\x00-\xFF]/g,'?').replace(/([\\()])/g,'\\$1');
  const FONT={F1:'Helvetica, Arial, sans-serif',F2:'bold Helvetica, Arial, sans-serif'};
  const wid=(t,f,sz)=>{if(f==='F3'||f==='F4')return String(t).length*.6*sz;meas.font=(f==='F2'?'bold ':'')+sz+'px Helvetica, Arial, sans-serif';return meas.measureText(String(t)).width};
  const n2=x=>x.toFixed(2),col=(r,g,b)=>`${n2(r)} ${n2(g)} ${n2(b)}`;
  const BLUE=col(.016,.235,.584),INK=col(.08,.1,.17),GRAY=col(.36,.42,.51);
  let c='';
  const text=(x,top,t,f,sz,color,al)=>{const w=wid(t,f,sz);if(al==='r')x-=w;else if(al==='c')x-=w/2;
    c+=`BT /${f} ${sz} Tf ${color} rg ${n2(x)} ${n2(H-top)} Td (${enc(t)}) Tj ET\n`};
  const wrap=(t,f,sz,max)=>{const words=String(t).split(' '),lines=[];let cur='';
    for(const w of words){const x=cur?cur+' '+w:w;if(wid(x,f,sz)>max&&cur){lines.push(cur);cur=w}else cur=x}if(cur)lines.push(cur);return lines};
  let sg=null;
  if(ld?.assinatura){try{const si=new Image();si.src=ld.assinatura;await si.decode();
    const sw=si.naturalWidth,sh=si.naturalHeight,sc=document.createElement('canvas');sc.width=sw;sc.height=sh;
    const sx=sc.getContext('2d');sx.fillStyle='#fff';sx.fillRect(0,0,sw,sh);sx.drawImage(si,0,0);
    sg={w:sw,h:sh,jb:atob(sc.toDataURL('image/jpeg',.92).split(',')[1])}}catch(err){sg=null}}
  const lh=40,lw=lh*iw/ih,M2=48,CW=W-2*M2;
  const via=(t0,lbl)=>{
    c+=`${BLUE} rg 0 ${n2(H-t0-5)} ${n2(W)} 5 re f\n`;
    c+=`q ${n2(lw)} 0 0 ${lh} ${M2} ${n2(H-t0-22-lh)} cm /Im1 Do Q\n`;
    text(M2+lw+14,t0+40,'RECIBO DE ALUGUEL','F2',15,BLUE);
    text(M2+lw+14,t0+54,'Nº '+num,'F3',8,GRAY);
    text(W-M2,t0+46,brl(v),'F4',15,BLUE,'r');
    c+=`0.5 w ${col(.85,.87,.92)} RG ${M2} ${n2(H-t0-72)} m ${n2(W-M2)} ${n2(H-t0-72)} l S\n`;
    const par=`Recebi de ${lt?.nome||'—'}${lt?.cpf?', CPF '+cpf(lt.cpf):''}, a importância de ${brl(v)} (${extenso(v)}), referente ao aluguel do mês de ${mesLabel(p.referencia)} do imóvel situado em ${im?.endereco||'—'}${im?.bairro?', bairro '+im.bairro:''}.`;
    let y=t0+96;
    for(const l of wrap(par,'F1',10.5,CW-12)){text(M2,y,l,'F1',10.5,INK);y+=15}
    y+=4;
    c+=`${col(.945,.957,.98)} rg ${M2} ${n2(H-y-40)} ${n2(CW)} 40 re f\n`;
    const cw=CW/3;
    [['VENCIMENTO',dt(p.vencimento)],['DATA DO PAGAMENTO',dt(p.dataPagamento)],['FORMA DE PAGAMENTO',p.forma||'-']].forEach(([a,b],k)=>{
      text(M2+12+k*cw,y+14,a,'F1',7.5,GRAY);text(M2+12+k*cw,y+30,b,'F3',10,INK)});
    y+=40+22;
    text(M2,y,'Dou plena e geral quitação do valor acima.','F1',10.5,INK);
    y+=58;
    if(sg){const gh=40,gw=Math.min(170,gh*sg.w/sg.h),gh2=gw*sg.h/sg.w;c+=`q ${n2(gw)} 0 0 ${n2(gh2)} ${n2(W/2-gw/2)} ${n2(H-y+3)} cm /Im2 Do Q\n`}
    c+=`0.8 w ${INK} RG ${n2(W/2-120)} ${n2(H-y)} m ${n2(W/2+120)} ${n2(H-y)} l S\n`;
    text(W/2,y+13,ld?.nome||'Locador','F2',11,INK,'c');
    const sub=[ld?.doc?'CPF/CNPJ '+cpf(ld.doc):'',ld?.pix?'Pix: '+ld.pix:''].filter(Boolean).join('  -  ');
    if(sub)text(W/2,y+26,sub,'F1',8.5,GRAY,'c');
    text(W/2,t0+H/2-18,'CJNProperty - emitido em '+dt(today())+' - '+lbl,'F1',7.5,GRAY,'c');
  };
  if(vias==='lt')via(0,'Via do locatário');else via(0,'Via do locador');
  if(vias==='2'){
  c+=`0.6 w [4 3] 0 d ${col(.6,.62,.68)} RG ${M2} ${n2(H/2)} m ${n2(W-M2)} ${n2(H/2)} l S [] 0 d\n`;
  via(H/2+6,'Via do locatário');}
  const o=[];
  o[1]='<< /Type /Catalog /Pages 2 0 R >>';
  o[2]='<< /Type /Pages /Kids [3 0 R] /Count 1 >>';
  o[3]=`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R /F4 8 0 R >> /XObject << /Im1 9 0 R${sg?' /Im2 10 0 R':''} >> >> /Contents 4 0 R >>`;
  o[4]=`<< /Length ${c.length} >>\nstream\n${c}endstream`;
  ['Helvetica','Helvetica-Bold','Courier','Courier-Bold'].forEach((f,i)=>{o[5+i]=`<< /Type /Font /Subtype /Type1 /BaseFont /${f} /Encoding /WinAnsiEncoding >>`});
  o[9]=`<< /Type /XObject /Subtype /Image /Width ${iw} /Height ${ih} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jb.length} >>\nstream\n${jb}\nendstream`;
  if(sg)o[10]=`<< /Type /XObject /Subtype /Image /Width ${sg.w} /Height ${sg.h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${sg.jb.length} >>\nstream\n${sg.jb}\nendstream`;
  const NO=sg?10:9;
  let out='%PDF-1.4\n%\xE2\xE3\xCF\xD3\n';const off=[];
  for(let i=1;i<=NO;i++){off[i]=out.length;out+=`${i} 0 obj\n${o[i]}\nendobj\n`}
  const xr=out.length;
  out+=`xref\n0 ${NO+1}\n`+'0000000000 65535 f \n'+off.slice(1).map(x=>String(x).padStart(10,'0')+' 00000 n \n').join('')+`trailer\n<< /Size ${NO+1} /Root 1 0 R >>\nstartxref\n${xr}\n%%EOF`;
  const bytes=new Uint8Array(out.length);for(let i=0;i<out.length;i++)bytes[i]=out.charCodeAt(i)&255;
  return bytes;
}
async function baixarPdf(p){
  try{
    const bytes=await reciboPdf(p),{lt,num}=reciboInfo(p);
    const nome=('Recibo-'+num+'-'+(lt?.nome||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^A-Za-z0-9]+/g,'-')).replace(/-+$/,'')+viasNome(RECVIAS)+'.pdf';
    const blob=new Blob([bytes],{type:'application/pdf'});
    if(!window.CJN&&window.claude){try{const d=await claude.use('downloads');if(d){await d.save({filename:nome,data:blob});toast('PDF salvo');return}}catch(e){if(e&&e.code==='declined')return}}
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=nome;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),4000);toast('PDF gerado');
  }catch(e){toast('Não foi possível gerar o PDF')}
}
let RECIBO=null,RECVIAS='2';
try{const sv=localStorage.getItem('cjn_vias');if(sv==='loc'||sv==='lt'||sv==='2')RECVIAS=sv}catch(e){}
const setVias=v=>{RECVIAS=v;try{localStorage.setItem('cjn_vias',v)}catch(e){}};
const viasNome=v=>v==='loc'?'-via-locador':v==='lt'?'-via-locatario':'-2-vias';
function openRecibo(id,over){
  const base=by('pagamentos',id);if(!base)return;
  RECIBO={id,p:{...base,...(over||{})}};
  const layer=document.getElementById('layer');
  const draw=()=>{
    const p=RECIBO.p,{im,lt,ld,num}=reciboInfo(p),v=+p.valor||0;
    const fone=String(lt?.telefone||'').replace(/\D/g,''),wa=fone.length>=10?(fone.startsWith('55')&&fone.length>=12?fone:'55'+fone):'';
    const art=(lbl,v2)=>`<article class="recibo${v2?' via2':''}">
      <header><img src="${LOGO}" alt="CJN"><div><h3>RECIBO DE ALUGUEL</h3><div class="rn">Nº ${esc(num)}</div></div><div class="rv">${brl(v)}</div></header>
      <p>Recebi de <b>${esc(lt?.nome||'—')}</b>${lt?.cpf?`, CPF ${esc(cpf(lt.cpf))}`:''}, a importância de <b>${brl(v)}</b> (${esc(extenso(v))}), referente ao aluguel do mês de <b>${esc(mesLabel(p.referencia))}</b> do imóvel situado em <b>${esc(im?.endereco||'—')}</b>${im?.bairro?`, bairro ${esc(im.bairro)}`:''}.</p>
      <dl><div><dt>Vencimento</dt><dd>${dt(p.vencimento)}</dd></div><div><dt>Data do pagamento</dt><dd>${dt(p.dataPagamento)}</dd></div><div><dt>Forma de pagamento</dt><dd>${esc(p.forma||'—')}</dd></div></dl>
      <p>Dou plena e geral quitação do valor acima.</p>
      <div class="ass">${ld?.assinatura?`<img class="sig" src="${esc(ld.assinatura)}" alt="Assinatura">`:''}<div class="ln"></div><b>${esc(ld?.nome||'Locador')}</b><span>${ld?.doc?'CPF/CNPJ '+esc(cpf(ld.doc)):''}${ld?.pix?' · Pix: '+esc(ld.pix):''}</span></div>
      <footer>CJNProperty · emitido em ${dt(today())} · ${lbl}</footer></article>`;
    layer.innerHTML=`<div class="modal"><div class="rwrap" data-vias="${RECVIAS}">${art('Via do locador')}${art('Via do locatário',1)}
      <div class="racts noprint"><p class="sub" style="width:100%;margin:0 0 4px">Escolha quais vias saem no PDF e na impressão. As vias são idênticas, só muda o rodapé.</p><div class="bar"><label>Vias do recibo<select id="recVias"><option value="2" ${RECVIAS==='2'?'selected':''}>2 vias (locador + locatário)</option><option value="loc" ${RECVIAS==='loc'?'selected':''}>Só a via do locador</option><option value="lt" ${RECVIAS==='lt'?'selected':''}>Só a via do locatário</option></select></label><label>Data do pagamento<input id="recData" type="date" value="${esc(p.dataPagamento||'')}"></label><label>Forma de pagamento<input id="recForma" type="text" list="dlFormas" placeholder="Pix 500,00 + Dinheiro 300,00" value="${esc(p.forma||'')}"><datalist id="dlFormas"><option>Pix</option><option>Dinheiro</option><option>Transferência</option><option>Cartão</option><option>Boleto</option></datalist></label></div>
      <div class="bar"><button class="btn" data-recact="pdf">Baixar PDF</button>${window.CJN?'<button class="btn ghost" data-recact="print">Imprimir</button>':''}<button class="btn ghost" data-recact="copy">Copiar texto</button>${wa?`<a class="btn ghost" href="https://wa.me/${wa}?text=${encodeURIComponent(reciboTexto(p))}" target="_blank" rel="noopener">WhatsApp</a>`:''}<button class="btn ghost" data-recact="close">Fechar</button></div></div></div></div>`;
    layer.querySelector('.modal').addEventListener('mousedown',e=>{if(e.target.classList.contains('modal'))layer.innerHTML=''});
  };
  RECIBO.draw=draw;draw();
}
function vRecibos(){
  const pagos=D.pagamentos.filter(p=>p.dataPagamento);
  const meses=[...new Set(pagos.map(p=>p.referencia))].sort().reverse();
  const list=pagos.filter(p=>recMes==='todos'||p.referencia===recMes).sort((a,b)=>b.dataPagamento.localeCompare(a.dataPagamento));
  const tot=list.reduce((s,p)=>s+(+p.valor||0),0);
  const rows=list.map(p=>{const {im,lt,num}=reciboInfo(p);
    return `<tr data-rec="${p.id}" tabindex="0"><td class="mono">${esc(num)}</td><td><b>${esc(lt?.nome||'—')}</b><div class="sub">${esc(imLabel(im))}</div></td><td>${esc(mesLabel(p.referencia))}</td><td class="mono">${dt(p.dataPagamento)}</td><td>${esc(p.forma||'—')}</td><td class="num mono">${brl(p.valor)}</td><td><button class="btn sm" data-rec="${p.id}">Ver recibo</button></td></tr>`}).join('');
  return `<header class="top"><div><h1>Recibos</h1><p class="sub">${list.length} recibo(s) · ${brl(tot)}</p></div>
    <label>Mês de referência<select id="selRec"><option value="todos">Todos</option>${meses.map(m=>`<option value="${m}" ${m===recMes?'selected':''}>${esc(mesLabel(m))}</option>`).join('')}</select></label></header>
  ${rows?`<div class="tw"><table><thead><tr><th>Recibo</th><th>Locatário / imóvel</th><th>Referência</th><th>Pago em</th><th>Forma</th><th class="num">Valor</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`:empty('Nenhum recibo ainda','Quando um pagamento for registrado em Pagamentos, o recibo aparece aqui.')}`;
}
'''
def patch(s):
    def rep(a,b,count=1):
        nonlocal s
        assert a in s,a[:70]
        s=s.replace(a,b,count)
    rep("['pagamentos','Pagamentos']];","['pagamentos','Pagamentos'],['recibos','Recibos']];")
    rep("painelAno=new Date().getFullYear();","painelAno=new Date().getFullYear(), recMes='todos';")
    rep("['dataPagamento','Data do pagamento','date']]}","['dataPagamento','Data do pagamento','date'],['forma','Forma de pagamento (várias: Pix 500,00 + Dinheiro 300,00)','text']]}")
    rep("['pix','Chave Pix','text']]}","['pix','Chave Pix','text'],['assinatura','Assinatura digital (PNG)','sig','full']]}")
    rep("    else if(t==='file'){\n      if(!assets) return '';","    else if(t==='sig'){inp=`<input id=\"f_${k}\" type=\"hidden\" value=\"${esc(v)}\"><div class=\"sigbox\"><div class=\"pv\" id=\"sigPv\">${v?`<img src=\"${esc(v)}\" alt=\"Assinatura\">`:'Sem assinatura'}</div><div><input id=\"sigFile\" type=\"file\" accept=\"image/png,image/*\"><button type=\"button\" class=\"btn sm ghost\" data-recact=\"sigdel\">Remover</button></div></div><span class=\"sub\">PNG com fundo transparente funciona melhor. Aparece nos recibos.</span>`}\n    else if(t==='file'){\n      if(!assets) return '';")
    rep("pagamentos:vPagamentos}[view]","pagamentos:vPagamentos,recibos:vRecibos}[view]")
    rep("[data-view],[data-modo],","[data-view],[data-rec],[data-recact],[data-modo],")
    rep("  if(d.view){view=d.view;render()}","  if(d.view){view=d.view;render()}\n  else if(d.rec){openRecibo(d.rec)}\n  else if(d.recact){const a=d.recact;if(a==='sigdel'){sigSet('')}else if(a==='close')document.getElementById('layer').innerHTML='';else if(a==='print')window.print();else if(a==='pdf')baixarPdf(RECIBO.p);else if(a==='copy'){const tx=reciboTexto(RECIBO.p);try{await navigator.clipboard.writeText(tx);toast('Texto copiado')}catch(err){toast('Não foi possível copiar')}}}")
    rep("else if(d.pay){const p=by('pagamentos',d.pay);try{await db.collection('pagamentos').doc(p.id).update({dataPagamento:p.dataPagamento?'':today()});toast(p.dataPagamento?'Pagamento desfeito':'Pagamento registrado')}catch(err){toast('Sem permissão para alterar')}}",
        "else if(d.pay){const p=by('pagamentos',d.pay);if(!p.dataPagamento){openPagar(p.id)}else{try{await db.collection('pagamentos').doc(p.id).update({dataPagamento:''});toast('Pagamento desfeito')}catch(err){toast('Sem permissão para alterar')}}}")
    rep("if(e.target.id==='selMes'){pagMes=e.target.value;render()}","if(e.target.id==='selMes'){pagMes=e.target.value;render()}\n  if(e.target.id==='sigFile'){sigLoad(e.target)}\n  if(e.target.id==='recVias'&&RECIBO){setVias(e.target.value);RECIBO.draw()}\n  if(e.target.id==='selRec'){recMes=e.target.value;render()}\n  if(e.target.id==='recData'&&RECIBO){const v=e.target.value;if(!v){toast('Informe a data do pagamento');RECIBO.draw();return}RECIBO.p.dataPagamento=v;db.collection('pagamentos').doc(RECIBO.id).update({dataPagamento:v}).catch(()=>toast('Sem permissão para salvar'));RECIBO.draw()}\n  if(e.target.id==='recForma'&&RECIBO){RECIBO.p.forma=e.target.value;db.collection('pagamentos').doc(RECIBO.id).update({forma:e.target.value}).catch(()=>toast('Sem permissão para salvar'));RECIBO.draw()}")
    rep("e.target.matches('[data-edit]')","e.target.matches('[data-edit],[data-rec]')")
    rep("<td><button class=\"btn sm ${p.dataPagamento?'ghost':''}\" data-pay=\"${p.id}\">${p.dataPagamento?'Desfazer':'Registrar pagamento'}</button></td></tr>",
        "<td><div class=\"bar\"><button class=\"btn sm ${p.dataPagamento?'ghost':''}\" data-pay=\"${p.id}\">${p.dataPagamento?'Desfazer':'Registrar pagamento'}</button>${p.dataPagamento?`<button class=\"btn sm\" data-rec=\"${p.id}\">Recibo</button>`:''}</div></td></tr>")
    rep("<button class=\"btn sm ghost\" data-edit=\"pagamentos:${ps.id}\">Editar</button>","${ps.dataPagamento?`<button class=\"btn sm\" data-rec=\"${ps.id}\">Recibo</button>`:''}<button class=\"btn sm ghost\" data-edit=\"pagamentos:${ps.id}\">Editar</button>")
    # arquivos como link quando não há upload
    rep("if(!assets) return '';","if(!assets){return `<label class=\"full\">${l} (link do Google Drive ou endereço)<input id=\"f_${k}\" type=\"url\" value=\"${esc(v)}\" placeholder=\"https://…\"></label>`}")
    rep("if(t==='file'){const f=el.files[0];","if(t==='file'){if(el.type!=='file'){out[k]=el.value.trim();continue}const f=el.files[0];")
    rep("<img src=\"${esc(i.foto)}\"","<img src=\"${esc(imgSrc(i.foto))}\"")
    rep("/* ---------- render e eventos ---------- */",JS+"\n/* ---------- render e eventos ---------- */")
    rep("@media (max-width:760px){\n  .shell",CSS+"@media (max-width:760px){\n  .shell")
    return s
for f in sys.argv[1:]:
    s=open(f).read(); open(f,'w').write(patch(s)); print('ok',f)
