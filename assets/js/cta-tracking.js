/* CTA tracking - substitui o onclick="dataLayer..." inline em todas as
 * paginas localizadas e na home. Externalizado por requisito da CSP
 * (script-src 'self', sem 'unsafe-inline').
 *
 * Captura clicks em [data-cta-primario="whatsapp"] e empurra evento
 * para o dataLayer se houver GA/GTM no escopo global. */
(function () {
  function track(e) {
    if (window.dataLayer && typeof window.dataLayer.push === 'function') {
      window.dataLayer.push({
        event: 'whatsapp_cta',
        page_path: location.pathname,
      });
    }
  }
  function bind() {
    document.querySelectorAll('[data-cta-primario="whatsapp"]').forEach((el) => {
      el.addEventListener('click', track);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
