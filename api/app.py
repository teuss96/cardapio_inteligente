"""
API Python - Cardápio Inteligente
Contrato: retorna array direto de alimentos com campos fixos:
    nome (str), preco (number), desc (str), status (bool), promocao (bool)

Integração com esquema existente (SQLite já possui):
    categorias(id, nome)
    produtos(id, nome, preco, categoria_id)

Para não alterar sua tabela 'produtos', esta API adiciona uma tabela auxiliar
    produtos_meta(produto_id, desc, status, promocao)
e realiza LEFT JOIN para fornecer o contrato esperado pelo front.

Endpoints principais:
    GET /api/alimentos                 -> lista todos (join produtos + meta + categoria)
    GET /api/alimentos/<id>            -> item por id
    POST /api/alimentos                -> cria produto + metadados
    PUT /api/alimentos/<id>            -> atualiza produto + metadados
    PATCH /api/alimentos/<id>/status   -> atualiza apenas status
    PATCH /api/alimentos/<id>/promocao -> atualiza apenas promocao

CORS liberado para qualquer origem (ajuste para produção).

Para rodar:
    pip install -r requirements.txt
    python app.py
"""
from __future__ import annotations
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import (create_engine, Column, Integer, String, Boolean, Numeric,
                        DateTime, text, ForeignKey)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from dotenv import load_dotenv
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None

# Carrega variáveis de ambiente de um arquivo .env (se existir)
load_dotenv()


DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
AUTO_CREATE_META = os.getenv("AUTO_CREATE_META", "1") == "1"  # allow disabling sidecar creation
DISABLE_INIT_DB = os.getenv("DISABLE_INIT_DB", "0") == "1"      # skip Base.metadata.create_all entirely
USE_SUPABASE_API = os.getenv("USE_SUPABASE_API", "0") == "1"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # use only server-side, never expose publicly

def build_database_url() -> str:
    direct = os.getenv("DATABASE_URL")
    if direct:
        return direct
    host = os.getenv("SUPABASE_HOST")
    if host:
        db = os.getenv("SUPABASE_DB", "postgres")
        user = os.getenv("SUPABASE_USER", "postgres")
        password = os.getenv("SUPABASE_PASSWORD", "")
        port = os.getenv("SUPABASE_PORT", "5432")
        sslmode = "require" if os.getenv("SUPABASE_SSL", "1") == "1" else "prefer"
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}?sslmode={sslmode}"
    return "sqlite:///cardapio.db"

DATABASE_URL = build_database_url()

engine = None
SessionLocal = None
Base = declarative_base()

supabase_client = None  # type: ignore[assignment]
if USE_SUPABASE_API and SUPABASE_URL and (SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY) and create_client:
    # Prefer service key for unrestricted RLS operations; fallback to anon key
    supabase_key_to_use = SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY
    supabase_client = create_client(SUPABASE_URL, supabase_key_to_use)
else:
    # Fallback to SQLAlchemy engine
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

class Categoria(Base):
    __tablename__ = 'categorias'
    __table_args__ = {'schema': DB_SCHEMA} if DB_SCHEMA else None
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(120), nullable=False)


class Produto(Base):
    __tablename__ = 'produtos'
    __table_args__ = {'schema': DB_SCHEMA} if DB_SCHEMA else None
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(120), nullable=False, index=True)
    preco = Column(Numeric(10, 2), nullable=False, default=0)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=True)
    atualizado_em = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)


