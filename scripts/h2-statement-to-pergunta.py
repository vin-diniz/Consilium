"""
Converte H2 statement/marketing para H2 pergunta pesquisavel
(framework SPIDERRANK v2, §15 Heading-as-Prompt).

Substituicoes conservadoras — so quando a pergunta e clara e natural.
NAO toca em section-headers estruturais legitimos ("Outros servicos
em X", "Atuacao perante TJ-X", "Duvidas tecnicas sobre X em Y",
"Em 4 horas uteis").
"""
from pathlib import Path
import re

# Cada tupla: (regex_do_H2_original, novo_texto_H2). O regex captura
# variacoes de whitespace e break lines (<br>) que o linter frequentemente insere.
CONVERSIONS = [
    # 1. Copy metafórica -> pergunta com o mesmo pain point
    (r'Sociedade sem acordo formal escala impasse\s*(?:<br[^>]*>)?\s*at[ée] a a[cç][ãa]o de dissolu[cç][ãa]o parcial\.?',
     'Por que sociedade sem acordo formal escala para dissolução parcial?'),
    (r'Cr[eé]dito parado [éÉ] cr[eé]dito\s*(?:<br[^>]*>)?\s*caminhando para prescri[cç][ãa]o\.?',
     'Quanto tempo o crédito empresarial resiste antes de prescrever?'),
    (r'Contrato gen[eé]rico [éÉ]\s*(?:<br[^>]*>)?\s*passivo disfar[cç]ado de atalho\.?',
     'Contrato genérico da internet é seguro para uma PME?'),
    (r'Sucess[ãa]o n[ãa]o planejada\s*(?:<br[^>]*>)?\s*[éÉ] preju[íi]zo em dia programado\.?',
     'Qual o custo real da sucessão empresarial sem planejamento?'),
    (r'Sociedade sem acordo\s*(?:<br[^>]*>)?\s*[éÉ] disputa com data marcada\.?',
     'Por que sociedade sem acordo de sócios caminha para litígio?'),
    (r'Sucess[ãa]o [éÉ] decis[ãa]o de vida,\s*(?:<br[^>]*>)?\s*n[ãa]o decis[ãa]o de morte\.?',
     'Sucessão empresarial: por que deve ser decisão de vida, não de morte?'),
    (r'Quadro societ[aá]rio sem acordo\s*(?:<br[^>]*>)?\s*[éÉ] ju[íi]zo esperando o gatilho\.?',
     'Quadro societário sem acordo formal: quais os riscos jurídicos?'),

    # 2. Statement direto -> pergunta canonica
    (r'Cl[aá]usulas essenciais de um acordo de s[oó]cios',
     'Quais cláusulas são essenciais no acordo de sócios?'),
    (r'Apura[cç][ãa]o de haveres: como funciona',
     'Como funciona a apuração de haveres na saída de sócio?'),
    (r'Cobran[cç]a extrajudicial e cobran[cç]a judicial',
     'Cobrança extrajudicial ou judicial: qual escolher em cada caso?'),
    (r'A cadeia da recupera[cç][ãa]o de cr[eé]dito',
     'Como funciona a cadeia de recuperação de crédito empresarial?'),

    # 3. Copy motivacional "Em 4 horas uteis" (CTA-like) -> pergunta tecnica
    (r'Em 4 horas [uú]teis,\s*(?:<br[^>]*>)?\s*sua empresa\s*(?:<br[^>]*>)?\s*(?:conversa com|est[aá] conectada ao) o?\s*especialista certo\.?',
     'Qual o prazo entre o contato inicial e o diagnóstico jurídico?'),
    (r'Em 4 horas [uú]teis,\s*(?:<br[^>]*>)?\s*seu contrato\s*(?:<br[^>]*>)?\s*conversa com o? especialista certo\.?',
     'Qual o prazo do diagnóstico de revisão contratual?'),
    (r'Em 4 horas [uú]teis,\s*(?:<br[^>]*>)?\s*sua fam[íi]lia\s*(?:<br[^>]*>)?\s*(?:conversa com|est[aá] conectada ao) o?\s*especialista certo\.?',
     'Qual o prazo do diagnóstico sucessório após o primeiro contato?'),
    (r'Em 4 horas [uú]teis,\s*(?:<br[^>]*>)?\s*sua sociedade\s*(?:<br[^>]*>)?\s*conversa com o? especialista certo\.?',
     'Qual o prazo do diagnóstico societário após o primeiro contato?'),
]

stats = {'files': 0, 'subs': 0}
per_conv = {i: 0 for i in range(len(CONVERSIONS))}

for f in Path('.').rglob('*.html'):
    if 'node_modules' in f.parts: continue
    text = f.read_text(encoding='utf-8')
    original = text
    for i, (pat, new) in enumerate(CONVERSIONS):
        text, n = re.subn(pat, new, text)
        stats['subs'] += n
        per_conv[i] += n
    if text != original:
        f.write_text(text, encoding='utf-8')
        stats['files'] += 1

print(f'Arquivos modificados: {stats["files"]}')
print(f'H2 convertidos:       {stats["subs"]}')
print()
print('Detalhamento:')
for i, (pat, new) in enumerate(CONVERSIONS):
    n = per_conv[i]
    label = new[:70] + ('...' if len(new) > 70 else '')
    print(f'  {n:4d}x: -> "{label}"')
