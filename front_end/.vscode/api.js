const API_CONFIG = {
  BASE_URL: 'http://localhost:3000/api',
  TIMEOUT: 10000,
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};
function formatarPreco(valor) {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return 'R$ 0,00';
  }
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(valor);
}
async function requisicao(endpoint, opcoes = {}) {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const headers = { ...API_CONFIG.DEFAULT_HEADERS };
  
  if (opcoes.headers) {
    Object.assign(headers, opcoes.headers);
  }
  
  const config = {
    method: opcoes.method || 'GET',
    headers: headers,
    ...opcoes
  };
  
  if (opcoes.body && !['GET', 'HEAD'].includes(config.method)) {
    config.body = JSON.stringify(opcoes.body);
  }
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    
    const resposta = await fetch(url, {
      ...config,
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    let dados = null;
    const contentType = resposta.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      dados = await resposta.json();
    } else {
      const texto = await resposta.text();
      if (texto) {
        try {
          dados = JSON.parse(texto);
        } catch (e) {
          dados = { mensagem: texto };
        }
      }
    }
    
    if (!resposta.ok) {
      return {
        erro: true,
        mensagem: dados?.mensagem || dados?.erro || `Erro ${resposta.status}: ${resposta.statusText}`,
        status: resposta.status,
        dados: null
      };
    }
    
    return {
      erro: false,
      mensagem: dados?.mensagem || 'Requisição realizada com sucesso',
      dados: dados?.dados || dados?.data || dados,
      status: resposta.status
    };
    
  } catch (erro) {
    console.error('Erro na requisição:', erro);
    
    if (erro.name === 'AbortError') {
      return {
        erro: true,
        mensagem: 'Tempo de requisição excedido. Verifique sua conexão.',
        dados: null
      };
    }
    
    if (erro.message === 'Failed to fetch' || erro.message.includes('NetworkError')) {
      return {
        erro: true,
        mensagem: 'Não foi possível conectar ao servidor. Verifique se a API está rodando.',
        dados: null
      };
    }
    
    return {
      erro: true,
      mensagem: erro.message || 'Erro inesperado ao fazer requisição',
      dados: null
    };
  }
}
async function buscarCardapio() {
  return await requisicao('/alimentos', { method: 'GET' });
}
function mostrarNotificacao(mensagem, tipo = 'info') {
  const notificacaoAntiga = document.querySelector('.notificacao-toast');
  if (notificacaoAntiga) {
    notificacaoAntiga.remove();
  }
  
  const toast = document.createElement('div');
  toast.className = `notificacao-toast notificacao-${tipo}`;
  toast.textContent = mensagem;
  
  document.body.appendChild(toast);
  
  setTimeout(() => toast.classList.add('show'), 10);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
window.API_CONFIG = API_CONFIG;
window.formatarPreco = formatarPreco;
window.buscarCardapio = buscarCardapio;
window.mostrarNotificacao = mostrarNotificacao;

console.log('✅ API Module carregado com sucesso!');
console.log(`📡 Base URL: ${API_CONFIG.BASE_URL}`);
