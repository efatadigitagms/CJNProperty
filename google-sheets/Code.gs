/**
 * CJNProperty - ponte entre o aplicativo e esta planilha do Google.
 *
 * COMO USAR (uma vez só):
 * 1. Na planilha: Extensões > Apps Script. Apague o que houver e cole este arquivo inteiro.
 * 2. Crie o seu usuário e senha: escolha a função "adicionarUsuario", edite USUARIO e SENHA dentro dela,
 *    clique em Executar (autorize quando o Google pedir) e depois APAGUE a senha do código.
 *    A senha fica guardada só como resumo criptografado. Para outro usuário, repita.
 * 3. Escolha a função "setup" no topo do editor e clique em Executar. Autorize quando o Google pedir.
 *    Isso cria as abas db_Imoveis, db_Locadores, db_Locatarios, db_Contratos e db_Pagamentos.
 *    Suas abas atuais não são alteradas.
 * 4. Implantar > Nova implantação > tipo "App da Web".
 *    Executar como: Eu. Quem pode acessar: Qualquer pessoa. Copie o endereço que termina em /exec.
 * 5. No aplicativo: botão "Planilha Google", cole o endereço e entre com usuário e senha.
 *
 * Depois de mudar este código, use Implantar > Gerenciar implantações > Editar > Nova versão.
 */
// Modo antigo (opcional): código de acesso único. Deixe como está para usar só usuário e senha.
const TOKEN = 'TROQUE-ESTE-CODIGO';
// Quantas horas o login vale antes de pedir a senha de novo (168 = 7 dias).
const SESSION_HOURS = 168;

// [chave no app, nome da coluna na planilha, tipo: t=texto, n=numero, d=data AAAA-MM-DD]
const SCHEMA = {
  imoveis:    {tab: 'db_Imoveis',    cols: [['id','Id','t'],['codigo','Codigo','t'],['endereco','Endereco','t'],['bairro','Bairro','t'],['tipo','Tipo','t'],['aluguel','Valor_Aluguel','n'],['status','Status','t'],['foto','Foto_Link','t']]},
  locadores:  {tab: 'db_Locadores',  cols: [['id','Id','t'],['nome','Nome','t'],['doc','CPF_CNPJ','t'],['pix','Chave_Pix','t'],['assinatura','Assinatura','t']]},
  locatarios: {tab: 'db_Locatarios', cols: [['id','Id','t'],['nome','Nome','t'],['cpf','CPF','t'],['telefone','Telefone','t'],['email','Email','t'],['profissao','Profissao','t']]},
  contratos:  {tab: 'db_Contratos',  cols: [['id','Id','t'],['numero','Numero','t'],['imovelId','Id_Imovel','t'],['locadorId','Id_Locador','t'],['locatarioId','Id_Locatario','t'],['entrada','Data_Entrada','d'],['saida','Data_Saida','d'],['valor','Valor_Mensal','n'],['status','Status','t'],['pdf','Contrato_Link','t']]},
  pagamentos: {tab: 'db_Pagamentos', cols: [['id','Id','t'],['contratoId','Id_Contrato','t'],['referencia','Referencia','t'],['valor','Valor','n'],['vencimento','Vencimento','d'],['dataPagamento','Data_Pagamento','d'],['forma','Forma_Pagamento','t']]}
};
// Dados de exemplo (fictícios). Usados apenas ao criar as abas; edite ou apague depois.
const SEED = {
 "imoveis": [
  {
   "id": "i1",
   "codigo": "101",
   "endereco": "Rua das Flores, 101",
   "bairro": "Centro",
   "tipo": "Residencial",
   "aluguel": 800,
   "status": "Alugado",
   "foto": ""
  },
  {
   "id": "i2",
   "codigo": "102",
   "endereco": "Rua das Flores, 102",
   "bairro": "Centro",
   "tipo": "Comercial",
   "aluguel": 1500,
   "status": "Alugado",
   "foto": ""
  },
  {
   "id": "i3",
   "codigo": "103",
   "endereco": "Avenida Brasil, 250",
   "bairro": "Jardim",
   "tipo": "Residencial",
   "aluguel": 1000,
   "status": "Disponível",
   "foto": ""
  }
 ],
 "locadores": [
  {
   "id": "l001",
   "nome": "Maria Exemplo da Silva",
   "doc": "00000000000",
   "pix": "exemplo@email.com"
  }
 ],
 "locatarios": [
  {
   "id": "t1",
   "nome": "João Exemplo de Souza",
   "cpf": "11111111111",
   "telefone": "11 90000-0000",
   "email": "",
   "profissao": "vendedor"
  },
  {
   "id": "t2",
   "nome": "Ana Modelo Pereira",
   "cpf": "22222222222",
   "telefone": "",
   "email": "",
   "profissao": "gerente"
  }
 ],
 "contratos": [
  {
   "id": "c1",
   "numero": "0001",
   "imovelId": "i1",
   "locadorId": "l001",
   "locatarioId": "t1",
   "entrada": "2026-09-20",
   "saida": "2027-09-20",
   "valor": 800,
   "status": "Ativo",
   "pdf": ""
  },
  {
   "id": "c2",
   "numero": "0002",
   "imovelId": "i2",
   "locadorId": "l001",
   "locatarioId": "t2",
   "entrada": "2026-03-25",
   "saida": "2028-03-25",
   "valor": 1500,
   "status": "Ativo",
   "pdf": ""
  }
 ],
 "pagamentos": []
};

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return out_({ok: true, app: 'CJNProperty'});
}

