// main.js — gallery lightbox + FAQ single-open
document.addEventListener('DOMContentLoaded', () => {
  console.log('松坂搬家 site loaded');

  // --- Gallery lightbox ---
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox.querySelector('.lightbox-img');
  const closeBtn = lightbox.querySelector('.lightbox-close');
  function openLightbox(src) { lightboxImg.src = src; lightbox.hidden = false; document.body.style.overflow = 'hidden'; }
  function closeLightbox() { lightbox.hidden = true; lightboxImg.src = ''; document.body.style.overflow = ''; }
  document.querySelectorAll('.gallery-item').forEach(btn =>
    btn.addEventListener('click', () => openLightbox(btn.dataset.src)));
  closeBtn.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !lightbox.hidden) closeLightbox(); });

  // --- FAQ single-open accordion ---
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => item.addEventListener('toggle', () => {
    if (item.open) faqItems.forEach(o => { if (o !== item) o.open = false; });
  }));
});
