/* ═══════════════════════════════════════════════════════
   CONSILIUM | HUB DE INTELIGÊNCIA JURÍDICA — main.js
   Scroll animations · Counter · Nav · Form
═══════════════════════════════════════════════════════ */

'use strict';

/* ── NAVIGATION ─────────────────────────────────────── */
const header    = document.getElementById('header');
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');

// Sticky header on scroll
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// Mobile menu toggle
navToggle?.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  navToggle.classList.toggle('open', isOpen);
  navToggle.setAttribute('aria-expanded', String(isOpen));
  document.body.style.overflow = isOpen ? 'hidden' : '';
});

// Close mobile menu on link click
navLinks?.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle?.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  });
});

// Close on ESC
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && navLinks?.classList.contains('open')) {
    navLinks.classList.remove('open');
    navToggle?.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    navToggle?.focus();
  }
});


/* ── DROPDOWN "SERVIÇOS" ────────────────────────────
   Desktop: hover via CSS
   Mobile: click/tap toggla .open
   Acessibilidade: ESC fecha · outside click fecha · ARIA em sincronia */
const dropdownItems = document.querySelectorAll('.nav__item--dropdown');

dropdownItems.forEach(item => {
  const toggle = item.querySelector('.nav__link--toggle');
  const dropdown = item.querySelector('.nav__dropdown');
  if (!toggle || !dropdown) return;

  toggle.addEventListener('click', (e) => {
    // No desktop (hover) o clique do botão não faz nada (o hover já mostra).
    // No mobile (sem hover reliable), toggla .open.
    const isMobile = window.matchMedia('(max-width: 640px)').matches
                   || !window.matchMedia('(hover: hover)').matches;
    if (isMobile) {
      e.preventDefault();
      e.stopPropagation();
      const willOpen = !item.classList.contains('open');
      // Fecha outros dropdowns abertos
      dropdownItems.forEach(other => {
        if (other !== item) {
          other.classList.remove('open');
          other.querySelector('.nav__link--toggle')
            ?.setAttribute('aria-expanded', 'false');
        }
      });
      item.classList.toggle('open', willOpen);
      toggle.setAttribute('aria-expanded', String(willOpen));
    }
  });

  // Seta aria-expanded quando desktop hover abre (para screen readers)
  item.addEventListener('mouseenter', () => {
    if (window.matchMedia('(hover: hover)').matches) {
      toggle.setAttribute('aria-expanded', 'true');
    }
  });
  item.addEventListener('mouseleave', () => {
    if (window.matchMedia('(hover: hover)').matches) {
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
});

// Fechar dropdown ao clicar fora (mobile)
document.addEventListener('click', (e) => {
  dropdownItems.forEach(item => {
    if (item.classList.contains('open') && !item.contains(e.target)) {
      item.classList.remove('open');
      item.querySelector('.nav__link--toggle')
        ?.setAttribute('aria-expanded', 'false');
    }
  });
});

// ESC fecha qualquer dropdown aberto
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    dropdownItems.forEach(item => {
      if (item.classList.contains('open')) {
        item.classList.remove('open');
        const toggle = item.querySelector('.nav__link--toggle');
        toggle?.setAttribute('aria-expanded', 'false');
        toggle?.focus();
      }
    });
  }
});


/* ── HERO TICKER ────────────────────────────────────── */
const ticker = document.getElementById('heroTicker');
if (ticker) {
  // Duplicate children for seamless infinite scroll
  const items = [...ticker.children];
  items.forEach(item => {
    const clone = item.cloneNode(true);
    ticker.appendChild(clone);
  });
}


/* ── SCROLL REVEAL ──────────────────────────────────── */
// Fallback para navegadores sem IntersectionObserver
if (!('IntersectionObserver' in window)) {
  document.querySelectorAll('.reveal, .reveal-instant').forEach(el => el.classList.add('visible'));
} else {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -10% 0px' }
  );

  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  // Instant reveals — cinematic stagger para o hero (LCP não bloqueado)
  document.querySelectorAll('.reveal-instant').forEach((el, i) => {
    setTimeout(() => el.classList.add('visible'), 80 + i * 120);
  });

  // Fail-safe: depois de 2,5s, qualquer .reveal ainda invisível é revelada.
  // Evita "buracos" caso o observer falhe por layout complexo, print, deep-link ou JS parcial.
  window.addEventListener('load', () => {
    setTimeout(() => {
      document.querySelectorAll('.reveal:not(.visible), .reveal-instant:not(.visible)')
        .forEach(el => el.classList.add('visible'));
    }, 2500);
  });
}





/* ── ACTIVE NAV LINK ─────────────────────────────────── */
const sections  = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav__link:not(.nav__link--cta)');

const sectionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navAnchors.forEach(a => {
          const isActive = a.getAttribute('href') === `#${id}`;
          a.style.color = isActive ? 'var(--text-primary)' : '';
        });
      }
    });
  },
  { threshold: 0.35 }
);

sections.forEach(s => sectionObserver.observe(s));


/* ── PHONE MASK ──────────────────────────────────────── */
const phoneInput = document.getElementById('phone');

phoneInput?.addEventListener('input', function () {
  let v = this.value.replace(/\D/g, '').slice(0, 11);
  if (v.length > 10) {
    v = v.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
  } else if (v.length > 6) {
    v = v.replace(/^(\d{2})(\d{4})(\d*)$/, '($1) $2-$3');
  } else if (v.length > 2) {
    v = v.replace(/^(\d{2})(\d*)$/, '($1) $2');
  }
  this.value = v;
});


/* ── CONTACT FORM ────────────────────────────────────── */
const form        = document.getElementById('contactForm');
const formSuccess = document.getElementById('formSuccess');

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validateForm()) return;

  const btn = form.querySelector('button[type="submit"]');

  btn.disabled = true;
  btn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="spin">
      <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" stroke-dasharray="20 18"/>
    </svg>
    Enviando...
  `;

  // Collect lead data
  const data = {
    name:    form.name.value.trim(),
    company: form.company.value.trim(),
    phone:   form.phone.value.trim(),
    issue:   form.issue.value,
    source:  window.location.href,
    date:    new Date().toISOString(),
  };

  // In production, replace this with your actual endpoint / webhook
  await simulateSend(data);

  form.hidden = true;
  formSuccess.hidden = false;
  formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});

async function simulateSend(data) {
  // Replace with: await fetch('/api/leads', { method:'POST', body: JSON.stringify(data), headers:{'Content-Type':'application/json'} })
  console.info('[Consilium] Lead capturado:', data);
  return new Promise(resolve => setTimeout(resolve, 900));
}

function validateForm() {
  let valid = true;
  const required = form.querySelectorAll('[required]');

  required.forEach(field => {
    const isEmpty = !field.value.trim();
    field.classList.toggle('error', isEmpty);

    if (isEmpty) {
      valid = false;
      if (field === required[0]) field.focus();
    } else {
      field.addEventListener('input', () => field.classList.remove('error'), { once: true });
    }
  });

  return valid;
}


/* ── SMOOTH SCROLL for anchors ───────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});


/* ── CSS: spinner for button ─────────────────────────── */
const spinStyle = document.createElement('style');
spinStyle.textContent = `
  @keyframes spin { to { transform: rotate(360deg); } }
  .spin { animation: spin 0.8s linear infinite; }
`;
document.head.appendChild(spinStyle);
