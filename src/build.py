"""Monta os dois arquivos finais a partir de uma única base:
   - ../gestao-imobiliaria.html            (publicado dentro do Claude, usa o banco do Claude)
   - ../cjnproperty-pwa/index.html         (PWA para o GitHub Pages: IndexedDB + Google Sheets)
Uso: PWA_OUT=.. python3 build.py   (gera ../index.html; sem PWA_OUT grava também ../gestao-imobiliaria.html)
"""
import json, os, importlib.util, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location('recibo', os.path.join(HERE, 'recibo_patch.py'))
recibo = importlib.util.module_from_spec(spec); sys.argv = [sys.argv[0]]; spec.loader.exec_module(recibo)

base = open(os.path.join(HERE, 'app.base.html')).read()
app = recibo.patch(base)

# rodapé do menu (só o PWA define window.footHtml) e estilos do rodapé
a = ".join('');\n  if(!db)"
assert a in app
app = app.replace(a, ".join('')+(window.footHtml?window.footHtml():'');\n  if(!db)", 1)
css = '''.foot{margin-top:18px;display:flex;flex-direction:column;gap:6px;border-top:1px solid var(--line);padding-top:12px}
nav.side .foot button{font-size:12px;border:1px solid var(--line);justify-content:center}
.fst{font-size:11px;color:var(--muted);line-height:1.3;word-break:break-word}.fst.bad{color:var(--bad)}
@media (max-width:760px){.foot{flex-direction:row;margin:0 0 0 8px;border:0;padding:0}.foot .fst{display:none}}
'''
a = '@media (max-width:760px){\n  .shell'
assert a in app
app = app.replace(a, css + a, 1)

# --- versão do Claude ---
if not os.environ.get('PWA_OUT'): open(os.path.join(ROOT, 'gestao-imobiliaria.html'), 'w').write(app)

# --- versão PWA ---
_sd = os.environ.get('SEED') or os.path.join(HERE, 'seed.json')
if not os.path.exists(_sd): _sd = os.path.join(HERE, 'seed_public.json')
seed = json.load(open(_sd))
shim = open(os.path.join(HERE, 'shim.js')).read().replace('__SEED__', json.dumps(seed, ensure_ascii=False))
head = '''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<style>:root{color-scheme:dark;background:#000;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}body{margin:0}</style>
'''
marker = '<script>\nconst LOGO='
assert marker in app
pwa = head + app.replace(marker, '<script>\n' + shim + '</script>\n' + marker, 1) + '\n</body></html>\n'
open(os.path.join(os.environ.get('PWA_OUT') or os.path.join(ROOT, 'cjnproperty-pwa'), 'index.html'), 'w').write(pwa)
print('ok', len(app), len(pwa))