function doPost(e) {
  let req;
  try { req = JSON.parse(e.postData.contents); } catch (err) { return out_({ok: false, error: 'Pedido inválido'}); }
  if (req && req.action === 'login') return out_(login_(req));
  const authErr = auth_(req);
  if (authErr) return out_({ok: false, error: authErr});
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    if (req.action === 'ping') return out_({ok: true});
    if (req.action === 'list') return out_({ok: true, data: listAll_()});
    if (req.action === 'ops') { applyOps_(req.ops || []); return out_({ok: true}); }
    return out_({ok: false, error: 'Ação desconhecida'});
  } catch (err) {
    return out_({ok: false, error: String(err)});
  } finally {
    lock.releaseLock();
  }
}

/** Devolve '' se o pedido está autorizado, ou a mensagem de erro. */
function auth_(req) {
  if (!req) return 'Pedido inválido';
  if (req.session) {
    const parts = String(req.session).split('.');
    if (parts.length !== 2) return 'Sessão inválida. Entre de novo.';
    let payload;
    try { payload = Utilities.newBlob(Utilities.base64DecodeWebSafe(parts[0])).getDataAsString(); } catch (err) { return 'Sessão inválida. Entre de novo.'; }
    if (hex_(Utilities.computeHmacSha256Signature(payload, secret_())) !== parts[1]) return 'Sessão inválida. Entre de novo.';
    const i = payload.lastIndexOf('|');
    const name = payload.slice(0, i), exp = Number(payload.slice(i + 1));
    if (!(exp > Date.now() / 1000)) return 'Sessão expirada. Entre de novo.';
    if (!users_()[name]) return 'Usuário sem acesso. Entre de novo.';
    return '';
  }
  if (req.token) {
    if (TOKEN !== 'TROQUE-ESTE-CODIGO' && req.token === TOKEN) return '';
    return 'Código de acesso incorreto';
  }
  return 'Entre com usuário e senha';
}

function props_() { return PropertiesService.getScriptProperties(); }
function users_() { try { return JSON.parse(props_().getProperty('USERS') || '{}'); } catch (err) { return {}; } }
function secret_() {
  let s = props_().getProperty('SECRET');
  if (!s) { s = Utilities.getUuid() + Utilities.getUuid(); props_().setProperty('SECRET', s); }
  return s;
}
function hex_(bytes) { return bytes.map(function (b) { return ('0' + (b & 255).toString(16)).slice(-2); }).join(''); }
function hashPw_(salt, pw) {
  let h = salt + '|' + pw;
  for (let i = 0; i < 1500; i++) h = hex_(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, salt + h));
  return h;
}
function setUser_(name, pw) {
  name = String(name || '').toLowerCase().trim();
  if (!name) throw new Error('Informe o usuário');
  if (String(pw || '').length < 8) throw new Error('A senha precisa ter pelo menos 8 caracteres');
  const all = users_(), salt = Utilities.getUuid();
  all[name] = {s: salt, h: hashPw_(salt, String(pw))};
  props_().setProperty('USERS', JSON.stringify(all));
}

/** Cria ou troca a senha de um usuário. Edite as duas linhas, execute, e DEPOIS APAGUE a senha deste código. */
function adicionarUsuario() {
  const USUARIO = 'seu-usuario';
  const SENHA = 'troque-esta-senha';
  setUser_(USUARIO, SENHA);
  Logger.log('Usuário "' + USUARIO.toLowerCase().trim() + '" salvo. Agora APAGUE a senha deste código e salve.');
}

/** Remove um usuário (ele perde o acesso na hora). */
function removerUsuario() {
  const USUARIO = 'seu-usuario';
  const all = users_();
  delete all[String(USUARIO).toLowerCase().trim()];
  props_().setProperty('USERS', JSON.stringify(all));
  Logger.log('Usuário removido.');
}

