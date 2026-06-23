/* Contact form handler - posta em /api/contact (Pages Function).
 * Substitui o submit direto ao Web3Forms.
 * Externalizado em /assets/js/ para conformidade com CSP script-src 'self'. */
(function () {
  const form = document.getElementById('contactForm');
  if (!form) return;
  const formSuccess = document.getElementById('formSuccess');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const btn = form.querySelector('button[type="submit"]');
    const originalBtnHTML = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="spin">
        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" stroke-dasharray="20 18"/>
      </svg>
      Enviando...
    `;

    // Honeypot: se foi marcado (bot), abortar silenciosamente
    if (form.botcheck && form.botcheck.checked) {
      form.hidden = true;
      if (formSuccess) formSuccess.hidden = false;
      return;
    }

    const fd = new FormData(form);
    const payload = {
      name:    fd.get('name'),
      company: fd.get('company'),
      phone:   fd.get('phone'),
      issue:   fd.get('issue'),
      lgpd_consent: form.querySelector('[name="lgpd_consent"]')?.checked || false,
      botcheck: fd.get('botcheck') || '',
      'cf-turnstile-response': fd.get('cf-turnstile-response') || '',
      // page_url ja vai SEM query string (defesa extra, VULN-005)
      page_url: window.location.origin + window.location.pathname,
      submitted_at: new Date().toISOString(),
    };

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.success) {
        form.hidden = true;
        if (formSuccess) {
          formSuccess.hidden = false;
          formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        form.reset();
        if (window.turnstile) window.turnstile.reset();
      } else {
        throw new Error(data.message || 'Falha no envio');
      }
    } catch (err) {
      console.error('[Consilium] Erro no envio:', err);
      alert('Nao foi possivel enviar agora. Tente novamente em instantes ou escreva para acesso@consiliumadvogados.com.br.');
      btn.disabled = false;
      btn.innerHTML = originalBtnHTML;
      if (window.turnstile) window.turnstile.reset();
    }
  });

  function validateForm() {
    let valid = true;
    let firstInvalid = null;
    const required = form.querySelectorAll('[required]');

    required.forEach((field) => {
      const isInvalid = field.type === 'checkbox' ? !field.checked : !field.value.trim();
      field.classList.toggle('error', isInvalid);

      if (isInvalid) {
        valid = false;
        if (!firstInvalid) firstInvalid = field;
      } else {
        field.addEventListener(
          field.type === 'checkbox' ? 'change' : 'input',
          () => field.classList.remove('error'),
          { once: true }
        );
      }
    });

    const phone = form.querySelector('input[name="phone"]');
    if (phone && phone.value.trim() && phone.pattern) {
      const re = new RegExp(phone.pattern);
      if (!re.test(phone.value.trim())) {
        phone.classList.add('error');
        valid = false;
        if (!firstInvalid) firstInvalid = phone;
      }
    }

    if (firstInvalid) {
      firstInvalid.focus({ preventScroll: false });
      firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return valid;
  }
})();
