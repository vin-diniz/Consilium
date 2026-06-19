"""
PARTE A do briefing CTA: insere CTA dual (WhatsApp primario + formulario
secundario) nas 252 paginas localizadas.

2 posicoes por pagina (briefing §A):
1) CTA-TOPO: logo apos a intro (hero subtitle + intro do servico),
   antes do bloco svc-strip.
2) CTA-FIM: dentro do svc-final-cta existente, substituindo o botao
   unico por dual.

Marcadores idempotentes:
- <!-- CTA-TOPO:START --> ... <!-- CTA-TOPO:END -->
- <!-- CTA-FIM:START --> ... <!-- CTA-FIM:END -->

Reusa classes do design system: .btn--primary (preenchido) + .btn--ghost
(contorno), envolvidos por .cta-group.

Atribuicao de lead: default (briefing) -> mensagem exata + evento de
clique (dataLayer push se houver GA/GTM). NAO contextualiza por servico/
cidade no texto (aguarda OK do Lucas conforme briefing).
"""
from pathlib import Path
import re

WA_LINK = "https://wa.me/554198303552?text=Ol%C3%A1%2C%20vim%20atrav%C3%A9s%20do%20seu%20site%20Consilium%20e%20gostaria%20de%20atendimento"
DATA_LAYER = "window.dataLayer&&window.dataLayer.push({event:'whatsapp_cta',page_path:location.pathname});"

CTA_TOPO_BLOCK = f'''
        <!-- CTA-TOPO:START -->
        <div class="cta-group reveal-instant" style="margin-top: 28px;">
          <a href="{WA_LINK}" class="btn btn--primary" data-cta-primario="whatsapp" target="_blank" rel="noopener nofollow" onclick="{DATA_LAYER}">
            Avaliar a viabilidade do meu caso
          </a>
          <a href="/#contato" class="btn btn--ghost">Enviar pelo formulário</a>
        </div>
        <!-- CTA-TOPO:END -->
'''

# Para o CTA-FIM, substituimos o conteudo entre os marcadores ja inseridos
# (na primeira execucao, criamos os marcadores e o conteudo de uma so vez)
CTA_FIM_BLOCK = f'''<!-- CTA-FIM:START -->
          <div class="cta-group" style="justify-content: center;">
            <a href="{WA_LINK}" class="btn btn--primary btn--large" data-cta-primario="whatsapp" target="_blank" rel="noopener nofollow" onclick="{DATA_LAYER}">
              Avaliar a viabilidade do meu caso
            </a>
            <a href="/#contato" class="btn btn--ghost">Enviar pelo formulário</a>
          </div>
          <!-- CTA-FIM:END -->'''

SERVICOS = [
    'cobranca-empresarial',
    'planejamento-sucessorio-empresarial',
    'revisao-de-contratos-empresariais',
    'acordo-de-socios-e-estruturacao-societaria',
]

stats = {'topo_inserted': 0, 'topo_skip_existing': 0, 'topo_no_anchor': [],
         'fim_replaced': 0, 'fim_no_anchor': []}

# Padroes para inserir CTA-TOPO: APOS a primeira </section> (hero) ou apos o svc-strip
# Estrategia: inserir antes do primeiro `<section class="section"` que vem depois do hero
# Mais seguro: inserir como bloco DENTRO do container do hero, depois do .page-hero__meta
# Padrao concreto observado: </section> de fechamento do .page-hero seguido por proxima secao

# Para CTA-FIM: substituir o conteudo do svc-final-cta. Padroes observados:
# - <div class="svc-final-cta reveal">...<a href="/#contato" class="btn btn--primary btn--large">...</a>...</div>
# Estrategia: substituir o primeiro <a class="btn btn--primary btn--large"> com href /#contato
# por DOIS botoes (dual)

# Para idempotencia: se ja existe CTA-TOPO:START, nao re-inserir.

for svc in SERVICOS:
    d = Path(f'servicos/{svc}')
    if not d.is_dir():
        continue
    for f in d.glob('*.html'):
        if not re.match(r'.+-[a-z]{2}\.html$', f.name):
            continue
        text = f.read_text(encoding='utf-8')
        original = text

        # ── CTA-TOPO ────────────────────────────────────────────────
        if '<!-- CTA-TOPO:START -->' not in text:
            # Insere logo apos o ultimo </p> da meta-data do hero
            # (publicado em / atualizado em).
            m_meta = re.search(
                r'<p class="meta-data reveal-instant"[^>]*>.*?</p>',
                text,
                re.DOTALL,
            )
            # Fallback: page-hero__meta (paginas mais antigas sem meta-data)
            if not m_meta:
                m_meta = re.search(
                    r'<p class="page-hero__meta"[^>]*>.*?</p>',
                    text,
                    re.DOTALL,
                )
            # Fallback 2: hero__ctas (insere depois dos CTAs originais do hero)
            if not m_meta:
                m_meta = re.search(
                    r'<div class="hero__ctas[^"]*"[^>]*>.*?</div>',
                    text,
                    re.DOTALL,
                )
            if m_meta:
                insertion_point = m_meta.end()
                text = text[:insertion_point] + CTA_TOPO_BLOCK + text[insertion_point:]
                stats['topo_inserted'] += 1
            else:
                stats['topo_no_anchor'].append(f.name)
        else:
            stats['topo_skip_existing'] += 1

        # ── CTA-FIM ─────────────────────────────────────────────────
        if '<!-- CTA-FIM:START -->' not in text:
            # Substitui o botao unico no svc-final-cta por dual
            # Padrao concreto (de spot-check):
            # <a href="/#contato" class="btn btn--primary btn--large">[CONTEUDO]</a>
            # dentro de uma seção svc-final-cta. Tem variantes com SVG dentro.
            # Estrategia: substituir o primeiro href="/#contato" class="btn btn--primary btn--large"
            # ate o </a> correspondente.

            # Regex tolerante a SVG/whitespace internos:
            m = re.search(
                r'<a href="/#contato"\s+class="btn btn--primary btn--large"[^>]*>(?:[^<]|<(?!/a>))*</a>',
                text,
                re.DOTALL,
            )
            if m:
                text = text[:m.start()] + CTA_FIM_BLOCK + text[m.end():]
                stats['fim_replaced'] += 1
            else:
                stats['fim_no_anchor'].append(f.name)

        if text != original:
            f.write_text(text, encoding='utf-8')

print(f'CTA-TOPO inserido em:           {stats["topo_inserted"]} paginas')
print(f'CTA-TOPO ja existia (skip):     {stats["topo_skip_existing"]} paginas')
print(f'CTA-TOPO sem ancora:            {len(stats["topo_no_anchor"])} (amostra: {stats["topo_no_anchor"][:3]})')
print(f'CTA-FIM substituido (dual) em:  {stats["fim_replaced"]} paginas')
print(f'CTA-FIM sem ancora:             {len(stats["fim_no_anchor"])} (amostra: {stats["fim_no_anchor"][:3]})')
