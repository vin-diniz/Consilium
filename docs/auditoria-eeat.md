# Auditoria de aplicação + conformidade E-E-A-T

**Data:** 2026-06-18 · **Repo:** `vin-diniz/Consilium` em `main` (commit `422c5c0`) · **Escopo:** site inteiro publicado no Cloudflare Pages.

**Legenda:** ✓ aplicado · ⚠ aplicado com problema · ✘ ausente · ⏳ briefado, não executado.

---

## §0 · Inventário de estado

| Camada | Estado | Evidência |
|---|---|---|
| 20 commits | ✓ pushed em `main` | `git log --oneline -20`: do `422c5c0` (núcleo Person) até `d73ddc5` (Tier 2 SC) |
| Home | ✓ | `index.html` 46 KB |
| 4 hubs de serviço | ✓ | `servicos/*.html` (cobranca, planejamento, revisao, acordo) |
| 252 páginas localizadas | ✓ | `servicos/{slug}/*.html` (88+88+38+38) |
| 21 blog posts | ✓ | `blog/*.html` exceto `categoria/` |
| 5 páginas de categoria blog | ✓ | `blog/categoria/*.html` |
| `privacidade.html` | ✓ (com Person canônico §5) | `privacidade.html` 47 KB |
| `sobre.html` | ⚠ existe mas é **AboutPage da Consilium**, NÃO ProfilePage do Giancarlo (núcleo §4) | `sobre.html`:1 — schema tem `AboutPage + Article + ItemList + HowTo + FAQPage` mas **0 ocorrências de `#giancarlo` ou `OAB/PR 122.982`** |
| Scripts idempotentes em `/scripts/` | ✓ | `build-city-{accordions,clusters}.mjs`, `patch-{locais,posts}-schema.py` |
| `docs/republicacao.md` | ✓ | `docs/republicacao.md` 2 KB |

---

## §1 · Verificação de aplicação

| Item | Status | Evidência | Observação |
|---|---|---|---|
| Fontes enxutas (5 pesos) | ✓ | `index.html`:94 — `Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@400;500;600` | confere com sprint perf |
| Hero AVIF + preload | ✓ | `index.html`:89 — `<link rel="preload" as="image" href="/assets/hero_bg.avif" type="image/avif" fetchpriority="high">` | LCP path mantido |
| Foto do responsável otimizada | ✓ | `assets/grothperfil-{480,960}.{avif,webp,jpg}`: 9.8K / 10K / 28K / 29K / 51K | `grothperfil.jpg` cru não referenciado em nenhum HTML |
| Estatísticas preenchidas | ✓ | `grep VALIDAR` em `--include='*.html'` retorna vazio | Sebrae/Serasa/IBGE/CNJ presentes na home (4 menções) |
| CTA WhatsApp | ✓ | `index.html` tem 1 ocorrência de `wa.me/554198303552`; `whatsapp-pendente` retorna vazio | TODO restante (1) é o link `/sobre` da pendência #4, **não** WA |
| OAB sem placeholder | ✓ | `grep OAB/__\|_____\|\[OAB` vazio; `OAB/PR 122.982` presente em **279 arquivos** | uniforme |
| Schema enxugado na home | ✓ | 4 nós no `@graph`: `Organization, Person, WebSite, WebPage` | sem Services × 3, sem FAQPage duplicada |
| Sanfona/cluster (linking) | ✓ | 4/4 hubs com `CIDADES:START`; cluster + voltar-hub em amostras de locais | scripts em `/scripts/` |
| Datas (`<time>` ↔ schema) | ✓ | hub cobrança: `<time datetime="2026-06-14" itemprop="dateModified">` ↔ `"dateModified": "2026-06-14T00:00:00-03:00"` | bate |

---

## §2 · Auditoria E-E-A-T

### §2.1 Authoritativeness — consistência de entidade (o maior risco)

| Check | Resultado | Evidência |
|---|---|---|
| `Person.@id` único | ✓ 1 valor (2 grafias: indentado/minificado) | `"@id": "https://www.consiliumadvogados.com.br/#giancarlo"` |
| `Person.name` único | ✓ `"Giancarlo Groth"` | nenhuma variação encontrada |
| OAB única | ✓ `OAB/PR 122.982` | nenhuma divergência |
| `Organization.@id` único | ✓ `https://www.consiliumadvogados.com.br/#organization` | uniforme |
| Logo único | ✓ `assets/logo-consilium.svg` | uniforme |
| `Person` concorrente com nome/OAB divergente | ✓ não encontrado | grep não retornou variantes |

