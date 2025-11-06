const CATEGORIAS = {
  'Entrada': 'Entrada',
  'Pratos Principais': 'Pratos Principais',
  'Sobremesas': 'Sobremesas',
};

const ORDEM_CATEGORIAS = ['Entrada', 'Pratos Principais', 'Sobremesas'];

function criarCardPrato(prato) {
  const disponivel = prato.disponivel !== false;
  const precoFormatado = formatarPreco(prato.preco || prato.valor);
  const imagem = prato.imagem || prato.imagem_url || prato.foto || '';
  const descricao = prato.descricao || prato.desc || '';
  
  const classes = ['card', 'prato'];
  if (!disponivel) classes.push('indisponivel');
  
  return `
    <article class="${classes.join(' ')}" 
             data-id="${prato.id || ''}"
             data-nome="${prato.nome || prato.titulo || ''}"
             data-preco="${precoFormatado}"
             data-img="${imagem}"
             data-desc="${descricao}">
      <h3 class="card-titulo">${prato.nome || prato.titulo || 'Prato'}</h3>
      <p class="card-desc">${descricao || 'Descrição não disponível.'}</p>
      <span class="card-preco">${precoFormatado}</span>
      ${!disponivel ? '<span class="badge">Indisponível</span>' : ''}
    </article>
  `;
}

function criarSecao(categoria, pratos) {
  if (!pratos || pratos.length === 0) return '';
  
  const cards = pratos.map(prato => criarCardPrato(prato)).join('');
  
  return `
    <section class="secao">
      <h2 class="titulo-secao">${categoria}</h2>
      <div class="grid-cardapio">
        ${cards}
      </div>
    </section>
  `;
}

function renderizarCardapio(dados) {
  const container = document.getElementById('cardapio-container');
  if (!container) return;
  
  const pratosPorCategoria = {};
  
  dados.forEach(prato => {
    const categoria = prato.categoria || prato.categoria_nome || 'Outros';
    const categoriaNormalizada = CATEGORIAS[categoria] || categoria;
    
    if (!pratosPorCategoria[categoriaNormalizada]) {
      pratosPorCategoria[categoriaNormalizada] = [];
    }
    
    pratosPorCategoria[categoriaNormalizada].push(prato);
  });
  
  let html = '';
  
  ORDEM_CATEGORIAS.forEach(categoria => {
    if (pratosPorCategoria[categoria]) {
      html += criarSecao(categoria, pratosPorCategoria[categoria]);
    }
  });
  
  Object.keys(pratosPorCategoria).forEach(categoria => {
    if (!ORDEM_CATEGORIAS.includes(categoria)) {
      html += criarSecao(categoria, pratosPorCategoria[categoria]);
    }
  });
  
  container.innerHTML = html;
  inicializarModal();
}

function mostrarLoading(mostrar = true) {
  const loading = document.getElementById('loading');
  const container = document.getElementById('cardapio-container');
  const erro = document.getElementById('erro');
  
  if (loading) loading.style.display = mostrar ? 'block' : 'none';
  if (container) container.style.display = mostrar ? 'none' : 'block';
  if (erro) erro.style.display = 'none';
}

function mostrarErro(mensagem) {
  const erro = document.getElementById('erro');
  const erroMensagem = document.getElementById('erro-mensagem');
  const container = document.getElementById('cardapio-container');
  const loading = document.getElementById('loading');
  
  if (erro) erro.style.display = 'block';
  if (erroMensagem) erroMensagem.textContent = mensagem;
  if (container) container.style.display = 'none';
  if (loading) loading.style.display = 'none';
}

async function carregarCardapio() {
  mostrarLoading(true);
  
  try {
    const resultado = await buscarCardapio();
    
    if (resultado.erro) {
      mostrarErro(resultado.mensagem);
      return;
    }
    
    let pratos = resultado.dados;
    
    if (pratos && typeof pratos === 'object' && !Array.isArray(pratos)) {
      pratos = pratos.pratos || pratos.data || pratos.items || [];
    }
    
    if (!Array.isArray(pratos)) {
      mostrarErro('Formato de dados inválido recebido do servidor.');
      return;
    }
    
    if (pratos.length === 0) {
      mostrarErro('Nenhum prato encontrado no cardápio.');
      return;
    }
    
    mostrarLoading(false);
    renderizarCardapio(pratos);
    
  } catch (error) {
    console.error('Erro ao carregar cardápio:', error);
    mostrarErro('Erro inesperado ao carregar o cardápio. Tente novamente.');
  }
}

function inicializarModal() {
  const modal = document.getElementById('modal');
  if (!modal) return;

  const title = document.getElementById('modalTitle');
  const img = document.getElementById('modalImg');
  const price = document.getElementById('modalPrice');
  const desc = document.querySelector('.modal-desc');

  document.removeEventListener('click', handleCardClick);
  document.addEventListener('click', handleCardClick);

  function handleCardClick(e) {
    const close = e.target.closest('[data-close]');
    if (close) {
      fecharModal();
      return;
    }

    const prato = e.target.closest('.prato');
    if (prato && !prato.classList.contains('indisponivel')) {
      const nome = prato.getAttribute('data-nome');
      const preco = prato.getAttribute('data-preco');
      const imgSrc = prato.getAttribute('data-img');
      const descricao = prato.getAttribute('data-desc');
      
      if (title) title.textContent = nome || '';
      if (img && imgSrc) img.src = imgSrc;
      if (price) price.textContent = preco || '';
      if (desc) desc.textContent = descricao || 'Descrição não disponível.';
      
      modal.classList.add('show');
    }
  }

  function fecharModal() {
    modal.classList.remove('show');
  }

  modal.addEventListener('click', function (e) {
    if (e.target === modal) fecharModal();
  });
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('cardapio-container')) {
    carregarCardapio();
  }
  
  inicializarModal();
});

window.carregarCardapio = carregarCardapio;