class ProdutoMeta(Base):
    __tablename__ = 'produtos_meta'
    __table_args__ = {'schema': DB_SCHEMA} if DB_SCHEMA else None
    produto_id = Column(Integer, ForeignKey('produtos.id'), primary_key=True)
    descricao = Column(String(500), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    promocao = Column(Boolean, nullable=False, default=False)
    atualizado_em = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

# Inicializa DB se necessário
def init_db():
    if USE_SUPABASE_API:
        return  # Do not attempt DDL via API client
    if DISABLE_INIT_DB:
        return
    if engine is None:
        return
    if AUTO_CREATE_META:
        ProdutoMeta.__table__.create(bind=engine, checkfirst=True)
    else:
        Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.before_request
def criar_sessao():
    if USE_SUPABASE_API:
        return
    request.db = SessionLocal()

@app.teardown_request
def fechar_sessao(exc):
    if USE_SUPABASE_API:
        return
    db = getattr(request, 'db', None)
    if db:
        if exc:
            db.rollback()
        else:
            db.commit()
        db.close()

# Helpers -------------------------------------------------------------

def parse_json_alimento(data: Dict[str, Any]) -> Dict[str, Any]:
    erros = []
    nome = data.get("nome")
    if not nome or not isinstance(nome, str):
        erros.append("Campo 'nome' obrigatório e deve ser string")
    try:
        preco_raw = data.get("preco", 0)
        preco = Decimal(str(preco_raw))
        if preco < 0:
            erros.append("'preco' não pode ser negativo")
    except Exception:
        erros.append("Campo 'preco' inválido")
        preco = Decimal("0")
    desc = data.get("desc", "")
    status = bool(data.get("status", True))
    promocao = bool(data.get("promocao", False))
    return {
        "erros": erros,
        "dados": {
            "nome": nome,
            "preco": preco,
            "desc": desc,
            "status": status,
            "promocao": promocao
        }
    }

def json_error(mensagem: str, status_code: int = 400, detalhes: Any = None):
    payload = {"erro": True, "mensagem": mensagem}
    if detalhes is not None:
        payload["detalhes"] = detalhes
    return jsonify(payload), status_code

# Endpoints -----------------------------------------------------------

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "hora": datetime.utcnow().isoformat()})

def montar_item(prod, meta_map, cat_map):
    pid = prod.get("id")
    meta = meta_map.get(pid)
    desc_val = ""
    if meta:
        if meta.get("descricao") is not None:
            desc_val = meta.get("descricao") or ""
        elif meta.get("desc") is not None:
            desc_val = meta.get("desc") or ""
    return {
        "id": pid,
        "nome": prod.get("nome"),
        "preco": float(prod.get("preco")) if prod.get("preco") is not None else 0.0,
        "desc": desc_val,
        "status": (bool(meta.get("status")) if meta and meta.get("status") is not None else True),
        "promocao": (bool(meta.get("promocao")) if meta and meta.get("promocao") is not None else False),
        "categoria_nome": cat_map.get(prod.get("categoria_id"))
    }

@app.route('/api/alimentos', methods=['GET'])
def listar_alimentos():
    if USE_SUPABASE_API and supabase_client:
        prods = supabase_client.table('produtos').select('id,nome,preco,categoria_id').execute().data
        metas_raw = supabase_client.table('produtos_meta').select('produto_id,descricao,status,promocao').execute().data
        cats = supabase_client.table('categorias').select('id,nome').execute().data
        meta_map = {m['produto_id']: {**m, 'desc': m.get('descricao')} for m in metas_raw}
        cat_map = {c['id']: c['nome'] for c in cats}
        dados = [montar_item(p, meta_map, cat_map) for p in prods]
        # Order by nome localmente
        dados.sort(key=lambda x: (x['nome'] or '').lower())
        return jsonify(dados)
    # SQLAlchemy path
    db = request.db
    rows = (
        db.query(Produto, ProdutoMeta, Categoria)
        .outerjoin(ProdutoMeta, ProdutoMeta.produto_id == Produto.id)
        .outerjoin(Categoria, Categoria.id == Produto.categoria_id)
        .order_by(Produto.nome.asc())
        .all()
    )
    dados = []
    for p, m, c in rows:
        dados.append({
            "id": p.id,
            "nome": p.nome,
            "preco": float(p.preco),
            "desc": (m.descricao if m and m.descricao is not None else ""),
            "status": (bool(m.status) if m and m.status is not None else True),
            "promocao": (bool(m.promocao) if m and m.promocao is not None else False),
            "categoria_nome": c.nome if c else None,
        })
    return jsonify(dados)

