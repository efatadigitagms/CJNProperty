# CJNProperty — Instruções do projeto

Aplicativo para gerenciar imóveis alugados: cadastro de imóveis, locadores e locatários, contratos, cobranças mensais com calendário e recibos de pagamento. Foi criado a partir da planilha `Gestao_Imobiliaria.xlsx`.

---

## 1. O que existe

| Item | Para que serve |
|---|---|
| **App no Claude** (link privado na sua conta) | Versão de uso e testes. Os dados ficam no banco do próprio Claude. |
| **`cjnproperty-pwa.zip`** | Versão para publicar no GitHub Pages. Instala no celular como aplicativo e funciona offline. |
| **Google Sheets (opcional)** | Planilha que funciona como banco de dados da versão do GitHub, com o script `google-sheets/Code.gs`. |

Arquivos da versão do GitHub:

| Arquivo | Função |
|---|---|
| `index.html` | O aplicativo inteiro (telas, regras, armazenamento e sincronização). |
| `manifest.webmanifest` | Nome, cores e ícones do app instalado. |
| `sw.js` | Service worker: guarda o app no aparelho para abrir sem internet. |
| `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`, `logo.png` | Ícones e logo CJN. |
| `google-sheets/Code.gs` | Script que liga o app à planilha do Google. |
| `INSTRUCOES.md` | Este documento. |

---

## 2. Telas do aplicativo

- **Painel**: imóveis alugados, receita mensal contratada, recebido no mês, valor em atraso, cobranças em aberto, contratos que terminam em até 6 meses e imóveis disponíveis.
- **Imóveis**: cartões com foto, endereço, bairro, valor, situação (Alugado, Disponível, Em manutenção) e locatário atual.
- **Contratos**: locatário, imóvel, locador, vigência, valor mensal e situação. Avisa quando faltam 90 dias ou menos para o término.
- **Pessoas**: locatários (CPF, telefone, e-mail, profissão) e locadores (CPF/CNPJ, chave Pix).
- **Pagamentos**
  - *Lista*: filtro por mês e por situação (Pendente, Atrasado, Pago). O botão **Gerar cobranças do mês** cria uma cobrança para cada contrato ativo. **Registrar pagamento** abre uma janela com a **data do pagamento em aberto** (vem com a data de hoje, mas você pode informar outra) e a forma de pagamento; ao confirmar, abre o recibo. **Desfazer** limpa a data.
  - *Calendário*: escolha um contrato e veja todos os meses dele, do início ao término, coloridos por situação. Toque em um mês para gerar a cobrança, registrar ou desfazer o pagamento. Abaixo há o calendário do mês com o dia de vencimento de cada contrato (cinza = previsto, ainda sem cobrança).
- **Recibos**: lista de todos os pagamentos feitos, com filtro por mês de referência.
  - O recibo traz o logo, número, valor por extenso, dados do locatário, do imóvel e do locador, vencimento, data e forma de pagamento (Pix, Dinheiro, Transferência, Cartão, Boleto).
  - A **data** e a **forma de pagamento** podem ser alteradas no próprio recibo (salvam na hora).
  - **Duas vias iguais**: o PDF e a impressão saem com **1ª via** (locador) e **2ª via** (locatário) idênticas na mesma folha A4, separadas por uma linha tracejada de corte. Na tela aparece uma via só.
  - Botões: **Baixar PDF** (arquivo A4 com as duas vias e logo, gerado no próprio aparelho e nomeado `Recibo-REC-AAAAMM-XXXX-Nome.pdf`), **Imprimir** (na versão do GitHub), **Copiar texto** e **WhatsApp** (abre a conversa com o telefone do locatário e o texto pronto).
  - O número do recibo segue o padrão `REC-AAAAMM-XXXX` (mês de referência e início do número do contrato).

---

## 3. Dados

Relações: **Contrato** liga um Imóvel, um Locador e um Locatário. **Pagamento** pertence a um Contrato e a um mês de referência.

| Tabela | Campos |
|---|---|
| Imóveis | código, endereço, bairro, tipo, valor do aluguel, situação, link da foto |
| Locadores | nome, CPF/CNPJ, chave Pix |
| Locatários | nome, CPF, telefone, e-mail, profissão |
| Contratos | número, imóvel, locador, locatário, início, término, valor mensal, situação (Ativo/Encerrado), link do PDF |
| Pagamentos | contrato, mês de referência (AAAA-MM), valor, vencimento, data do pagamento, forma de pagamento |

Regras:
- O **vencimento** de cada cobrança é o dia do início do contrato (início em 25/03, vence todo dia 25). Em meses curtos usa o último dia. Dá para editar cada cobrança.
- Situação do pagamento: **Pago** se tem data de pagamento; **Atrasado** se o vencimento já passou; **Pendente** nos demais casos.
- Cada contrato tem no máximo uma cobrança por mês.