function login_(req) {
  const name = String(req.user || '').toLowerCase().trim();
  const cache = CacheService.getScriptCache(), fk = 'fail_' + name;
  const fails = Number(cache.get(fk) || 0);
  if (fails >= 5) return {ok: false, error: 'Muitas tentativas. Aguarde 15 minutos.'};
  const u = users_()[name];
  const h = hashPw_(u ? u.s : 'x', String(req.pass || ''));
  if (!u || h !== u.h) {
    cache.put(fk, String(fails + 1), 900);
    return {ok: false, error: 'Usuário ou senha incorretos'};
  }
  cache.remove(fk);
  const exp = Math.floor(Date.now() / 1000) + SESSION_HOURS * 3600;
  const payload = name + '|' + exp;
  const sig = hex_(Utilities.computeHmacSha256Signature(payload, secret_()));
  return {ok: true, session: Utilities.base64EncodeWebSafe(payload) + '.' + sig, user: name, exp: exp};
}

function sheet_(col) {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SCHEMA[col].tab);
  if (!sh) throw new Error('Aba ' + SCHEMA[col].tab + ' não existe. Execute a função setup.');
  return sh;
}

function cellOut_(v, type) {
  if (v instanceof Date) return Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  if (type === 'n') return Number(v) || 0;
  return v === '' || v == null ? '' : String(v);
}

function listAll_() {
  const data = {};
  Object.keys(SCHEMA).forEach(function (col) {
    const S = SCHEMA[col];
    const rows = sheet_(col).getDataRange().getValues();
    data[col] = rows.slice(1).filter(function (r) { return String(r[0]).trim() !== ''; }).map(function (r) {
      const o = {};
      S.cols.forEach(function (c, i) { o[c[0]] = cellOut_(r[i], c[2]); });
      return o;
    });
  });
  return data;
}

function applyOps_(ops) {
  const byCol = {};
  ops.forEach(function (o) { if (SCHEMA[o.col]) (byCol[o.col] = byCol[o.col] || []).push(o); });
  Object.keys(byCol).forEach(function (col) {
    const S = SCHEMA[col], sh = sheet_(col), n = S.cols.length;
    const last = sh.getLastRow();
    const ids = last > 1 ? sh.getRange(2, 1, last - 1, 1).getValues() : [];
    const rowOf = {};
    ids.forEach(function (r, i) { rowOf[String(r[0])] = i + 2; });
    const toDelete = [];
    byCol[col].forEach(function (o) {
      const id = String(o.id);
      if (o.op === 'delete') {
        if (rowOf[id]) { toDelete.push(rowOf[id]); delete rowOf[id]; }
        return;
      }
      const d = o.data || {};
      const row = S.cols.map(function (c) {
        if (c[0] === 'id') return id;
        const v = d[c[0]];
        if (c[2] === 'n') return Number(v) || 0;
        return v == null ? '' : String(v);
      });
      let r = rowOf[id];
      if (!r) {
        r = Math.max(sh.getLastRow(), 1) + 1;
        if (r > sh.getMaxRows()) sh.insertRowsAfter(sh.getMaxRows(), 50);
        rowOf[id] = r;
      }
      sh.getRange(r, 1, 1, n).setValues([row]);
    });
    toDelete.sort(function (a, b) { return b - a; }).forEach(function (r) { sh.deleteRow(r); });
  });
}

/** Cria as abas do aplicativo (só as que ainda não existem) e carrega os dados iniciais. */
function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  Object.keys(SCHEMA).forEach(function (col) {
    const S = SCHEMA[col];
    let sh = ss.getSheetByName(S.tab);
    const isNew = !sh;
    if (!sh) sh = ss.insertSheet(S.tab);
    const n = S.cols.length;
    sh.getRange(1, 1, 1, n).setValues([S.cols.map(function (c) { return c[1]; })])
      .setFontWeight('bold').setBackground('#043C95').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    S.cols.forEach(function (c, i) {
      sh.getRange(2, i + 1, Math.max(sh.getMaxRows() - 1, 1), 1).setNumberFormat(c[2] === 'n' ? '#,##0.00' : '@');
    });
    if (isNew && SEED[col] && SEED[col].length) {
      const rows = SEED[col].map(function (o) {
        return S.cols.map(function (c) {
          const v = o[c[0]];
          return c[2] === 'n' ? Number(v) || 0 : (v == null ? '' : String(v));
        });
      });
      sh.getRange(2, 1, rows.length, n).setValues(rows);
    }
    sh.autoResizeColumns(1, n);
  });
  Logger.log('Pronto. Agora faça a implantação como App da Web.');
}
