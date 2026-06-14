# Ciclo de republicação — hubs (trimestral)

A cada trimestre, por hub (ordem por volume de impressão e prioridade GSC: sucessório → acordo de sócios → contratos → cobrança):

1. Revisar dados/estatísticas e citações legais (atualizar nº de lei, súmula, REsp se houver mudança).
2. Adicionar 1 bloco novo ou reescrever 1 seção (sinal real de atualização, não troca cosmética de data).
3. Atualizar `<time dateModified>` visível **E** `dateModified` no JSON-LD (devem bater).
4. Reenviar a URL no GSC (Inspeção de URL → Solicitar indexação).

**Datas-alvo:** mar / jun / set / dez.

---

## Regras de hygiene quando atualizar

- `datePublished` **nunca muda** depois de publicada a página (só corrige se foi inserida errada).
- `dateModified` reflete a data do commit que carrega a alteração real de conteúdo.
- Para páginas com `<time itemprop="dateModified">` no HTML, atualizar simultaneamente:
  - atributo `datetime="YYYY-MM-DD"`
  - texto humano "Atualizado em DD de mês de YYYY"
  - campo `"dateModified"` no JSON-LD (`@type": "WebPage"` ou `"BlogPosting"`)

## Sanity check antes de commitar republicação

```bash
# 1. data visivel bate com JSON-LD?
grep -oE 'datetime="[0-9-]+"' caminho/da/pagina.html
grep -oE '"dateModified":\s*"[0-9-]+' caminho/da/pagina.html

# 2. ultima data real do arquivo no git
git log -1 --format=%cs -- caminho/da/pagina.html
```

## Lote inicial padronizado

Hubs e páginas locais foram padronizadas em 2026-06-14 com:

- Hubs: `datePublished=2026-04-19`, `dateModified=2026-06-14`
- Páginas locais (252): `datePublished=2026-05-28`, `dateModified=2026-06-14`
- Posts blog (21): mantêm `datePublished` original; `dateModified` atualizado no ciclo de revisão.

## Quando republicar fora do trimestre

- Mudança na legislação citada na página (lei, decreto, súmula).
- Decisão relevante do STJ ou STF que afete o tema.
- Erro factual reportado.
- Reescrita estrutural do conteúdo (não troca cosmética).

Sempre que houver mudança real, atualizar ambos (`<time>` visível e JSON-LD).