Ajustes feitos ao importar a planilha original:
- Os códigos das abas não batiam entre si (por exemplo "Casa" e "8a9100a6"). Os contratos foram ligados aos imóveis pelo endereço e pelo valor do aluguel. Conferir.
- CPFs que o Excel tinha cortado (zero à esquerda) foram corrigidos.
- O imóvel CJr estava sem situação e entrou como Disponível.
- A chave Pix da Joana Darc é igual à do Carlos José. Pode ser engano de cópia.
- As abas Usuarios e Vistorias estavam vazias e ainda não foram incluídas no app.

---

## 4. Publicar no GitHub Pages

1. No GitHub, crie um repositório (por exemplo `cjnproperty`).
2. Envie **todos os arquivos do zip** para a raiz do repositório, mantendo a pasta `google-sheets`. Pelo site: *Add file → Upload files*.
3. Vá em **Settings → Pages**. Em *Build and deployment*, escolha **Deploy from a branch**, branch **main** e pasta **/ (root)**, e salve.
4. Em alguns minutos o app abre em `https://SEU-USUARIO.github.io/cjnproperty/`.

Observações:
- Repositórios gratuitos em GitHub Pages precisam ser **públicos**. Por isso, **nunca coloque dados reais, códigos de acesso ou links da planilha dentro do repositório**. O arquivo `index.html` traz apenas os 4 imóveis de exemplo vindos da planilha original. Se preferir, troque esses dados por exemplos fictícios antes de publicar.
- Para atualizar o app, envie o novo `index.html` (e `sw.js`, se mudou) para o repositório. Quem já instalou recebe a atualização ao abrir o app com internet.

### Instalar no celular ou computador
- **Android (Chrome)**: menu ⋮ → *Instalar app* ou *Adicionar à tela inicial*.
- **iPhone (Safari)**: botão Compartilhar → *Adicionar à Tela de Início*.
- **Computador (Chrome/Edge)**: ícone de instalação na barra de endereço.

---

## 5. Usar o Google Sheets como banco de dados

Sem esta etapa, os dados ficam **somente no navegador do aparelho** (um celular não enxerga o que foi lançado no outro). Com ela, a planilha passa a ser a fonte dos dados e todos os aparelhos conectados enxergam o mesmo.

### Configuração (uma vez)
1. Abra a planilha no Google Sheets. Menu **Extensões → Apps Script**.
2. Apague o código que estiver lá e cole todo o conteúdo de `google-sheets/Code.gs`.
3. Na linha `const TOKEN = '...'`, troque o texto por um **código secreto seu** (longo, com letras e números). Guarde esse código.
4. No topo do editor, escolha a função **`setup`** e clique em **Executar**. Autorize quando o Google pedir (aparece o aviso "app não verificado": *Avançado → Acessar*; o script é seu).
   Isso cria as abas **db_Imoveis, db_Locadores, db_Locatarios, db_Contratos, db_Pagamentos** com os dados iniciais. As abas que você já tinha **não são alteradas**.
5. Clique em **Implantar → Nova implantação → tipo "App da Web"**.
   - *Executar como*: **Eu**.
   - *Quem pode acessar*: **Qualquer pessoa**.
   - Clique em Implantar e copie o endereço que termina em `/exec`.
6. No aplicativo, botão **Planilha Google** (menu lateral, ou no topo do celular). Cole o **endereço** e o **código secreto** e toque em **Conectar e sincronizar**.

Faça o passo 6 em cada aparelho que for usar.

### Como funciona
- O app mostra os dados na hora (cópia local) e envia cada alteração para a planilha em segundo plano. O texto no rodapé do menu mostra a situação: *Sincronizado*, *N alterações para enviar*, *Sem conexão* ou o erro.
- Sem internet, o app continua funcionando e envia as alterações quando a conexão volta.
- A cada minuto, e ao voltar para o app, ele busca a planilha. **Você pode editar direto na planilha**: as mudanças aparecem no app.
- Se duas pessoas alterarem o mesmo registro ao mesmo tempo, vale o último a gravar.
- Ao conectar, **os dados da planilha substituem os do aparelho**. Se a planilha estiver vazia, o app envia os dados que tem.
- Ao editar na planilha, mantenha a linha de títulos e a coluna **Id** de cada linha. Para um registro novo, use um Id único (por exemplo `i5`). Datas no formato `AAAA-MM-DD` (ou `dd/mm/aaaa`) e referência no formato `AAAA-MM`.
- **Fotos e PDFs**: o campo vira um **link** (Google Drive ou endereço da imagem), porque fotos não cabem em uma célula. No Drive, deixe o arquivo compartilhado por link para a foto aparecer no cartão.
- Depois de alterar o `Code.gs`, use **Implantar → Gerenciar implantações → Editar → Nova versão**. O endereço continua o mesmo.

### Segurança
- O código secreto protege a planilha: quem tiver o endereço `/exec` **e** o código consegue ler e gravar tudo. Não compartilhe os dois em grupos nem em repositórios públicos.
- A planilha tem CPFs e telefones. Mantenha-a privada e dê acesso só a quem precisa. Para trocar o código, edite `TOKEN`, publique uma nova versão e reconecte os aparelhos.

