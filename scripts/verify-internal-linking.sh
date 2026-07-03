#!/usr/bin/env bash
# scripts/verify-internal-linking.sh
# Verificacao pre-deploy do sprint de internal linking. Nao altera arquivos.
set -euo pipefail
FAIL=0
DOMAIN="consiliumadvogados.com.br"

echo "== 1. Referencias .html residuais (links internos, sitemap, canonical, og, JSON-LD) =="
if grep -rInE "${DOMAIN}[^\"' ]*\.html" --include="*.html" --include="*.xml" . ; then
  echo "  [FALHA] Ainda ha URLs .html do proprio dominio. Limpar."; FAIL=1
else
  echo "  [OK] Nenhuma URL .html do dominio."
fi

echo "== 2. Anchors / CTAs proibidos =="
if grep -rInE ">[[:space:]]*(saiba mais|clique aqui|veja mais|leia mais|conheça|entre em contato|nossa equipe)[[:space:]]*<" --include="*.html" . ; then
  echo "  [FALHA] Vocabulario proibido encontrado."; FAIL=1
else
  echo "  [OK] Nenhum anchor/CTA proibido."
fi

echo "== 3. CTAs de conversao apontam para /#contato =="
grep -rIn -E "(Receba diagnóstico|Veja a viabilidade jurídica|Solicite análise técnica)" --include="*.html" . \
  | grep -v "#contato" || echo "  [OK] CTAs aprovados vinculados a /#contato (ou ausentes)."

echo "== 4. Contagem de links de entrada nos alvos primarios =="
count_inbound () {
  local target="$1"; local minimo="$2"; local nome="$3"
  local n
  n=$(grep -rIl "href=\"${target}\"" --include="*.html" . | wc -l | tr -d ' ')
  if [ "$n" -lt "$minimo" ]; then
    echo "  [ATENCAO] ${nome}: ${n} paginas linkam (esperado >= ${minimo})."; FAIL=1
  else
    echo "  [OK] ${nome}: ${n} paginas linkam."
  fi
}
count_inbound "/servicos/planejamento-sucessorio-empresarial" 4 "Hub Sucessorio"
count_inbound "/blog/protocolo-familiar-o-que-e-validade-juridica" 3 "Protocolo familiar"
count_inbound "/blog/apuracao-de-haveres-como-funciona" 4 "Apuracao de haveres"
count_inbound "/blog/holding-familiar-quando-estruturar" 2 "Holding familiar"

echo
if [ "$FAIL" -eq 0 ]; then echo "RESULTADO: PASS"; else echo "RESULTADO: revisar itens acima"; exit 1; fi
