/* =========================================================
   Business 2 Brothers — interações
   Para trocar o número do WhatsApp, edite WHATSAPP_NUMBER.
   ========================================================= */
const WHATSAPP_NUMBER = '5521980602549';
const WHATSAPP_DEFAULT_MSG = 'Olá! Vim pelo site da Business 2 Brothers e gostaria de conversar sobre um projeto.';

// Links de WhatsApp (cada botão pode ter sua própria mensagem em data-msg)
document.querySelectorAll('[data-whatsapp]').forEach((link) => {
  const msg = link.dataset.msg || WHATSAPP_DEFAULT_MSG;
  link.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`;
  link.target = '_blank';
  link.rel = 'noopener';
});

// Ano no rodapé
const ano = document.getElementById('ano');
if (ano) ano.textContent = new Date().getFullYear();

// Menu do celular
const toggle = document.querySelector('.menu-toggle');
const menu = document.getElementById('menu');
if (toggle && menu) {
  const setOpen = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    menu.classList.toggle('is-open', open);
  };
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
}

// Sombra no cabeçalho ao rolar
const topbar = document.querySelector('.topbar');
const onScroll = () => topbar && topbar.classList.toggle('is-scrolled', window.scrollY > 8);
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Destaca no menu a seção visível
const navLinks = [...document.querySelectorAll('.nav a')];
const sections = navLinks.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window && sections.length) {
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      navLinks.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach((s) => spy.observe(s));
}

// Carrosséis com setas
document.querySelectorAll('[data-carousel]').forEach((carousel) => {
  const track = carousel.querySelector('.carousel__track');
  const prev = carousel.querySelector('.carousel__btn--prev');
  const next = carousel.querySelector('.carousel__btn--next');
  if (!track) return;

  const step = () => {
    const item = track.querySelector('li');
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return item ? item.getBoundingClientRect().width + gap : track.clientWidth;
  };
  const update = () => {
    const max = track.scrollWidth - track.clientWidth - 8;
    if (prev) prev.disabled = track.scrollLeft <= 8;
    if (next) next.disabled = track.scrollLeft >= max;
  };
  prev && prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
  next && next.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
});

// Animação suave ao aparecer na tela
if ('IntersectionObserver' in window) {
  const targets = document.querySelectorAll('.section__head, .sobre__grid > *, .card, .proj, .depo, .cta');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
    });
  }, { threshold: 0.12 });
  targets.forEach((el) => { el.classList.add('reveal'); io.observe(el); });
}
