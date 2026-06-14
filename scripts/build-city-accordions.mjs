// scripts/build-city-accordions.mjs
//
// Gera a sanfona de cidades (zero-JS, crawlavel) em cada hub de servico.
// Reescreve apenas o conteudo entre os marcadores:
//   <!-- CIDADES:START:{slug} --> ... <!-- CIDADES:END:{slug} -->
//
// Idempotente: re-rodar a cada nova leva de paginas locais publicadas.
// Le diretamente os arquivos {cidade}-{uf}.html dentro de servicos/{slug}/

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const UF_NOMES = {
  pr: 'Paraná',
  rj: 'Rio de Janeiro',
  mg: 'Minas Gerais',
  sc: 'Santa Catarina',
};

// Ordem de exibicao das UFs (de cima pra baixo na sanfona): RJ primeiro (open),
// depois MG, depois PR, depois SC. Mantem o mesmo padrao das hubs originais.
const UF_ORDEM = ['rj', 'mg', 'pr', 'sc'];

// Servico slug -> rotulo do link descritivo
const SERVICO_LABEL = {
  'acordo-de-socios-e-estruturacao-societaria': 'Acordo de Sócios',
  'cobranca-empresarial': 'Cobrança Empresarial',
  'planejamento-sucessorio-empresarial': 'Planejamento Sucessório',
  'revisao-de-contratos-empresariais': 'Revisão de Contratos',
};

// Nomes especiais de cidades (acento, ç, hifens internos preservados)
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
  'cacador': 'Caçador',
  'chapeco': 'Chapecó',
  'criciuma': 'Criciúma',
  'florianopolis': 'Florianópolis',
  'palhoca': 'Palhoça',
  'tubarao': 'Tubarão',
  'concordia': 'Concórdia',
  'xaxim': 'Xaxim',
  'icara': 'Içara',
  'forquilhinha': 'Forquilhinha',
  'ararangua': 'Araranguá',
  'biguacu': 'Biguaçu',
  'jaragua-do-sul': 'Jaraguá do Sul',
  'mage': 'Magé',
  'macae': 'Macaé',
  'niteroi': 'Niterói',
  'petropolis': 'Petrópolis',
  'itaborai': 'Itaboraí',
  'campos-dos-goytacazes': 'Campos dos Goytacazes',
  'nova-iguacu': 'Nova Iguaçu',
  'foz-do-iguacu': 'Foz do Iguaçu',
  'cascavel': 'Cascavel',
  'maringa': 'Maringá',
  'umuarama': 'Umuarama',
  'francisco-beltrao': 'Francisco Beltrão',
  'telemaco-borba': 'Telêmaco Borba',
  'campo-mourao': 'Campo Mourão',
  'apucarana': 'Apucarana',
  'londrina': 'Londrina',
  'paranagua': 'Paranaguá',
  'ponta-grossa': 'Ponta Grossa',
  'pato-branco': 'Pato Branco',
  'guarapuava': 'Guarapuava',
  'sao-bento': 'São Bento',
};

function titleize(slug) {
  if (NOMES_ESPECIAIS[slug]) return NOMES_ESPECIAIS[slug];
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const SERVICES = readdirSync('./servicos', { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name)
  .filter(d => SERVICO_LABEL[d]); // so os 4 servicos conhecidos

for (const svc of SERVICES) {
  const dir = `./servicos/${svc}`;
  const slugs = readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isFile() && e.name.endsWith('.html'))
    .map(e => e.name.replace(/\.html$/, ''))
    .filter(n => /-[a-z]{2}$/.test(n)); // termina em -uf

  const byUF = {};
  for (const slug of slugs) {
    const uf = slug.slice(-2);
    const cidade = titleize(slug.slice(0, -3));
    (byUF[uf] ??= []).push({ cidade, slug });
  }

  const label = SERVICO_LABEL[svc];
  let block = '          <div class="locations-accordion reveal">\n';
  let isFirst = true;
  for (const uf of UF_ORDEM) {
    if (!byUF[uf]) continue;
    const cidades = byUF[uf].sort((a, b) => a.cidade.localeCompare(b.cidade, 'pt-BR'));
    const openAttr = isFirst ? ' open' : '';
    isFirst = false;
    block += `            <details class="locations-accordion__item"${openAttr}>\n`;
    block += `              <summary class="locations-accordion__summary">\n`;
    block += `                <span class="locations-accordion__uf">${uf.toUpperCase()}</span>\n`;
    block += `                <span class="locations-accordion__state">${UF_NOMES[uf]}</span>\n`;
    block += `                <span class="locations-accordion__count">${cidades.length} cidade${cidades.length === 1 ? '' : 's'}</span>\n`;
    block += `                <svg class="locations-accordion__chevron" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">\n`;
    block += `                  <path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>\n`;
    block += `                </svg>\n`;
    block += `              </summary>\n`;
    block += `              <ul class="locations-accordion__list" role="list">\n`;
    for (const c of cidades) {
      block += `                <li><a href="/servicos/${svc}/${c.slug}">${label} em ${c.cidade} - ${uf.toUpperCase()}</a></li>\n`;
    }
    block += `              </ul>\n`;
    block += `            </details>\n`;
  }
  block += '          </div>';

  const hubPath = `./servicos/${svc}.html`;
  if (!existsSync(hubPath)) {
    console.warn('Hub nao encontrada:', hubPath);
    continue;
  }
  let html = readFileSync(hubPath, 'utf8');
  const startMarker = `<!-- CIDADES:START:${svc} -->`;
  const endMarker = `<!-- CIDADES:END:${svc} -->`;
  const re = new RegExp(
    `(${escapeRegex(startMarker)})[\\s\\S]*?(${escapeRegex(endMarker)})`,
  );
  if (!re.test(html)) {
    console.warn('Marcadores ausentes em:', hubPath);
    continue;
  }
  html = html.replace(re, `${startMarker}\n${block}\n        ${endMarker}`);
  writeFileSync(hubPath, html);
  const totalCidades = Object.values(byUF).reduce((s, arr) => s + arr.length, 0);
  console.log(`ok ${svc}: ${totalCidades} cidades, ${Object.keys(byUF).length} UFs`);
}
