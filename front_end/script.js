// Modal de pratos
(function () {
  const modal = document.getElementById('modal');
  if (!modal) return;

  const title = document.getElementById('modalTitle');
  const img = document.getElementById('modalImg');
  const price = document.getElementById('modalPrice');

  document.addEventListener('click', function (e) {
    const close = e.target.closest('[data-close]');
    if (close) return fechar();

    const prato = e.target.closest('.prato');
    if (prato && !prato.classList.contains('indisponivel')) {
      const nome = prato.getAttribute('data-nome');
      const preco = prato.getAttribute('data-preco');
      const imgSrc = prato.getAttribute('data-img');
      if (title) title.textContent = nome || '';
      if (img && imgSrc) img.src = imgSrc;
      if (price) price.textContent = preco || '';
      modal.classList.add('show');
    }
  });

  function fechar() {
    modal.classList.remove('show');
  }

  modal.addEventListener('click', function (e) {
    if (e.target === modal) fechar();
  });
})();

