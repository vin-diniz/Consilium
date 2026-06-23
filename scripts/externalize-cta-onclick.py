"""
Externaliza onclick="window.dataLayer..." (252 locais + home + outras) para
/assets/js/cta-tracking.js. Necessario para CSP script-src 'self' funcionar
sem 'unsafe-inline' (VULN-003, Tarefa B).

1) Remove o onclick="window.dataLayer&&window.dataLayer.push({event:'whatsapp_cta',page_path:location.pathname});"
   de todas as tags <a> (substitui por nada - o data-cta-primario="whatsapp" ja existe e e o seletor).
2) Injeta <script src="/assets/js/cta-tracking.js" defer></script> antes do </body>
   em arquivos que tinham o onclick e ainda nao tem o script. Idempotente.
"""
from pathlib import Path
import re

ONCLICK_PATTERN = re.compile(
    r'\s*onclick="window\.dataLayer&amp;&amp;window\.dataLayer\.push\(\{event:\'whatsapp_cta\',page_path:location\.pathname\}\);"'
    r'|'
    r'\s*onclick="window\.dataLayer&&window\.dataLayer\.push\(\{event:\'whatsapp_cta\',page_path:location\.pathname\}\);"'
)
SCRIPT_TAG = '  <script src="/assets/js/cta-tracking.js" defer></script>\n'

stats = {'onclick_removed': 0, 'script_added': 0, 'already_had_script': 0}
files_touched = []

for f in Path('.').rglob('*.html'):
    if 'node_modules' in f.parts:
        continue
    text = f.read_text(encoding='utf-8')
    original = text

    # 1) Remove onclick
    new_text, n = ONCLICK_PATTERN.subn('', text)
    if n > 0:
        stats['onclick_removed'] += n
        text = new_text

    # 2) Injeta script se o arquivo USA o data-cta-primario="whatsapp" e ainda nao tem o script
    needs_script = 'data-cta-primario="whatsapp"' in text
    has_script = 'cta-tracking.js' in text

    if needs_script and not has_script:
        # Inserir antes do </body>
        if '</body>' in text:
            text = text.replace('</body>', SCRIPT_TAG + '</body>', 1)
            stats['script_added'] += 1
    elif needs_script and has_script:
        stats['already_had_script'] += 1

    if text != original:
        f.write_text(text, encoding='utf-8')
        files_touched.append(str(f))

print(f'onclick removidos: {stats["onclick_removed"]}')
print(f'script injetado em: {stats["script_added"]} arquivos')
print(f'script ja existia em: {stats["already_had_script"]} arquivos')
print(f'arquivos modificados: {len(files_touched)}')