@app.route('/api/alimentos/<int:alimento_id>', methods=['GET'])
def obter_alimento(alimento_id: int):
    if USE_SUPABASE_API and supabase_client:
        prod_resp = supabase_client.table('produtos').select('id,nome,preco,categoria_id').eq('id', alimento_id).limit(1).execute().data
        if not prod_resp:
            return json_error("Alimento não encontrado", 404)
        metas_raw = supabase_client.table('produtos_meta').select('produto_id,descricao,status,promocao').eq('produto_id', alimento_id).limit(1).execute().data
        cats = []
        categoria_id = prod_resp[0].get('categoria_id')
        if categoria_id is not None:
            cats = supabase_client.table('categorias').select('id,nome').eq('id', categoria_id).limit(1).execute().data
        meta_map = {m['produto_id']: {**m, 'desc': m.get('descricao')} for m in metas_raw}
        cat_map = {c['id']: c['nome'] for c in cats}
        return jsonify(montar_item(prod_resp[0], meta_map, cat_map))
    # SQLAlchemy path
    db = request.db
    row = (
        db.query(Produto, ProdutoMeta, Categoria)
        .outerjoin(ProdutoMeta, ProdutoMeta.produto_id == Produto.id)
        .outerjoin(Categoria, Categoria.id == Produto.categoria_id)
        .filter(Produto.id == alimento_id)
        .first()
    )
    if not row:
        return json_error("Alimento não encontrado", 404)
    p, m, c = row
    return jsonify({
        "id": p.id,
        "nome": p.nome,
        "preco": float(p.preco),
        "desc": (m.descricao if m and m.descricao is not None else ""),
        "status": (bool(m.status) if m and m.status is not None else True),
        "promocao": (bool(m.promocao) if m and m.promocao is not None else False),
        "categoria_nome": c.nome if c else None,
    })

@app.route('/api/alimentos', methods=['POST'])
def criar_alimento():
    payload = request.get_json(force=True, silent=True) or {}
    parsed = parse_json_alimento(payload)
    if parsed["erros"]:
        return json_error("Dados inválidos", 400, parsed["erros"])
    if USE_SUPABASE_API and supabase_client:
        prod_resp = supabase_client.table('produtos').insert({
            'nome': parsed['dados']['nome'],
            'preco': float(parsed['dados']['preco']),
            'categoria_id': None
        }).execute().data
        if not prod_resp:
            return json_error("Falha ao inserir produto", 500)
        new_id = prod_resp[0]['id']
        supabase_client.table('produtos_meta').insert({
            'produto_id': new_id,
            'descricao': parsed['dados'].get('desc'),
            'status': parsed['dados'].get('status', True),
            'promocao': parsed['dados'].get('promocao', False)
        }).execute()
        return obter_alimento(new_id)
    # SQLAlchemy path
    db = request.db
    prod = Produto(nome=parsed["dados"]["nome"], preco=parsed["dados"]["preco"])
    db.add(prod)
    db.flush()
    meta = ProdutoMeta(
        produto_id=prod.id,
        descricao=parsed["dados"].get("desc"),
        status=parsed["dados"].get("status", True),
        promocao=parsed["dados"].get("promocao", False)
    )
    db.add(meta)
    return obter_alimento(prod.id)

