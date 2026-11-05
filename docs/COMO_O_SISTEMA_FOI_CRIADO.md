# CJNProperty — Como o sistema foi criado

Registro completo das instruções, decisões e etapas de criação. Serve para refazer, mudar ou continuar o sistema (sozinho ou com o Claude). Nada aqui contém dados reais, senhas ou links privados.

Endereços: site https://efatadigitagms.github.io/CJNProperty/ · repositório https://github.com/efatadigitagms/CJNProperty

---

## 1. Objetivo
Gerenciar imóveis alugados do proprietário: imóveis, locadores, locatários, contratos, cobranças mensais com calendário e recibos de pagamento. Nasceu da planilha `Gestao_Imobiliaria.xlsx`. Idioma: português do Brasil. Valores em R$, datas dd/mm/aaaa.

## 2. Linha do tempo (o que foi pedido e feito, em ordem)
1. **Painel e calendário mensal de pagamentos**, a partir da planilha.
2. **Publicação no GitHub Pages**, como PWA (instala no celular, funciona offline).
3. **Identidade visual**: cor principal `#043C95` e logo CJN (escudo cinza e azul-marinho).
4. **Google Sheets como banco de dados** (via Apps Script), para todos os aparelhos verem os mesmos dados.
5. **Aba Recibos**: logo, data de pagamento editável, PDF para baixar, duas vias idênticas.
6. **Assinatura digital (PNG)** do locador no recibo.
7. **Dias em atraso** nos pagamentos vencidos (lista, painel, calendário).
8. **PDF com escolha de vias**: 2 vias, só locador ou só locatário.
9. **Renomear "Painel" para "Painel de Controlo".**
10. **Login com usuário e senha** (primeiro tentado com conta Google; trocado por usuário e senha, sem Google Cloud).
11. **Tema preto**, depois trocado por **azul-marinho e cinza** (cores do escudo).
12. **Fotos no site do GitHub**: o envio de foto foi criado para o site (reduz a imagem para caber numa célula da planilha).
13. **Tempo do locatário no imóvel** (anos e meses) em Imóveis, Contratos e Pessoas.
14. **Mais de uma forma de pagamento** no mesmo recibo (ex.: Pix 500,00 + Dinheiro 300,00).
15. **Arrecadado no ano**: cartão no painel e gráfico de barras por mês, com escolha do ano (conta pela data de recebimento).
16. **Dados reais** migrados para a planilha do proprietário; repositório público fica só com dados fictícios.

## 3. Arquitetura

Há **dois aplicativos gerados da mesma base**:

| Saída | Onde roda | Banco de dados |
|---|---|---|
| `gestao-imobiliaria.html` | Dentro do Claude (link privado) | Banco do próprio Claude |
| `index.html` (PWA) | GitHub Pages / celular | IndexedDB no aparelho + Google Sheets (opcional) |

Arquivos de origem (pasta `src/`):

| Arquivo | Função |
|---|---|
| `app.base.html` | O aplicativo limpo: telas, regras, formulários, estilos. |
| `recibo_patch.py` | Aplica à base o módulo de recibos (tela, PDF feito à mão, assinatura, vias, forma de pagamento múltipla). |
| `shim.js` | Só do PWA: camada de armazenamento (IndexedDB), sincronização com a planilha, login, envio de foto/PDF. Faz o site imitar o banco do Claude (`claude.use('db')`). |
| `build.py` | Junta tudo e gera os dois arquivos. |
| `seed_public.json` | Dados fictícios de exemplo (os reais ficam fora do GitHub). |

Para gerar o site: dentro de `src/`, rode `PWA_OUT=.. python3 build.py`. Isso cria `../index.html`. Depois aumente a versão do cache em `sw.js` (`cjnproperty-vN`) e publique.

Outros arquivos do repositório: `manifest.webmanifest`, `sw.js` (cache offline; páginas pela rede primeiro), ícones, `logo.png`, `google-sheets/Code.gs`, `INSTRUCOES.md` (guia de uso e instalação).

## 4. Modelo de dados
- `imoveis` {codigo, endereco, bairro, tipo, aluguel, status, foto}
- `locadores` {nome, doc, pix, assinatura}
- `locatarios` {nome, cpf, telefone, email, profissao}
- `contratos` {numero, imovelId, locadorId, locatarioId, entrada, saida, valor, status, pdf}
- `pagamentos` {contratoId, referencia (AAAA-MM), valor, vencimento, dataPagamento, forma}; id = `contratoId_AAAA-MM`