**Conclusão §2.1:** entidade canônica fechada. Google e AI Overviews leem a Consilium e o Dr. Giancarlo como **uma entidade única** em 279 páginas — exatamente o que o núcleo §1 (regra de ouro) exige.

### §2.2 Expertise

| Check | Resultado | Evidência |
|---|---|---|
| `reviewedBy → #giancarlo` em páginas de conteúdo | ✓ | 278 arquivos com `reviewedBy` (apontando para `#giancarlo` em todos) |
| `#giancarlo` presente em todas as páginas | ✓ 279 arquivos | home + 4 hubs + 252 locais + 21 posts + privacidade |
| `jobTitle` padronizado | ✓ `"Advogado · Responsável técnico"` (1 string canônica) | amostras coincidem |
| `knowsAbout` no Person | ✓ 7 itens em todas as amostras | direito empresarial + cobrança B2B + sucessão + holding familiar + revisão de contratos + acordo de sócios + estruturação societária |
| Bio na home | ✓ | `index.html` bloco `#responsavel-tecnico` (h1+badge+bio+link) |
| Bio na `/sobre` | ⚠ a página existe mas **não traz o Person canônico nem a OAB visível** | `sobre.html`: 0 menções a Giancarlo ou 122.982 |
| `author` nos posts | ⚠ inconsistente — **dois autores diferentes** sem confirmação editorial: 12 posts com `author=#organization` + 9 posts com `author="Equipe Editorial Consilium"` (Person fictícia) | ver tabela abaixo |

#### Detalhe `author` por post (21 posts)

| Posts com `author=#organization` (12) | Posts com `author="Equipe Editorial Consilium"` (9) |
|---|---|
| acao-monitoria-quando-usar-no-lugar-da-acao-de-cobranca | acordo-socios-cooperativa-vs-ltda-maringa |
| apuracao-de-haveres-como-funciona | clausulas-contratos-saude-educacao-londrina |
| clausulas-essenciais-contratos-b2b | cobranca-cadeia-automotiva-curitiba |
| cobranca-empresarial-como-recuperar-credito | desconsideracao-da-personalidade-juridica-quando-atinge-o-socio |
| dissolucao-parcial-de-sociedade | holding-rural-sucessao-cascavel |
| drag-along-acordo-de-socios | mapeamento-juridico-de-riscos-empresariais |
| empresa-processada-por-dano-moral | o-que-sao-haveres-e-por-que-precisam-ser-pagos |
| holding-familiar-quando-estruturar | reestruturacao-de-passivos-empresariais |
| modelo-de-contrato-internet-nao-protege | sucessao-empresarial-por-obito-sem-planejamento |
| prazos-prescricionais-creditos-empresariais | |
| protocolo-familiar-o-que-e-validade-juridica | |
| revisao-de-contrato-empresarial-quando-e-possivel | |

> **Pendência editorial:** confirmar com o Lucas, post a post, quais foram escritos pelo Giancarlo e trocar `author` para `#giancarlo`. Os 9 com `author="Equipe Editorial Consilium"` são particularmente problemáticos: "Equipe Editorial Consilium" é uma Person fictícia sem `@id` canônico, fragmenta o knowledge graph e não corresponde a uma pessoa real (afronta integridade + 205).

### §2.3 Trustworthiness

