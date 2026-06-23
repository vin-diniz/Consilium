// /functions/api/contact.js
// Cloudflare Pages Function — recebe o lead, valida, confere Turnstile e
// repassa ao Web3Forms. Chave do Web3Forms e secret do Turnstile vivem em
// variaveis de ambiente do Pages (WEB3FORMS_ACCESS_KEY, TURNSTILE_SECRET_KEY).
// NUNCA no HTML.
//
// Campos reais do form (id="contactForm" em /index.html):
//   name (texto)              - obrigatorio
//   company (texto)           - obrigatorio
//   phone (texto, mascara)    - obrigatorio
//   issue (select 4 opcoes)   - obrigatorio
//   lgpd_consent (checkbox)   - obrigatorio
//   botcheck (honeypot)       - bot se marcado
//
// O form NAO pede email - o retorno e por telefone/WhatsApp.

function originAllowed(origin) {
  if (!origin) return false;
  let host;
  try { host = new URL(origin).hostname; } catch { return false; }
  if (host === "www.consiliumadvogados.com.br") return true;
  if (host === "consiliumadvogados.com.br") return true;
  if (host === "consilium-bem.pages.dev") return true;        // alias pages.dev
  if (host.endsWith(".consilium-bem.pages.dev")) return true; // previews
  return false;
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

const ISSUE_OPTIONS = new Set(["contrato", "ativos", "risco", "assessoria"]);
const ISSUE_LABELS = {
  contrato:   "Blindagem Contratual",
  ativos:     "Recuperacao Estrategica de Creditos",
  risco:      "Gestao de Passivos e Processos",
  assessoria: "Assessoria Juridica Recorrente (Boutique)",
};

export async function onRequestPost({ request, env }) {
  // 1) Origem (resolve VULN-002: so o proprio site pode postar)
  const origin = request.headers.get("Origin") || "";
  if (!originAllowed(origin)) {
    return json({ success: false, message: "Origem nao autorizada." }, 403);
  }

  // 2) Corpo (JSON enviado pelo front)
  let data;
  try { data = await request.json(); }
  catch { return json({ success: false, message: "Requisicao invalida." }, 400); }

  // 3) Honeypot - campo oculto preenchido = bot. Finge sucesso e descarta.
  if (data.botcheck) return json({ success: true, message: "Recebido." }, 200);

  // 4) Turnstile (anti-bot server-side)
  const token = data["cf-turnstile-response"];
  if (!token) return json({ success: false, message: "Verificacao anti-spam ausente." }, 400);

  const ip = request.headers.get("CF-Connecting-IP") || "";
  const verifyRes = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      secret: env.TURNSTILE_SECRET_KEY,
      response: token,
      remoteip: ip,
    }),
  });
  const verify = await verifyRes.json();
  if (!verify.success) {
    return json({ success: false, message: "Falha na verificacao anti-spam." }, 403);
  }

  // 5) Validacao de campos (nomes do form real)
  const nome = String(data.name || "").trim();
  const empresa = String(data.company || "").trim();
  const telefone = String(data.phone || "").trim();
  const issue = String(data.issue || "").trim();
  const consent = data.lgpd_consent === true
               || data.lgpd_consent === "on"
               || data.lgpd_consent === "true";

  const erros = [];
  if (nome.length < 2 || nome.length > 120) erros.push("nome");
  if (empresa.length < 2 || empresa.length > 150) erros.push("empresa");
  const digitos = telefone.replace(/\D/g, "");
  if (digitos.length < 10 || digitos.length > 13 || telefone.length > 25) erros.push("telefone");
  if (!ISSUE_OPTIONS.has(issue)) erros.push("frente");
  if (!consent) erros.push("consentimento");
  if (erros.length) {
    return json({ success: false, message: "Dados invalidos.", fields: erros }, 422);
  }

  // 6) page_url SEM query string (VULN-005)
  let pageUrl = "";
  try {
    const u = new URL(String(data.page_url || ""));
    pageUrl = `${u.origin}${u.pathname}`;
  } catch { pageUrl = ""; }

  // 7) Repasse ao Web3Forms (chave so no servidor)
  const w3Res = await fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify({
      access_key: env.WEB3FORMS_ACCESS_KEY,
      subject: "Novo Diagnostico - Consilium (consiliumadvogados.com.br)",
      from_name: "Consilium | Site",
      name: nome,
      company: empresa,
      phone: telefone,
      frente: ISSUE_LABELS[issue],
      page_url: pageUrl,
      submitted_at: new Date().toISOString(),
    }),
  });
  const resultado = await w3Res.json().catch(() => ({}));
  if (!resultado.success) {
    return json({ success: false, message: "Nao foi possivel enviar agora. Tente novamente em instantes." }, 502);
  }

  return json({ success: true, message: "Recebido. Retorno em ate 4 horas uteis." }, 200);
}
