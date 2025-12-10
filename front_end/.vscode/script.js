const CATEGORIAS = {
  'Bebidas': 'Bebidas',
  'Pratos': 'Pratos',
  'Sobremesas': 'Sobremesas',
};

const ORDEM_CATEGORIAS = ['Bebidas', 'Pratos', 'Sobremesas'];

function criarCardPrato(prato) {
  const disponivel = Boolean(prato.status ?? prato.disponivel);
  const preco = Number(prato.preco ?? 0);
  const precoFmt = formatarPreco(preco);
  const imagem = prato.imagem || prato.foto || '';
  const nomePrato = escapeHtml(prato.nome || 'Alimento');
  const descPrato = escapeHtml(prato.desc || '');
  const imgSrc = escapeHtml(imagem || 'https://via.placeholder.com/400x200/FBEDC8/75403C?text=Sem+Imagem');
  const emPromocao = prato.promocao === true;

  const classes = ['card', 'prato'];
  if (!disponivel) classes.push('indisponivel');
  if (emPromocao) classes.push('em-promocao');

  return `
    <article class="${classes.join(' ')}" 
             data-id="${prato.id || ''}"
             data-nome="${nomePrato}"
             data-preco="${precoFmt}"
             data-img="${imgSrc}"
             data-desc="${descPrato}"
             data-promocao="${emPromocao ? 'true' : 'false'}">
      <h3 class="card-titulo">${nomePrato}</h3>
      <p class="card-desc">${descPrato || 'Descrição não disponível.'}</p>
      <span class="card-preco">${precoFmt}</span>
      ${emPromocao ? '<span class="badge badge-promo" aria-label="Promoção do dia">Promoção</span>' : ''}
      ${!disponivel ? '<span class="badge">Indisponível</span>' : ''}
    </article>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
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
      console.error('Erro ao buscar cardápio:', resultado);
      return;
    }
    
    let pratos = resultado.dados;
    
    if (pratos && typeof pratos === 'object' && !Array.isArray(pratos)) {
      pratos = pratos.pratos || pratos.data || pratos.items || [];
    }
    
    if (!Array.isArray(pratos)) {
      mostrarErro('Formato de dados inválido recebido do servidor.');
      console.error('Dados recebidos:', pratos);
      return;
    }
    
    if (pratos.length === 0) {
      mostrarErro('Nenhum prato encontrado no cardápio.');
      return;
    }
    
    console.log(`✅ ${pratos.length} prato(s) carregado(s) com sucesso!`);
    
    mostrarLoading(false);
    renderizarCardapio(pratos);
    
  } catch (error) {
    console.error('Erro inesperado ao carregar cardápio:', error);
    mostrarErro('Erro inesperado ao carregar o cardápio. Verifique se a API está rodando.');
  }
}

function inicializarModal() {
  const modal = document.getElementById('modal');
  if (!modal) return;

  const title = document.getElementById('modalTitle');
  const img = document.getElementById('modalImg');
  const price = document.getElementById('modalPrice');
  const desc = document.getElementById('modalDesc');

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
      if (img && imgSrc) {
        img.src = imgSrc;
        img.alt = `Imagem de ${nome}`;
      }
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
  
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('show')) {
      fecharModal();
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('cardapio-container')) {
    carregarCardapio();
  }
  
  inicializarModal();
});

window.carregarCardapio = carregarCardapio;