---

## 6. Rotina mensal

1. Início do mês: **Pagamentos → Gerar cobranças do mês**.
2. Quando o locatário pagar: **Registrar pagamento** (ou toque no mês no *Calendário*). Informe a **data do pagamento** e a **forma de pagamento**; o recibo abre em seguida.
3. Envie o recibo: **Baixar PDF** (e anexe no WhatsApp ou e-mail), **WhatsApp** (texto), **Copiar texto** ou **Imprimir**.
4. Acompanhe atrasos no **Painel** e no filtro *Atrasado* de Pagamentos.
5. Confira em **Contratos** quais terminam em breve.
6. De vez em quando, use **Exportar backup** (arquivo `.json`). **Importar backup** restaura.

---

## 7. Identidade visual

- Cor principal: **#043C95**. Modo escuro automático, conforme o aparelho (azul mais claro para manter a leitura).
- Cores de situação: verde (pago), amarelo (pendente), vermelho (atrasado).
- Logo CJN no menu, no recibo e nos ícones do app.
- Fontes: Bricolage Grotesque (títulos), IBM Plex Sans (textos) e IBM Plex Mono (valores e números).

---

## 8. Limites e problemas comuns

| Situação | O que fazer |
|---|---|
| "Código de acesso incorreto" | O código digitado no app é diferente do `TOKEN` do script. |
| "Resposta inválida" ou "Sem conexão ou endereço incorreto" | Confira o endereço `/exec` e se a implantação está com acesso **Qualquer pessoa**. Depois de mudar o script, publique uma **nova versão**. |
| "Aba db_... não existe" | Execute a função `setup` no Apps Script. |
| Alterei na planilha e não apareceu | Aguarde 1 minuto ou volte para o app. Confira se a linha tem **Id** e se as datas estão corretas. |
| O app antigo continua aparecendo | Abra com internet para atualizar. Se persistir, desinstale e instale de novo. |
| Dados sumiram do aparelho | Dados locais dependem do navegador. Use a planilha Google ou o backup `.json`. |
| Imprimir não abre | O botão existe só na versão do GitHub. Dentro do Claude use **Baixar PDF**. |
| iPhone não instala | Use o Safari (não o Chrome) e *Adicionar à Tela de Início*. |

Ainda não existe: upload de fotos e PDFs direto no Drive, controle de usuários e senhas, vistorias, reajuste anual automático, dia de vencimento diferente do dia de início do contrato, envio automático de lembretes.

---

## 9. Contexto para continuar o projeto com o Claude

Cole este bloco no início de uma nova conversa (ou nas instruções de um Projeto do Claude), junto com o `index.html` atual.

```
Projeto: CJNProperty, aplicativo web (PWA) para gestão de imóveis alugados, em português do Brasil.
Cor principal #043C95, logo CJN (escudo cinza e azul-marinho). Interface em português, valores em R$, datas dd/mm/aaaa.

Estrutura do index.html (arquivo único):
- Script 1 (camada de armazenamento): IndexedDB local + fila de sincronização com Google Sheets via Apps Script
  (POST text/plain para o endereço /exec com {token, action: ping|list|ops}). Expõe a mesma interface do banco do Claude:
  db.collection(nome).doc(id).set/update/delete, add, onSnapshot.
- Script 2 (aplicativo): estado global D (imoveis, locadores, locatarios, contratos, pagamentos), SCHEMA dos formulários,
  telas vPainel, vImoveis, vContratos, vPessoas, vPagamentos (lista e calendário), vRecibos, openRecibo, extenso().
Coleções e campos:
  imoveis{codigo,endereco,bairro,tipo,aluguel,status,foto}; locadores{nome,doc,pix}; locatarios{nome,cpf,telefone,email,profissao};
  contratos{numero,imovelId,locadorId,locatarioId,entrada,saida,valor,status,pdf};
  pagamentos{contratoId,referencia(AAAA-MM),valor,vencimento,dataPagamento,forma}; id do pagamento = contratoId_AAAA-MM.
Planilha Google: abas db_Imoveis, db_Locadores, db_Locatarios, db_Contratos, db_Pagamentos (script google-sheets/Code.gs).
Regras: vencimento = dia de início do contrato; Pago/Atrasado/Pendente calculado; recibo REC-AAAAMM-XXXX.
Convenções: sem dependências externas além das fontes do Google; todas as cores por variáveis CSS (claro e escuro);
funciona no celular; nunca colocar dados reais, token ou links privados no repositório.
Mudanças no schema devem ser feitas juntas em: SCHEMA (formulário), FIELDS/TYPES (camada de armazenamento) e SCHEMA do Code.gs.
Ao atualizar o app, aumente a versão do cache em sw.js (cjnproperty-vN).
```

Pedidos que o Claude pode atender facilmente: novos campos, novos relatórios (inadimplência, receita por imóvel), reajuste anual de aluguel, vistorias com fotos por link, lembretes por WhatsApp, dia de vencimento por contrato, nova identidade visual.
