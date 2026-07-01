"""
Adiciona o no Person canonico #giancarlo (OAB/PR 122.982) e o
reviewedBy no schema das paginas CollectionPage / Blog:
- blog.html (feed)
- blog/categoria/{cobranca, contratos, societario, sucessao}.html

Idempotente. Nao mexe em arquivos que ja tenham #giancarlo.
"""
from pathlib import Path
import re
import json

PERSON_NODE = '''    {
      "@id": "https://www.consiliumadvogados.com.br/#giancarlo",
      "@type": "Person",
      "name": "Giancarlo Groth",
      "jobTitle": "Advogado · Responsável técnico",
      "description": "Advogado dedicado ao direito empresarial, com cinco anos de atuação em cobrança B2B, sucessão, contratos e acordos de sócios. Responsável técnico da Consilium.",
      "image": "https://www.consiliumadvogados.com.br/assets/grothperfil-960.webp",
      "worksFor": { "@id": "https://www.consiliumadvogados.com.br/#organization" },
      "alumniOf": "[instituição]",
      "knowsAbout": [
        "direito empresarial",
        "recuperação de crédito B2B",
        "planejamento sucessório",
        "holding familiar",
        "revisão de contratos empresariais",
        "acordo de sócios",
        "estruturação societária"
      ],
      "identifier": "OAB/PR 122.982",
      "url": "https://www.consiliumadvogados.com.br/sobre",
      "sameAs": ["https://giacomelliadvocacia.com.br"]
    },
'''

REVIEWEDBY_LINE = '      "reviewedBy": { "@id": "https://www.consiliumadvogados.com.br/#giancarlo" },\n'

targets = [
    'blog.html',
    'blog/categoria/cobranca.html',
    'blog/categoria/contratos.html',
    'blog/categoria/societario.html',
    'blog/categoria/sucessao.html',
]

for path in targets:
    p = Path(path)
    text = p.read_text(encoding='utf-8')

    if '#giancarlo' in text:
        print(f'SKIP {path} (ja tem #giancarlo)')
        continue

    # 1. Inserir Person apos Organization node
    # O padrao termina com "memberOf": {...} \n      } \n \n      { ... proximo no
    # Localiza fecho da Organization: precisa achar "memberOf" e depois o }
    # seguido por outra { que abre o proximo no.
    org_end_pattern = re.compile(
        r'("memberOf":\s*\{\s*"@type":\s*"Organization",\s*"name":\s*"Ordem dos Advogados do Brasil",\s*"alternateName":\s*"OAB"\s*\}\s*\},\s*\n\s*\n\s*)(\{)',
        re.DOTALL
    )
    match = org_end_pattern.search(text)
    if not match:
        # Tenta padrao mais generico: fim de organization com founder+memberOf
        org_end_pattern2 = re.compile(
            r'("alternateName":\s*"OAB"\s*\}\s*\},?\s*\n\s*\n?\s*)(\{\s*"@type":\s*"(?:WebPage|CollectionPage))',
            re.DOTALL
        )
        match = org_end_pattern2.search(text)
        if not match:
            print(f'FAIL {path}: nao achou fim da Organization')
            continue

    insertion_point = match.end(1)
    text = text[:insertion_point] + PERSON_NODE + text[insertion_point:]

    # 2. Adicionar reviewedBy no no principal (Blog para blog.html, CollectionPage para categorias)
    if path.endswith('blog.html'):
        # Adiciona no Blog node antes do "author"
        blog_pattern = re.compile(
            r'(\{\s*"@type":\s*"Blog",\s*\n\s*"@id":\s*"[^"]+",\s*\n\s*"name":[^\n]+\n\s*"description":[^\n]+\n\s*"url":[^\n]+\n\s*"inLanguage":[^\n]+\n\s*"publisher":[^\n]+\n\s*)(\s*"author":)',
        )
        m = blog_pattern.search(text)
        if m:
            text = text[:m.end(1)] + REVIEWEDBY_LINE + text[m.end(1):]
        else:
            # Fallback: adiciona antes do primeiro "author" apos "@type": "Blog"
            m2 = re.search(r'"@type":\s*"Blog"', text)
            if m2:
                author_after = re.search(r'"author":', text[m2.end():])
                if author_after:
                    pos = m2.end() + author_after.start()
                    # Encontra inicio de linha
                    line_start = text.rfind('\n', 0, pos) + 1
                    text = text[:line_start] + REVIEWEDBY_LINE + text[line_start:]
    else:
        # CollectionPage: adiciona antes do "significantLink" ou antes do "}"
        cp_pattern = re.compile(
            r'(\{\s*"@type":\s*"CollectionPage",[^{}]*?"inLanguage":[^\n]+\n)(\s*"datePublished")',
            re.DOTALL
        )
        m = cp_pattern.search(text)
        if m:
            text = text[:m.end(1)] + REVIEWEDBY_LINE + text[m.end(1):]
        else:
            # Fallback: apos "mainEntity"
            cp2 = re.search(r'("mainEntity":\s*\{\s*"@id":[^}]+\}\s*,\s*\n)', text)
            if cp2:
                text = text[:cp2.end()] + REVIEWEDBY_LINE + text[cp2.end():]

    # Valida JSON-LD
    scripts = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>\s*(.*?)\s*</script>', text, re.DOTALL)
    all_valid = True
    for s in scripts:
        try:
            json.loads(s)
        except Exception as e:
            print(f'FAIL {path}: JSON-LD invalido apos insercao: {e}')
            all_valid = False
            break

    if all_valid:
        p.write_text(text, encoding='utf-8')
        print(f'OK   {path}')
    else:
        print(f'SKIP {path} (JSON invalido, nao salvo)')
