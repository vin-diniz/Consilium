// scripts/build-city-clusters.mjs
//
// Em cada pagina local (/servicos/{svc}/{cidade}-{uf}.html), insere antes
// de </main>:
//   - cluster intra-cidade: links para os outros servicos que EXISTEM
//     na mesma cidade (omite o servico atual e os ainda nao publicados)
//   - link de retorno descritivo a hub do servico atual
//
// Reexecutavel: usa marcadores <!-- CLUSTER:START --> ... <!-- CLUSTER:END -->
// Se ja existe o bloco entre marcadores, substitui; senao insere antes de </main>.

import { readdirSync, readFileSync, writeFileSync } from 'node:fs';

const UF_NOMES = {
  pr: 'Paraná',
  rj: 'Rio de Janeiro',
  mg: 'Minas Gerais',
  sc: 'Santa Catarina',
};

const SERVICOS = {
  'cobranca-empresarial': {
    label: 'Cobrança empresarial',
    hubLabel: 'cobrança empresarial',
  },
  'revisao-de-contratos-empresariais': {
    label: 'Revisão de contratos empresariais',
    hubLabel: 'revisão de contratos empresariais',
  },
  'acordo-de-socios-e-estruturacao-societaria': {
    label: 'Acordo de sócios e estruturação societária',
    hubLabel: 'acordo de sócios e estruturação societária',
  },
  'planejamento-sucessorio-empresarial': {
    label: 'Planejamento sucessório empresarial',
    hubLabel: 'planejamento sucessório empresarial',
  },
};

const NOMES_ESPECIAIS = {
  'sao-jose-dos-pinhais': 'São José dos Pinhais',
  'sao-jose': 'São José',
  'sao-bento-do-sul': 'São Bento do Sul',
  'sao-francisco-do-sul': 'São Francisco do Sul',
  'sao-joao-batista': 'São João Batista',
  'sao-joao-de-meriti': 'São João de Meriti',
  'sao-goncalo': 'São Gonçalo',
  'sao-miguel-do-oeste': 'São Miguel do Oeste',
  'balneario-camboriu': 'Balneário Camboriú',
  'braco-do-norte': 'Braço do Norte',
  'porto-uniao': 'Porto União',
  cacador: 'Caçador',
  chapeco: 'Chapecó',
  criciuma: 'Criciúma',
  florianopolis: 'Florianópolis',
  palhoca: 'Palhoça',
  tubarao: 'Tubarão',
  concordia: 'Concórdia',
  icara: 'Içara',
  forquilhinha: 'Forquilhinha',
  ararangua: 'Araranguá',
  biguacu: 'Biguaçu',
  'jaragua-do-sul': 'Jaraguá do Sul',
  mage: 'Magé',
  macae: 'Macaé',
  niteroi: 'Niterói',
  petropolis: 'Petrópolis',
  itaborai: 'Itaboraí',
  'campos-dos-goytacazes': 'Campos dos Goytacazes',
  'nova-iguacu': 'Nova Iguaçu',
  'foz-do-iguacu': 'Foz do Iguaçu',
  maringa: 'Maringá',
  'francisco-beltrao': 'Francisco Beltrão',
  'telemaco-borba': 'Telêmaco Borba',
  'campo-mourao': 'Campo Mourão',
  paranagua: 'Paranaguá',
};

function titleize(slug) {
  if (NOMES_ESPECIAIS[slug]) return NOMES_ESPECIAIS[slug];
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

// 1. Construir mapa cidade-uf -> servicos disponiveis
const matrix = {}; // key=`{cidade}-{uf}`, value = Set of svc slugs
for (const svc of Object.keys(SERVICOS)) {
  const dir = `./servicos/${svc}`;
  let files;
  try {
    files = readdirSync(dir, { withFileTypes: true });
  } catch (_) {
    continue;
  }
  for (const f of files) {
    if (!f.isFile() || !f.name.endsWith('.html')) continue;
    const slug = f.name.replace(/\.html$/, '');
    if (!/-[a-z]{2}$/.test(slug)) continue;
    (matrix[slug] ??= new Set()).add(svc);
  }
}

const startMarker = '<!-- CLUSTER:START -->';
const endMarker = '<!-- CLUSTER:END -->';
let totalEdited = 0;

for (const cidadeSlug of Object.keys(matrix)) {
  const uf = cidadeSlug.slice(-2);
  const cidadeNomeSlug = cidadeSlug.slice(0, -3);
  const cidadeNome = titleize(cidadeNomeSlug);
  const ufLabel = uf.toUpperCase();
  const ufNome = UF_NOMES[uf] || ufLabel;

  for (const svc of matrix[cidadeSlug]) {
    const path = `./servicos/${svc}/${cidadeSlug}.html`;
    const outros = [...matrix[cidadeSlug]].filter(s => s !== svc);
    if (outros.length === 0) continue; // sem outros servicos da mesma cidade

    const hubLabel = SERVICOS[svc].hubLabel;

    let block = `\n        <section class="outros-servicos-cidade reveal" aria-label="Outros serviços nesta cidade" style="padding: 32px 0;">\n`;
    block += `          <div class="container" style="max-width: 820px;">\n`;
    block += `            <h2 style="font-size: clamp(20px, 2.4vw, 26px); margin-bottom: 16px;">Outros serviços empresariais em ${cidadeNome} - ${ufLabel}</h2>\n`;
    block += `            <ul style="list-style: none; padding: 0; margin: 0;">\n`;
    for (const outroSvc of outros) {
      const label = SERVICOS[outroSvc].label;
      block += `              <li style="padding: 6px 0;"><a href="/servicos/${outroSvc}/${cidadeSlug}">${label} em ${cidadeNome}</a></li>\n`;
    }
    block += `            </ul>\n`;
    block += `            <p class="voltar-hub" style="margin-top: 24px;"><a href="/servicos/${svc}">Ver o panorama completo de ${hubLabel}</a></p>\n`;
    block += `          </div>\n`;
    block += `        </section>\n        `;

    let html;
    try {
      html = readFileSync(path, 'utf8');
    } catch (_) {
      continue;
    }

    if (html.includes(startMarker)) {
      // Substituir conteudo entre marcadores
      const re = new RegExp(
        `${startMarker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?${endMarker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`,
      );
      html = html.replace(re, `${startMarker}${block}${endMarker}`);
    } else {
      // Inserir antes do </main>
      const idx = html.lastIndexOf('</main>');
      if (idx < 0) {
        console.warn('sem </main> em', path);
        continue;
      }
      const insert = `${startMarker}${block}${endMarker}\n  `;
      html = html.substring(0, idx) + insert + html.substring(idx);
    }

    writeFileSync(path, html);
    totalEdited++;
  }
}

console.log(`Cluster intra-cidade aplicado em ${totalEdited} paginas locais`);
