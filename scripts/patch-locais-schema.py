"""
Patch idempotente do @graph JSON-LD das paginas localizadas.

Aplica em todas as paginas /servicos/{slug}/{cidade}-{uf}.html:
1) Inclui "founder" na Organization apontando para #giancarlo
2) Insere no Person #giancarlo logo apos a Organization
3) Inclui "reviewedBy" no no Service apontando para #giancarlo
4) Reformula "areaServed" para o padrao [City, AdministrativeArea por extenso]
   removendo containedInPlace e mesorregiao/subrregiao (entidade hiperlocal
   proibida pelo briefing)

Reutilizavel a cada nova leva. NAO duplica mudancas (idempotente).
Suporta variantes inline e multi-linha do JSON-LD.

Pendencia herdada: identifier do Person fica "[OAB/UF nº _____]" ate o
numero real ser informado.
"""
import re
from pathlib import Path

UF_PT = {
    'pr': 'Paraná',
    'rj': 'Rio de Janeiro',
    'mg': 'Minas Gerais',
    'sc': 'Santa Catarina',
}

SERVICOS = [
    'cobranca-empresarial',
    'planejamento-sucessorio-empresarial',
    'revisao-de-contratos-empresariais',
    'acordo-de-socios-e-estruturacao-societaria',
]

PERSON_NODE_MINIFIED = (
    '{"@id":"https://www.consiliumadvogados.com.br/#giancarlo",'
    '"@type":"Person",'
    '"name":"Giancarlo Groth",'
    '"jobTitle":"Advogado · Responsável técnico",'
    '"description":"Advogado dedicado ao direito empresarial, com atuação em recuperação de crédito B2B, planejamento sucessório, contratos e acordos de sócios. Responsável técnico da Consilium.",'
    '"image":"https://www.consiliumadvogados.com.br/assets/grothperfil-960.webp",'
    '"worksFor":{"@id":"https://www.consiliumadvogados.com.br/#organization"},'
    '"knowsAbout":["direito empresarial","recuperação de crédito B2B","planejamento sucessório","holding familiar","revisão de contratos empresariais","acordo de sócios","estruturação societária"],'
    '"identifier":"[OAB/UF nº _____]",'
    '"url":"https://www.consiliumadvogados.com.br/#responsavel-tecnico"}'
)

FOUNDER_FIELD = '"founder":{"@id":"https://www.consiliumadvogados.com.br/#giancarlo"},'
REVIEWED_FIELD = '"reviewedBy":{"@id":"https://www.consiliumadvogados.com.br/#giancarlo"},'

# Padroes de Organization (com ou sem extras antes do memberOf):
# 1) "...,email...memberOf:{...}}" (formato base, ex. SC acordo)
# 2) "...,logo,...,disambiguatingDescription,...memberOf:{...}}" (formato extendido, ex. PR cobranca)
# Estrategia: substituir somente a string '"memberOf":{"@type":"Organization","name":"Ordem dos Advogados do Brasil","alternateName":"OAB"}}'
# por FOUNDER+memberOf+},Person. Ambas variantes terminam igual.

ORG_OLD = '"memberOf":{"@type":"Organization","name":"Ordem dos Advogados do Brasil","alternateName":"OAB"}}'
ORG_NEW = FOUNDER_FIELD + '"memberOf":{"@type":"Organization","name":"Ordem dos Advogados do Brasil","alternateName":"OAB"}},\n' + PERSON_NODE_MINIFIED

# Regex robusta para areaServed (inline ou multilinha, com ou sem subrregiao):
# Captura: "areaServed":[ ... { ... City ... name="X" ... } ... ]
AREA_SERVED_RE = re.compile(
    r'"areaServed":\s*\[\s*'
    r'\{[^{}]*?"@type":"City","name":"(?P<cidade>[^"]+)"[^{}]*?(?:"containedInPlace":\{[^{}]*?"name":"(?P<state>[^"]+)"\})?[^{}]*?\}'
    r'(?:\s*,\s*\{[^{}]*?"@type":"AdministrativeArea","name":"[^"]+"\})?'
    r'\s*\]',
    re.DOTALL
)


changes = {'founder_person': 0, 'reviewedBy_inline': 0, 'reviewedBy_multiline': 0, 'areaServed': 0}

for svc in SERVICOS:
    d = Path(f'servicos/{svc}')
    if not d.is_dir():
        continue
    for f in d.glob('*.html'):
        slug = f.stem
        if not (len(slug) > 3 and slug[-3] == '-' and slug[-2:] in UF_PT):
            continue
        uf = slug[-2:]
        uf_pt = UF_PT[uf]
        text = f.read_text(encoding='utf-8')
        original = text

        # 1+2) founder + Person
        if FOUNDER_FIELD not in text and ORG_OLD in text:
            text = text.replace(ORG_OLD, ORG_NEW, 1)
            changes['founder_person'] += 1

        # 4) areaServed reformulado (regex multilinha)
        # Faz primeiro para criar o anchor "areaServed":[{"@type":"City"... na linha unica
        if 'AdministrativeArea","name":"' + uf_pt + '"' not in text:
            m = AREA_SERVED_RE.search(text)
            if m:
                cidade = m.group('cidade')
                old_block = m.group(0)
                new_block = (
                    '"areaServed":[{"@type":"City","name":"' + cidade + '"},'
                    '{"@type":"AdministrativeArea","name":"' + uf_pt + '"}]'
                )
                text = text.replace(old_block, new_block, 1)
                changes['areaServed'] += 1

        # 3) reviewedBy - aplicar antes de areaServed (que agora esta inline)
        if REVIEWED_FIELD not in text:
            # Tentar inline (apos areaServed reformulado)
            new_text = text.replace(
                ',"areaServed":[{"@type":"City"',
                ',' + REVIEWED_FIELD[:-1] + ',"areaServed":[{"@type":"City"',
                1,
            )
            if new_text != text:
                text = new_text
                changes['reviewedBy_inline'] += 1
            else:
                # Tentativa fallback: inserir antes de "provider":{"@id":...}
                new_text = text.replace(
                    ',"provider":{"@id":"https://www.consiliumadvogados.com.br/#organization"}',
                    ',' + REVIEWED_FIELD[:-1] + ',"provider":{"@id":"https://www.consiliumadvogados.com.br/#organization"}',
                    1,
                )
                if new_text != text:
                    text = new_text
                    changes['reviewedBy_multiline'] += 1

        if text != original:
            f.write_text(text, encoding='utf-8')

print(f'founder+Person aplicado em:        {changes["founder_person"]} paginas')
print(f'reviewedBy inline aplicado em:     {changes["reviewedBy_inline"]} paginas')
print(f'reviewedBy fallback aplicado em:   {changes["reviewedBy_multiline"]} paginas')
print(f'areaServed reformulado em:         {changes["areaServed"]} paginas')
