"""
Patch idempotente do @graph JSON-LD dos 21 blog posts.

Aplica em todos os blog/{slug}.html (excluindo blog/categoria/*):
1) Inclui "founder" na Organization apontando para #giancarlo
2) Insere no Person #giancarlo logo apos a Organization
3) Inclui "reviewedBy" no no BlogPosting apontando para #giancarlo

NAO ALTERA o campo "author" existente (Organization). Briefing: so trocar
author -> #giancarlo se confirmado que ele escreveu o post (pendencia
herdada que aguarda confirmacao do Lucas post a post). Postura segura:
manter author = Organization + adicionar reviewedBy = #giancarlo.

Datas: nao reescreve datePublished/dateModified pre-existentes - foram
setadas no sprint de frescor. Apenas valida que existem.

Idempotente. Reutilizavel a cada novo post.
"""
import re
from pathlib import Path
import subprocess

POSTS_DIR = Path('blog')

PERSON_NODE = '''    {
      "@id": "https://www.consiliumadvogados.com.br/#giancarlo",
      "@type": "Person",
      "name": "Giancarlo Groth",
      "jobTitle": "Advogado · Responsável técnico",
      "description": "Advogado dedicado ao direito empresarial, com atuação em recuperação de crédito B2B, planejamento sucessório, contratos e acordos de sócios. Responsável técnico da Consilium.",
      "image": "https://www.consiliumadvogados.com.br/assets/grothperfil-960.webp",
      "worksFor": { "@id": "https://www.consiliumadvogados.com.br/#organization" },
      "knowsAbout": [
        "direito empresarial",
        "recuperação de crédito B2B",
        "planejamento sucessório",
        "holding familiar",
        "revisão de contratos empresariais",
        "acordo de sócios",
        "estruturação societária"
      ],
      "identifier": "[OAB/UF nº _____]",
      "url": "https://www.consiliumadvogados.com.br/#responsavel-tecnico"
    },
'''

MEMBEROF_OLD_INDENTED = '''      "memberOf": {
        "@type": "Organization",
        "name": "Ordem dos Advogados do Brasil",
        "alternateName": "OAB"
      }
    },'''

MEMBEROF_NEW_INDENTED = (
    '      "founder": { "@id": "https://www.consiliumadvogados.com.br/#giancarlo" },\n'
    '      "memberOf": {\n'
    '        "@type": "Organization",\n'
    '        "name": "Ordem dos Advogados do Brasil",\n'
    '        "alternateName": "OAB"\n'
    '      }\n'
    '    },\n' + PERSON_NODE.rstrip(',\n') + ','
)

REVIEWED_FIELD = '"reviewedBy": { "@id": "https://www.consiliumadvogados.com.br/#giancarlo" }'

stats = {'founder_person': 0, 'reviewedBy': 0, 'noop': 0, 'no_blogposting': []}

for f in POSTS_DIR.glob('*.html'):
    if 'categoria' in f.name:
        continue
    text = f.read_text(encoding='utf-8')
    original = text

    # 1+2) founder + Person (formato indentado)
    if '"founder": { "@id": "https://www.consiliumadvogados.com.br/#giancarlo" }' not in text:
        if MEMBEROF_OLD_INDENTED in text:
            text = text.replace(MEMBEROF_OLD_INDENTED, MEMBEROF_NEW_INDENTED, 1)
            stats['founder_person'] += 1
        else:
            # Variante: memberOf inline ", "memberOf": { "@type":..., "alternateName": "OAB" }"
            inline_old = '"memberOf": { "@type": "Organization", "name": "Ordem dos Advogados do Brasil", "alternateName": "OAB" }\n    },'
            inline_new = (
                '"founder": { "@id": "https://www.consiliumadvogados.com.br/#giancarlo" },\n'
                '      "memberOf": { "@type": "Organization", "name": "Ordem dos Advogados do Brasil", "alternateName": "OAB" }\n'
                '    },\n' + PERSON_NODE.rstrip(',\n') + ','
            )
            if inline_old in text:
                text = text.replace(inline_old, inline_new, 1)
                stats['founder_person'] += 1

    # 3) reviewedBy no BlogPosting (antes de "author" ou "publisher" como ancora)
    if REVIEWED_FIELD not in text:
        # Localizar o no BlogPosting e inserir reviewedBy antes do primeiro "author"
        # ou, na falta, antes do "publisher" dentro do BlogPosting
        bp_match = re.search(r'"@type":\s*"BlogPosting"', text)
        if bp_match:
            # Procurar dentro do BlogPosting (ate proximo "@type" ou fim do bloco)
            bp_start = bp_match.start()
            # Tentar inserir antes de "author" ainda dentro do BlogPosting
            author_re = re.compile(r'(\n( *))"author":\s*\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*\},', re.DOTALL)
            m = author_re.search(text, bp_start)
            if m:
                indent = m.group(2)
                injection = '\n' + indent + REVIEWED_FIELD + ','
                text = text[:m.start()] + injection + text[m.start():]
                stats['reviewedBy'] += 1
            else:
                # fallback: antes de publisher
                pub_re = re.compile(r'(\n( *))"publisher":\s*\{[^{}]*?\},', re.DOTALL)
                m = pub_re.search(text, bp_start)
                if m:
                    indent = m.group(2)
                    injection = '\n' + indent + REVIEWED_FIELD + ','
                    text = text[:m.start()] + injection + text[m.start():]
                    stats['reviewedBy'] += 1
                else:
                    stats['no_blogposting'].append(f.name)
        else:
            stats['no_blogposting'].append(f.name)

    if text != original:
        f.write_text(text, encoding='utf-8')
    else:
        stats['noop'] += 1

print(f'founder+Person aplicado em: {stats["founder_person"]} posts')
print(f'reviewedBy aplicado em:     {stats["reviewedBy"]} posts')
print(f'sem mudanca:                {stats["noop"]} posts')
if stats['no_blogposting']:
    print(f'BlogPosting nao encontrado em: {stats["no_blogposting"]}')

# Validar datas com git log
print()
print('=== validacao de datas vs git ===')
for f in sorted(POSTS_DIR.glob('*.html')):
    if 'categoria' in f.name:
        continue
    text = f.read_text(encoding='utf-8')
    # datePublished do JSON-LD
    m = re.search(r'"datePublished":\s*"([^"]+)"', text)
    if not m:
        continue
    json_date = m.group(1)[:10]
    # primeiro commit do arquivo
    r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%cs', '--', str(f)],
                       capture_output=True, text=True)
    git_dates = r.stdout.strip().splitlines()
    git_first = git_dates[-1] if git_dates else 'N/A'
    flag = 'OK' if json_date == git_first else 'DIFF'
    print(f'{flag} {f.name}: json={json_date} git_first_commit={git_first}')