| Check | Resultado | Evidência |
|---|---|---|
| Foto real e profissional | ✓ | `assets/grothperfil-960.avif` 28 KB + `grothperfil-960.webp` 29 KB. Headshot institucional (otimizado a partir do original 3744×5616 / 18 MB) |
| `alt` da foto | ✓ `"Giancarlo Groth, advogado responsável técnico da Consilium"` | `index.html` no bloco `#responsavel-tecnico` |
| OAB visível nos pontos previstos | ✓ | 5 ocorrências de `OAB/PR&nbsp;122.982` no HTML visível da home (hero capsule, bloco do responsável, "Como funciona", 2 FAQs) |
| Footer com disclaimer Provimento 205 + LGPD | ✓ | `index.html`:698 — "Em conformidade com o Provimento 205/2021 do Conselho Federal da OAB" |
| Sem `aggregateRating` real | ✓ | `grep` retorna 1 falso positivo: comentário HTML em `index.html`:106 (`<!-- Sem aggregateRating, sem PostalAddress, sem SearchAction -->`). Nenhum nó real |
| Sem `PostalAddress` | ✓ | nenhum HTML do site contém |
| Sem `SearchAction` | ✓ | nenhum HTML do site contém |
| Marketing speak proibido (gratuit/líder/melhor escritório/maior escritório/garantia de êxito) | ✓ ausente em contexto autorreferente | 4 ocorrências de "gratuit/grátis" — todas em **contextos descritivos/educacionais** (não promessa do serviço): `blog/holding-familiar` "Holding não é grátis" (custo do instituto), `blog/modelo-de-contrato` "modelos disponíveis gratuitamente na internet" (descrição factual), `index.html` "garantia de resultado futuro" (disclaimer **negando** promessa), `privacidade.html` "direitos gratuitos" (terminologia LGPD do titular de dados) |
| "melhor" em contexto | ⚠ 26 ocorrências — **revisar uma a uma** | distribuição em hubs/locais/posts; nenhuma identificada como autorreferente ("melhor escritório") em sprints anteriores, mas merece varredura focada (ex.: `melhor entrega o caso`, `melhor previsibilidade` são técnicas, não promocionais) |
| Estatísticas com fonte+ano | ✓ 4 menções na home (Sebrae 2024, Serasa Experian 2025, IBGE, Banco Mundial, CNJ Justiça em Números) — sem número solto | sprint anterior |
| CTA `wa.me` aberto manualmente | ⏳ não testável por automação | recomendar teste manual em mobile e desktop |

### §2.4 Experience / Freshness

| Check | Resultado | Evidência |
|---|---|---|
| `<time>` visível ↔ `dateModified` schema | ✓ amostra confere | hub cobrança: `datetime="2026-06-14"` ↔ `"dateModified": "2026-06-14T00:00:00-03:00"` |
| `docs/republicacao.md` | ✓ existe (ciclo trimestral mar/jun/set/dez) | `docs/republicacao.md` 2074 bytes |

---

## §3 · Validação de schema (JSON.parse em 6 amostras)

| Arquivo | Parse | Nós no @graph | Person.@id correto | aggregateRating | PostalAddress | SearchAction |
|---|---|---|---|---|---|---|
| `index.html` | OK | Organization, Person, WebSite, WebPage | YES | no | no | no |
| `servicos/cobranca-empresarial.html` | OK | WebSite, LegalService/Organization, Person, WebPage, BreadcrumbList, Service, Article, HowTo, FAQPage | YES | no | no | no |
| `servicos/cobranca-empresarial/joinville-sc.html` | OK | WebSite, LegalService/Organization, Person, WebPage, BreadcrumbList, Service, FAQPage | YES | no | no | no |
| `servicos/acordo-de-socios-e-estruturacao-societaria/florianopolis-sc.html` | OK | WebSite, LegalService/Organization, Person, WebPage, BreadcrumbList, Service, FAQPage | YES | no | no | no |
| `blog/dissolucao-parcial-de-sociedade.html` | OK | WebSite, LegalService/Organization, Person, WebPage, BreadcrumbList, BlogPosting, FAQPage | YES | no | no | no |
| `sobre.html` | OK | WebSite, LegalService/Organization, **AboutPage**, Article, ItemList, BreadcrumbList, HowTo, FAQPage | **NO** (sem Person `#giancarlo`) | no | no | no |

**Conclusão §3:** 5 de 6 amostras conformes. **`sobre.html` é a divergência crítica.**

---

## §4 · Conferência manual (registrar como pendência)

| Item | Status | Observação |
|---|---|---|
| Nome exibido bate com registro OAB/PR 122.982 | ⏳ pendente | consultar a página pública da OAB/PR; se o registro for "Giancarlo Giacomelli" ou outra grafia, padronizar `Person.name` em 279 páginas (mesmo padrão do sprint de OAB). Pendência conhecida do núcleo §6 |
| Foto é headshot profissional sóbrio | ✓ a partir do `grothperfil.jpg` original (3744×5616) — recomenda-se conferência humana do AVIF/WebP de 960px renderizado | abrir `assets/grothperfil-960.webp` em browser e validar |
| Bio lê como sóbria/credível | ✓ revisado nos sprints | "Advogado dedicado ao direito empresarial, com cinco anos de atuação em cobrança B2B, sucessão, contratos e acordos de sócios. Responsável técnico da Consilium." — sóbrio, sem hype |
| `author` vs `reviewedBy` correto por post | ⏳ pendente confirmação editorial | tabela em §2.2 |