Regras: vencimento = dia de início do contrato; situação Pago/Atrasado/Pendente é calculada; atraso = dias entre vencimento e hoje; número do recibo `REC-AAAAMM-XXXX`; forma de pagamento múltipla guardada como texto, ex. `Pix 500,00 + Dinheiro 300,00` (uma forma só continua `Pix`).

**Regra de ouro:** ao mudar um campo, mude nos três lugares: SCHEMA do formulário (`app.base.html`), `FIELDS`/`TYPES` (`shim.js`) e `SCHEMA` do `Code.gs`. Depois publique nova versão do script.

## 5. Recibos e PDF
- PDF montado manualmente (sem bibliotecas), fontes padrão, logo e assinatura em JPEG.
- Opções: 2 vias com linha de corte, só via do locador, só via do locatário.
- Recibo sempre em papel branco, mesmo com o app em fundo preto.
- Assinatura: PNG enviado no cadastro do locador.

## 6. Google Sheets e Apps Script
- `google-sheets/Code.gs` cria as abas `db_Imoveis`, `db_Locadores`, `db_Locatarios`, `db_Contratos`, `db_Pagamentos` (função `setup`; não altera abas existentes).
- O app envia `POST` (texto simples, JSON) ao endereço `/exec`. Ações: `ping`, `list`, `ops`, `login`.
- Implantação: App da Web, "Executar como: Eu", "Quem acessa: Qualquer pessoa". Depois de mudar o código: **Implantar → Gerenciar implantações → Editar → Nova versão** (o endereço não muda).
- O app mostra os dados na hora (cópia local), envia as alterações em fila e busca a planilha a cada minuto. A planilha vence ao conectar.
- Limite de célula do Google: ~50 mil caracteres. Por isso foto vira JPEG reduzido (até ~46 mil caracteres) e PDF de contrato só entra se for bem pequeno.

## 7. Login e segurança
- Usuários ficam nas propriedades do script (`USERS`): senha guardada só como resumo (SHA-256 com sal, 1500 voltas). Para criar ou trocar: editar `USUARIO` e `SENHA` na função `adicionarUsuario`, executar e **apagar a senha do código**. Remover: `removerUsuario`.
- Sessão assinada por `SECRET` (HMAC), validade `SESSION_HOURS` (168 h = 7 dias), conferida a cada pedido. Usuário removido perde o acesso na hora.
- 5 senhas erradas = bloqueio de 15 minutos.
- A proteção real é a conferência no servidor (Apps Script). A tela de login do app é uma barreira de uso; dados já baixados ficam no navegador do aparelho (use **Sair** e limpe os dados do site em aparelho de terceiros).
- Sem Google Cloud. Modo antigo com código único (`TOKEN`) existe só como alternativa.
- Repositório público: nunca colocar dados reais, senhas, links privados nem a planilha.

## 8. Aparência
- Tema azul-marinho e cinza (cores do escudo): fundo `#0a1a33` com degradê, cartões `#102848`, destaque cinza-prata `#c4cbd6`. Cores por variáveis CSS na base.
- Fontes: Bricolage Grotesque, IBM Plex Sans e Mono. Layout com menu lateral (no celular, abas no topo).
- O nome da primeira tela é **Painel de Controlo**.

## 9. Como publicar uma mudança (checklist)
1. Editar `src/app.base.html` (ou `shim.js`, `recibo_patch.py`).
2. `cd src && PWA_OUT=.. python3 build.py`.
3. Aumentar `cjnproperty-vN` em `sw.js`.
4. Conferir no navegador; procurar dados reais antes de enviar (CPF, nomes, e-mails).
5. `git add`, `commit`, `push`. O GitHub Pages atualiza em 1 a 2 minutos (Ctrl+F5 para ver).
6. Se o `Code.gs` mudou, colar no Apps Script e publicar **Nova versão**.

## 10. Como pedir mudanças ao Claude
Cole no início da conversa: "Projeto CJNProperty (PWA de gestão de imóveis, GitHub efatadigitagms/CJNProperty). Leia `docs/COMO_O_SISTEMA_FOI_CRIADO.md` e `src/`. Fonte em `src/`, gerar com `build.py`." Depois descreva a mudança.

Ideias já conversadas ou fáceis de fazer: reajuste anual de aluguel, relatório de inadimplência e receita por imóvel, lembretes por WhatsApp, dia de vencimento por contrato, login obrigatório já no primeiro acesso (fixando o endereço `/exec` no site), link do Drive para PDFs grandes.