@app.route('/api/alimentos/<int:alimento_id>', methods=['PUT'])
def atualizar_alimento(alimento_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    parsed = parse_json_alimento(payload)
    if parsed["erros"]:
        return json_error("Dados inválidos", 400, parsed["erros"])
    if USE_SUPABASE_API and supabase_client:
        # Update produto
        upd_prod = supabase_client.table('produtos').update({
            'nome': parsed['dados']['nome'],
            'preco': float(parsed['dados']['preco'])
        }).eq('id', alimento_id).execute().data
        if not upd_prod:
            return json_error("Alimento não encontrado", 404)
        # Upsert meta
        existing_meta = supabase_client.table('produtos_meta').select('produto_id').eq('produto_id', alimento_id).execute().data
        meta_payload = {
            'produto_id': alimento_id,
            'descricao': parsed['dados'].get('desc'),
            'status': parsed['dados'].get('status', True),
            'promocao': parsed['dados'].get('promocao', False)
        }
        if existing_meta:
            supabase_client.table('produtos_meta').update(meta_payload).eq('produto_id', alimento_id).execute()
        else:
            supabase_client.table('produtos_meta').insert(meta_payload).execute()
        return obter_alimento(alimento_id)
    # SQLAlchemy path
    db = request.db
    prod: Produto | None = db.query(Produto).get(alimento_id)
    if not prod:
        return json_error("Alimento não encontrado", 404)
    prod.nome = parsed["dados"]["nome"]
    prod.preco = parsed["dados"]["preco"]
    meta: ProdutoMeta | None = db.query(ProdutoMeta).get(alimento_id)
    if not meta:
        meta = ProdutoMeta(produto_id=alimento_id)
        db.add(meta)
    meta.descricao = parsed["dados"].get("desc")
    meta.status = parsed["dados"].get("status", True)
    meta.promocao = parsed["dados"].get("promocao", False)
    return obter_alimento(alimento_id)

@app.route('/api/alimentos/<int:alimento_id>/status', methods=['PATCH'])
def alterar_status(alimento_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    if 'status' not in payload:
        return json_error("Campo 'status' é obrigatório", 400)
    if USE_SUPABASE_API and supabase_client:
        existing_meta = supabase_client.table('produtos_meta').select('produto_id').eq('produto_id', alimento_id).execute().data
        meta_payload = {
            'produto_id': alimento_id,
            'status': bool(payload['status'])
        }
        if existing_meta:
            supabase_client.table('produtos_meta').update(meta_payload).eq('produto_id', alimento_id).execute()
        else:
            supabase_client.table('produtos_meta').insert(meta_payload).execute()
        return obter_alimento(alimento_id)
    db = request.db
    prod: Produto | None = db.query(Produto).get(alimento_id)
    if not prod:
        return json_error("Alimento não encontrado", 404)
    meta: ProdutoMeta | None = db.query(ProdutoMeta).get(alimento_id)
    if not meta:
        meta = ProdutoMeta(produto_id=alimento_id)
        db.add(meta)
    meta.status = bool(payload['status'])
    return obter_alimento(alimento_id)

@app.route('/api/alimentos/<int:alimento_id>/promocao', methods=['PATCH'])
def alterar_promocao(alimento_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    if 'promocao' not in payload:
        return json_error("Campo 'promocao' é obrigatório", 400)
    if USE_SUPABASE_API and supabase_client:
        existing_meta = supabase_client.table('produtos_meta').select('produto_id').eq('produto_id', alimento_id).execute().data
        meta_payload = {
            'produto_id': alimento_id,
            'promocao': bool(payload['promocao'])
        }
        if existing_meta:
            supabase_client.table('produtos_meta').update(meta_payload).eq('produto_id', alimento_id).execute()
        else:
            supabase_client.table('produtos_meta').insert(meta_payload).execute()
        return obter_alimento(alimento_id)
    db = request.db
    prod: Produto | None = db.query(Produto).get(alimento_id)
    if not prod:
        return json_error("Alimento não encontrado", 404)
    meta: ProdutoMeta | None = db.query(ProdutoMeta).get(alimento_id)
    if not meta:
        meta = ProdutoMeta(produto_id=alimento_id)
        db.add(meta)
    meta.promocao = bool(payload['promocao'])
    return obter_alimento(alimento_id)

# Inicialização -------------------------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '3000')), debug=True)