---

## Bloqueadores de publicação

1. **`sobre.html` é AboutPage da Consilium, não ProfilePage do Giancarlo.**
   - Em 279 páginas, `Person.url = "https://www.consiliumadvogados.com.br/sobre"`.
   - Ao acessar `/sobre`, **não há referência a Giancarlo, OAB, foto ou bio**.
   - Knowledge graph fica suspenso no ar (referência sem destino concreto).
   - **Bloqueia E-E-A-T** porque o Google segue o `url` do Person e não encontra a entidade.
   - **Correção:** reescrever `sobre.html` como `ProfilePage` com `Person.@id #giancarlo` como `mainEntity` (núcleo §4). Briefing dedicado ainda não executado.

2. **`author` em 9 posts aponta para "Equipe Editorial Consilium" — Person fictícia sem `@id`.**
   - Fragmenta o knowledge graph (uma Person sem `@id` canônico não conecta com `#giancarlo`).
   - Pode ser interpretado como atribuição de autoria falsa.
   - **Correção:** confirmar com o Lucas, post a post; trocar para `author = #giancarlo` onde aplicável, ou trocar para `author = #organization` (mesma postura dos outros 12 posts) onde Giancarlo não escreveu.

---

## Correções sugeridas (para um sprint próprio)

| Prioridade | Item | Esforço |
|---|---|---|
| **Crítica** | Reescrever `sobre.html` como `ProfilePage` com Person canônico como `mainEntity`, com foto otimizada, bio, OAB visível, formação, sameAs reais | sprint dedicado (briefing existente do núcleo §4) |
| **Crítica** | Auditoria editorial de autoria post a post (21 posts) com o Lucas e troca de `author` para `#giancarlo` ou `#organization` conforme realidade | 1 sessão editorial + 1 commit |
| Alta | Remover/refatorar uso de "Equipe Editorial Consilium" como Person fictícia em 9 posts | bate junto com item anterior |
| Média | Varredura manual das 26 ocorrências de "melhor" para confirmar contexto técnico/educacional (não autorreferente) | 1h de revisão |
| Média | Adicionar `LinkedIn` e `Jusbrasil` ao `sameAs` do Person em 279 páginas quando os URLs forem fornecidos | script já existe em `/scripts/`; basta editar a constante e re-rodar |
| Baixa | Trocar `alumniOf: "[instituição]"` por instituição real quando confirmada | 1 sed em 279 arquivos |
| Baixa | Resolver TODO em `index.html`:342 (link "Ver perfil do responsável técnico" aponta para `#responsavel-tecnico` na própria home; trocar para `/sobre` quando ProfilePage existir) | bate com o item Crítico #1 |
| Baixa | Confirmar nome de registro na OAB/PR 122.982 e padronizar `Person.name` em 279 páginas se houver divergência | 1 consulta pública + 1 sed |

---

## Pendentes externos (aguardam dado)

- **URL LinkedIn do Giancarlo** → entra no `sameAs` (sprint próprio)
- **URL Jusbrasil do Giancarlo** → entra no `sameAs` (sprint próprio)
- **Nome registrado na OAB/PR 122.982** → padronização de `Person.name` se divergir de "Giancarlo Groth"
- **Instituição de formação** → preenche `alumniOf` (núcleo §6)
- **Decisão de posicionamento** (hub que encaminha vs atuação direta) → afeta o copy de `/sobre` quando criada
- **Confirmação editorial Lucas × post** → define `author` correto em 21 posts

---

## Resumo executivo

- **22 itens auditados nos pilares ✓** (entidade canônica, OAB, foto, fontes, freshness, sanfona, schema válido em 5/6 amostras)
- **2 bloqueadores de publicação** identificados:
  - `sobre.html` não materializa o `Person` canônico (knowledge graph com referência órfã)
  - `author` em 9 posts aponta para Person fictícia sem `@id`
- **8 correções sugeridas** para sprint próprio (2 críticas + 6 média/baixa)
- **6 pendentes externos** que aguardam dado do Lucas ou do registro público

**Conformidade com 205/2021:** sem promessa de resultado, sem honorários/gratuidade do serviço, sem captação ostensiva, sem superlativo autorreferente identificado. Disclaimer no footer das 279 páginas.

---

*SPIDERRANK · Consilium · auditoria E-E-A-T · 18 de junho de 2026.*
