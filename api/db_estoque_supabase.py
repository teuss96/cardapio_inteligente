import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def supabase_get(table, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, headers=supabase_headers(), params=params or {})
    resp.raise_for_status()
    return resp.json()

def supabase_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.post(url, headers=supabase_headers(), json=data)
    resp.raise_for_status()
    return resp.json()

def supabase_patch(table, match, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in match.items()}
    resp = requests.patch(url, headers=supabase_headers(), params=params, json=data)
    resp.raise_for_status()
    return resp.json()

def supabase_delete(table, match):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in match.items()}
    resp = requests.delete(url, headers=supabase_headers(), params=params)
    resp.raise_for_status()
    return True

def buscar_ingrediente_por_codigo(codigo):
    try:
        data = supabase_get("ingredientes", {"nome": f"eq.{codigo}"})
        return data[0] if data else None
    except:
        return None

def buscar_estoque_por_ingrediente(ingrediente_id):
    try:
        data = supabase_get("estoque", {"ingrediente_id": f"eq.{ingrediente_id}", "ativo": "eq.true"})
        return data
    except:
        return []

# ============== NOVAS FUNÇÕES PARA RELAÇÃO PRATO (PRODUTO) -> INGREDIENTES ==============
def listar_pratos():
    try:
        return supabase_get("produtos", {"order": "nome.asc"})
    except Exception:
        return []

def listar_pratos_admin():
    try:
        return supabase_get("produtos", {"order": "nome.asc"})
    except Exception:
        return []

def criar_prato(nome, preco, descricao=None, categoria_id=None):
    payload = {
        "nome": nome,
        "preco": preco,
        "descricao": descricao,
        "categoria_id": categoria_id,
        "status": "disponivel",
        "promocao": False
    }
    return supabase_post("produtos", payload)

def desativar_prato(prato_id):
    return supabase_patch("produtos", {"id": prato_id}, {"status": "indisponivel"})

def listar_ingredientes_disponiveis():
    try:
        return supabase_get("ingredientes", {"ativo": "eq.true", "order": "nome.asc"})
    except Exception:
        return []

def listar_mapeamentos(produto_id):
    try:
        return supabase_get("produtos_ingredientes", {"produto_id": f"eq.{produto_id}", "order": "ingrediente_id.asc"})
    except Exception:
        return []

def adicionar_mapeamento(produto_id, ingrediente_id, quantidade, unidade, obrigatorio=True, observacao=None):
    payload = {
        "produto_id": produto_id,
        "ingrediente_id": ingrediente_id,
        "quantidade": quantidade,
        "unidade": unidade,
        "obrigatorio": obrigatorio,
        "observacao": observacao
    }
    return supabase_post("produtos_ingredientes", payload)

def remover_mapeamento(mapeamento_id):
    return supabase_delete("produtos_ingredientes", {"id": mapeamento_id})

def trocar_tela(frame_destino):
    for frame in [frame_inicio, frame_cadastrar, frame_buscar, frame_listar, frame_ingredientes, frame_estoque_add, frame_prato_map, frame_pratos]:
        frame.pack_forget()
    frame_destino.pack(fill="both", expand=True)

def voltar_inicio():
    limpar_campos()
    frame_detalhes.pack_forget()
    frame_adicionar.pack_forget()
    resultado.set("")
    trocar_tela(frame_inicio)

def verificar_codigo(event=None):
    codigo = entry_codigo.get().strip()
    if not codigo:
        return
    ingrediente = buscar_ingrediente_por_codigo(codigo)
    if ingrediente:
        frame_adicionar.pack(pady=10)
        lbl_nome_existente.configure(text=f"Ingrediente: {ingrediente['nome']}")
        entry_qtd_add.focus()
        entry_codigo.ingrediente_id = ingrediente['id']
    else:
        frame_detalhes.pack(pady=10)
        entry_nome.focus()

def adicionar_existente():
    codigo = entry_codigo.get().strip()
    try:
        peso_add = float(entry_qtd_add.get())
        if peso_add <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Informe um peso válido (número positivo).")
        return
    ingrediente_id = getattr(entry_codigo, 'ingrediente_id', None)
    if not ingrediente_id:
        messagebox.showerror("Erro", "Ingrediente não encontrado!")
        return
    try:
        validade = entry_validade_add.get().strip() or None
        localizacao = entry_local_add.get().strip() or None
        supabase_post("estoque", {
            "ingrediente_id": ingrediente_id,
            "peso_balanca": peso_add,
            "validade": validade,
            "localizacao": localizacao
        })
        messagebox.showinfo("Sucesso", f"Adicionado {peso_add} kg ao estoque!")
        limpar_campos()
        frame_adicionar.pack_forget()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def cadastrar_produto():
    codigo = entry_codigo.get().strip()
    nome = entry_nome.get().strip()
    unidade = entry_unidade.get().strip() or "kg"
    categoria = entry_categoria.get().strip() or None
    peso_txt = entry_qtd.get().strip()
    if not codigo or not nome:
        messagebox.showwarning("Aviso", "Preencha o código e o nome.")
        return
    try:
        peso = float(peso_txt) if peso_txt else 0
        if peso < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Peso deve ser um número válido.")
        return
    try:
        resp = supabase_post("ingredientes", {"nome": codigo, "unidade": unidade, "categoria": categoria})
        ingrediente_id = resp[0]['id']
        if peso > 0:
            validade = entry_validade.get().strip() or None
            supabase_post("estoque", {"ingrediente_id": ingrediente_id, "peso_balanca": peso, "validade": validade})
        messagebox.showinfo("Cadastrado", f"Ingrediente '{nome}' cadastrado com sucesso!")
        limpar_campos()
        frame_detalhes.pack_forget()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def limpar_campos():
    entry_codigo.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_unidade.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)
    entry_validade.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)
    entry_qtd_add.delete(0, tk.END)
    entry_validade_add.delete(0, tk.END)
    entry_local_add.delete(0, tk.END)
    lbl_nome_existente.configure(text="")
    if hasattr(entry_codigo, 'ingrediente_id'):
        del entry_codigo.ingrediente_id

def buscar_produto(event=None):
    codigo = entry_busca.get().strip()
    ingrediente = buscar_ingrediente_por_codigo(codigo)
    if ingrediente:
        estoques = buscar_estoque_por_ingrediente(ingrediente['id'])
        total = sum(e.get('peso_balanca', 0) for e in estoques)
        validades = [e.get('validade') for e in estoques if e.get('validade')]
        prox_val = min(validades) if validades else "N/A"
        resultado.set(f"Ingrediente: {ingrediente['nome']}\nUnidade: {ingrediente['unidade']}\nCategoria: {ingrediente.get('categoria') or 'N/A'}\nEstoque Total: {total} {ingrediente['unidade']}\nPróxima Validade: {prox_val}")
    else:
        resultado.set("Ingrediente não encontrado.")

def listar_produtos():
    for item in tree.get_children():
        tree.delete(item)
    try:
        ingredientes = supabase_get("ingredientes", {"ativo": "eq.true", "order": "nome.asc"})
        for ing in ingredientes:
            estoques = buscar_estoque_por_ingrediente(ing['id'])
            total = sum(e.get('peso_balanca', 0) for e in estoques)
            validades = [e.get('validade') for e in estoques if e.get('validade')]
            prox_val = min(validades) if validades else ""
            tree.insert("", "end", values=(ing['id'], ing['nome'], ing['unidade'], ing.get('categoria') or '', total, prox_val))
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def abrir_gerenciar_ingredientes():
    listar_ingredientes()
    trocar_tela(frame_ingredientes)

def listar_ingredientes():
    for item in tree_ing.get_children():
        tree_ing.delete(item)
    try:
        ingredientes = supabase_get("ingredientes", {"order": "nome.asc"})
        for ing in ingredientes:
            tree_ing.insert("", "end", values=(ing['id'], ing['nome'], ing['unidade'], ing.get('categoria') or '', ing.get('estoque_minimo', 0), 'Sim' if ing.get('ativo') else 'Não'))
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def criar_ingrediente():
    nome = entry_ing_nome.get().strip()
    unidade = entry_ing_unidade.get().strip() or "kg"
    categoria = entry_ing_categoria.get().strip() or None
    estoque_min = entry_ing_minimo.get().strip()
    if not nome:
        messagebox.showwarning("Aviso", "Nome é obrigatório.")
        return
    try:
        supabase_post("ingredientes", {"nome": nome, "unidade": unidade, "categoria": categoria, "estoque_minimo": float(estoque_min) if estoque_min else 0})
        messagebox.showinfo("Sucesso", f"Ingrediente '{nome}' criado!")
        entry_ing_nome.delete(0, tk.END)
        entry_ing_unidade.delete(0, tk.END)
        entry_ing_categoria.delete(0, tk.END)
        entry_ing_minimo.delete(0, tk.END)
        listar_ingredientes()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def excluir_ingrediente():
    sel = tree_ing.selection()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione um ingrediente.")
        return
    item = tree_ing.item(sel[0])
    ing_id = item['values'][0]
    if messagebox.askyesno("Confirmar", "Deseja desativar este ingrediente?"):
        try:
            supabase_patch("ingredientes", {"id": ing_id}, {"ativo": False})
            listar_ingredientes()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

def abrir_adicionar_estoque():
    carregar_combo_ingredientes()
    trocar_tela(frame_estoque_add)

def carregar_combo_ingredientes():
    try:
        ingredientes = supabase_get("ingredientes", {"ativo": "eq.true", "order": "nome.asc"})
        combo_ing['values'] = [f"{i['id']} - {i['nome']}" for i in ingredientes]
    except:
        combo_ing['values'] = []

def adicionar_estoque_manual():
    sel = combo_ing.get()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione um ingrediente.")
        return
    ing_id = int(sel.split(" - ")[0])
    try:
        peso = float(entry_est_peso.get())
        if peso <= 0:
            raise ValueError
    except:
        messagebox.showerror("Erro", "Peso inválido.")
        return
    validade = entry_est_validade.get().strip() or None
    localizacao = entry_est_local.get().strip() or None
    lote = entry_est_lote.get().strip() or None
    try:
        supabase_post("estoque", {"ingrediente_id": ing_id, "peso_balanca": peso, "validade": validade, "localizacao": localizacao, "lote": lote})
        messagebox.showinfo("Sucesso", "Estoque adicionado!")
        entry_est_peso.delete(0, tk.END)
        entry_est_validade.delete(0, tk.END)
        entry_est_local.delete(0, tk.END)
        entry_est_lote.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

root = tk.Tk()
root.title("Sistema de Estoque - Supabase")
root.geometry("800x600")

frame_inicio = tk.Frame(root)
frame_inicio.pack(fill="both", expand=True)
tk.Label(frame_inicio, text="📦 Sistema de Estoque", font=("Arial", 20, "bold")).pack(pady=30)
tk.Button(frame_inicio, text="1 - Cadastrar com Leitor", width=30, height=2, command=lambda: trocar_tela(frame_cadastrar)).pack(pady=8)
tk.Button(frame_inicio, text="2 - Buscar Ingrediente", width=30, height=2, command=lambda: trocar_tela(frame_buscar)).pack(pady=8)
tk.Button(frame_inicio, text="3 - Listar Estoque", width=30, height=2, command=lambda: [trocar_tela(frame_listar), listar_produtos()]).pack(pady=8)
tk.Button(frame_inicio, text="4 - Gerenciar Ingredientes", width=30, height=2, command=abrir_gerenciar_ingredientes).pack(pady=8)
tk.Button(frame_inicio, text="5 - Adicionar Estoque Manual", width=30, height=2, command=abrir_adicionar_estoque).pack(pady=8)
tk.Button(frame_inicio, text="6 - Ingredientes por Prato", width=30, height=2, command=lambda: [carregar_pratos_mapeamento(), trocar_tela(frame_prato_map)]).pack(pady=8)
tk.Button(frame_inicio, text="7 - Gerenciar Pratos", width=30, height=2, command=lambda: [atualizar_lista_pratos(), trocar_tela(frame_pratos)]).pack(pady=8)
lbl_status = tk.Label(frame_inicio, text=f"Supabase: {SUPABASE_URL[:40]}..." if SUPABASE_URL else "⚠️ Configure .env", font=("Arial", 9), fg="gray")
lbl_status.pack(pady=20)

frame_cadastrar = tk.Frame(root)
tk.Label(frame_cadastrar, text="Cadastrar com Leitor", font=("Arial", 18, "bold")).pack(pady=10)
tk.Label(frame_cadastrar, text="Passe o código de barras:").pack()
entry_codigo = tk.Entry(frame_cadastrar, width=30)
entry_codigo.pack(pady=5)
entry_codigo.bind("<Return>", verificar_codigo)

frame_adicionar = tk.Frame(frame_cadastrar)
lbl_nome_existente = tk.Label(frame_adicionar, text="", font=("Arial", 12))
lbl_nome_existente.grid(row=0, column=0, columnspan=2, pady=5)
tk.Label(frame_adicionar, text="Peso a adicionar (kg):").grid(row=1, column=0)
entry_qtd_add = tk.Entry(frame_adicionar, width=10)
entry_qtd_add.grid(row=1, column=1)
tk.Label(frame_adicionar, text="Validade (AAAA-MM-DD):").grid(row=2, column=0)
entry_validade_add = tk.Entry(frame_adicionar, width=15)
entry_validade_add.grid(row=2, column=1)
tk.Label(frame_adicionar, text="Localização:").grid(row=3, column=0)
entry_local_add = tk.Entry(frame_adicionar, width=15)
entry_local_add.grid(row=3, column=1)
tk.Button(frame_adicionar, text="Adicionar ao Estoque", command=adicionar_existente).grid(row=4, column=0, columnspan=2, pady=8)

frame_detalhes = tk.Frame(frame_cadastrar)
tk.Label(frame_detalhes, text="Nome:").grid(row=0, column=0)
entry_nome = tk.Entry(frame_detalhes)
entry_nome.grid(row=0, column=1)
tk.Label(frame_detalhes, text="Unidade (kg, g, L):").grid(row=1, column=0)
entry_unidade = tk.Entry(frame_detalhes)
entry_unidade.grid(row=1, column=1)
tk.Label(frame_detalhes, text="Categoria:").grid(row=2, column=0)
entry_categoria = tk.Entry(frame_detalhes)
entry_categoria.grid(row=2, column=1)
tk.Label(frame_detalhes, text="Validade (AAAA-MM-DD):").grid(row=3, column=0)
entry_validade = tk.Entry(frame_detalhes)
entry_validade.grid(row=3, column=1)
tk.Label(frame_detalhes, text="Peso inicial (kg):").grid(row=4, column=0)
entry_qtd = tk.Entry(frame_detalhes)
entry_qtd.grid(row=4, column=1)
tk.Button(frame_detalhes, text="Salvar Novo Ingrediente", command=cadastrar_produto).grid(row=5, column=0, columnspan=2, pady=10)
tk.Button(frame_cadastrar, text="Voltar", command=voltar_inicio).pack(pady=10)

frame_buscar = tk.Frame(root)
tk.Label(frame_buscar, text="Buscar Ingrediente", font=("Arial", 18, "bold")).pack(pady=10)
entry_busca = tk.Entry(frame_buscar, width=40)
entry_busca.pack(pady=5)
entry_busca.bind("<Return>", buscar_produto)
resultado = tk.StringVar()
tk.Label(frame_buscar, textvariable=resultado, font=("Arial", 12), justify="left").pack(pady=10)
tk.Button(frame_buscar, text="Voltar", command=voltar_inicio).pack()

frame_listar = tk.Frame(root)
tk.Label(frame_listar, text="Estoque de Ingredientes", font=("Arial", 18, "bold")).pack(pady=10)
cols = ("ID", "Nome", "Unidade", "Categoria", "Estoque Total", "Próx. Validade")
tree = ttk.Treeview(frame_listar, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(expand=True, fill="both", padx=10, pady=10)
tk.Button(frame_listar, text="Atualizar", command=listar_produtos).pack(pady=5)
tk.Button(frame_listar, text="Voltar", command=voltar_inicio).pack(pady=5)

frame_ingredientes = tk.Frame(root)
tk.Label(frame_ingredientes, text="Gerenciar Ingredientes", font=("Arial", 18, "bold")).pack(pady=10)
frame_ing_form = tk.Frame(frame_ingredientes)
frame_ing_form.pack(pady=10)
tk.Label(frame_ing_form, text="Nome:").grid(row=0, column=0)
entry_ing_nome = tk.Entry(frame_ing_form, width=20)
entry_ing_nome.grid(row=0, column=1)
tk.Label(frame_ing_form, text="Unidade:").grid(row=0, column=2)
entry_ing_unidade = tk.Entry(frame_ing_form, width=8)
entry_ing_unidade.grid(row=0, column=3)
tk.Label(frame_ing_form, text="Categoria:").grid(row=1, column=0)
entry_ing_categoria = tk.Entry(frame_ing_form, width=20)
entry_ing_categoria.grid(row=1, column=1)
tk.Label(frame_ing_form, text="Est. Mínimo:").grid(row=1, column=2)
entry_ing_minimo = tk.Entry(frame_ing_form, width=8)
entry_ing_minimo.grid(row=1, column=3)
tk.Button(frame_ing_form, text="Criar", command=criar_ingrediente).grid(row=0, column=4, rowspan=2, padx=10)
cols_ing = ("ID", "Nome", "Unidade", "Categoria", "Est. Mínimo", "Ativo")
tree_ing = ttk.Treeview(frame_ingredientes, columns=cols_ing, show="headings", height=10)
for col in cols_ing:
    tree_ing.heading(col, text=col)
    tree_ing.column(col, width=90)
tree_ing.pack(expand=True, fill="both", padx=10, pady=10)
frame_ing_btns = tk.Frame(frame_ingredientes)
frame_ing_btns.pack(pady=5)
tk.Button(frame_ing_btns, text="Atualizar Lista", command=listar_ingredientes).pack(side="left", padx=5)
tk.Button(frame_ing_btns, text="Desativar Selecionado", command=excluir_ingrediente).pack(side="left", padx=5)
tk.Button(frame_ing_btns, text="Voltar", command=voltar_inicio).pack(side="left", padx=5)

frame_estoque_add = tk.Frame(root)
tk.Label(frame_estoque_add, text="Adicionar Estoque Manual", font=("Arial", 18, "bold")).pack(pady=10)
frame_est_form = tk.Frame(frame_estoque_add)
frame_est_form.pack(pady=10)
tk.Label(frame_est_form, text="Ingrediente:").grid(row=0, column=0)
combo_ing = ttk.Combobox(frame_est_form, width=30, state="readonly")
combo_ing.grid(row=0, column=1)
tk.Label(frame_est_form, text="Peso (kg):").grid(row=1, column=0)
entry_est_peso = tk.Entry(frame_est_form, width=15)
entry_est_peso.grid(row=1, column=1, sticky="w")
tk.Label(frame_est_form, text="Validade (AAAA-MM-DD):").grid(row=2, column=0)
entry_est_validade = tk.Entry(frame_est_form, width=15)
entry_est_validade.grid(row=2, column=1, sticky="w")
tk.Label(frame_est_form, text="Localização:").grid(row=3, column=0)
entry_est_local = tk.Entry(frame_est_form, width=20)
entry_est_local.grid(row=3, column=1, sticky="w")
tk.Label(frame_est_form, text="Lote:").grid(row=4, column=0)
entry_est_lote = tk.Entry(frame_est_form, width=15)
entry_est_lote.grid(row=4, column=1, sticky="w")
tk.Button(frame_est_form, text="Adicionar", command=adicionar_estoque_manual).grid(row=5, column=0, columnspan=2, pady=10)
tk.Button(frame_estoque_add, text="Voltar", command=voltar_inicio).pack(pady=10)

""" ================== FRAME MAPEAMENTO PRODUTO -> INGREDIENTES ================== """
frame_prato_map = tk.Frame(root)
tk.Label(frame_prato_map, text="Mapeamento de Ingredientes por Prato", font=("Arial", 18, "bold")).pack(pady=10)
frame_map_top = tk.Frame(frame_prato_map)
frame_map_top.pack(fill="x", padx=10)

tk.Label(frame_map_top, text="Pratos:").grid(row=0, column=0, sticky="w")
list_pratos = tk.Listbox(frame_map_top, height=10, width=30)
list_pratos.grid(row=1, column=0, rowspan=6, padx=5, pady=5, sticky="nsw")
scroll_pratos = tk.Scrollbar(frame_map_top, orient="vertical", command=list_pratos.yview)
scroll_pratos.grid(row=1, column=1, rowspan=6, sticky="ns")
list_pratos.configure(yscrollcommand=scroll_pratos.set)

tk.Label(frame_map_top, text="Mapeamentos do Prato:").grid(row=0, column=2, sticky="w")
cols_map = ("ID", "Ingrediente", "Qtd", "Unid", "Obr", "Obs")
tree_map = ttk.Treeview(frame_map_top, columns=cols_map, show="headings", height=10)
for col in cols_map:
    tree_map.heading(col, text=col)
    tree_map.column(col, width=90)
tree_map.grid(row=1, column=2, columnspan=5, padx=5, pady=5, sticky="nsew")
scroll_map = tk.Scrollbar(frame_map_top, orient="vertical", command=tree_map.yview)
scroll_map.grid(row=1, column=7, sticky="ns")
tree_map.configure(yscrollcommand=scroll_map.set)

frame_map_top.grid_columnconfigure(2, weight=1)
frame_map_top.grid_rowconfigure(1, weight=1)

frame_map_form = tk.Frame(frame_prato_map)
frame_map_form.pack(fill="x", padx=10, pady=10)
tk.Label(frame_map_form, text="Ingrediente:").grid(row=0, column=0)
combo_map_ing = ttk.Combobox(frame_map_form, width=30, state="readonly")
combo_map_ing.grid(row=0, column=1)
tk.Label(frame_map_form, text="Quantidade:").grid(row=0, column=2)
entry_map_qtd = tk.Entry(frame_map_form, width=10)
entry_map_qtd.grid(row=0, column=3)
tk.Label(frame_map_form, text="Unidade:").grid(row=0, column=4)
entry_map_unid = tk.Entry(frame_map_form, width=8)
entry_map_unid.grid(row=0, column=5)
var_obrigatorio = tk.BooleanVar(value=True)
chk_obrig = tk.Checkbutton(frame_map_form, text="Obrigatório", variable=var_obrigatorio)
chk_obrig.grid(row=0, column=6, padx=5)
tk.Label(frame_map_form, text="Observação:").grid(row=0, column=7)
entry_map_obs = tk.Entry(frame_map_form, width=20)
entry_map_obs.grid(row=0, column=8)
tk.Button(frame_map_form, text="Adicionar Ingrediente", command=lambda: acao_adicionar_mapeamento()).grid(row=0, column=9, padx=10)
tk.Button(frame_map_form, text="Remover Selecionado", command=lambda: acao_remover_mapeamento()).grid(row=0, column=10, padx=10)
tk.Button(frame_map_form, text="Voltar", command=voltar_inicio).grid(row=0, column=11, padx=10)

def carregar_pratos_mapeamento():
    list_pratos.delete(0, tk.END)
    pratos = listar_pratos()
    for p in pratos:
        list_pratos.insert(tk.END, f"{p['id']} - {p['nome']}")
    carregar_combo_ingredientes_map()

def carregar_combo_ingredientes_map():
    ingredientes = listar_ingredientes_disponiveis()
    combo_map_ing['values'] = [f"{i['id']} - {i['nome']}" for i in ingredientes]

def atualizar_mapeamentos_ui():
    sel = list_pratos.curselection()
    for item in tree_map.get_children():
        tree_map.delete(item)
    if not sel:
        return
    produto_id = int(list_pratos.get(sel[0]).split(" - ")[0])
    mapas = listar_mapeamentos(produto_id)
    # Para mostrar nome do ingrediente precisamos fazer um lookup rápido
    ingredientes_cache = {int(v.split(" - ")[0]): v.split(" - ")[1] for v in combo_map_ing['values']}
    for m in mapas:
        ing_nome = ingredientes_cache.get(m['ingrediente_id'], m['ingrediente_id'])
        tree_map.insert("", "end", values=(m['id'], ing_nome, m['quantidade'], m['unidade'], 'Sim' if m['obrigatorio'] else 'Não', m.get('observacao','')))

def acao_adicionar_mapeamento():
    sel_prato = list_pratos.curselection()
    if not sel_prato:
        messagebox.showwarning("Aviso", "Selecione um prato.")
        return
    prato_id = int(list_pratos.get(sel_prato[0]).split(" - ")[0])
    sel_ing = combo_map_ing.get()
    if not sel_ing:
        messagebox.showwarning("Aviso", "Selecione um ingrediente.")
        return
    ing_id = int(sel_ing.split(" - ")[0])
    try:
        qtd = float(entry_map_qtd.get())
        if qtd <= 0:
            raise ValueError
    except Exception:
        messagebox.showerror("Erro", "Quantidade inválida.")
        return
    unidade = entry_map_unid.get().strip() or 'g'
    obs = entry_map_obs.get().strip() or None
    try:
        adicionar_mapeamento(prato_id, ing_id, qtd, unidade, var_obrigatorio.get(), obs)
        entry_map_qtd.delete(0, tk.END)
        entry_map_unid.delete(0, tk.END)
        entry_map_obs.delete(0, tk.END)
        atualizar_mapeamentos_ui()
        messagebox.showinfo("Sucesso", "Ingrediente vinculado ao prato!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def acao_remover_mapeamento():
    sel_item = tree_map.selection()
    if not sel_item:
        messagebox.showwarning("Aviso", "Selecione um mapeamento na lista.")
        return
    item = tree_map.item(sel_item[0])
    map_id = item['values'][0]
    if messagebox.askyesno("Confirmar", "Remover este ingrediente do prato?"):
        try:
            remover_mapeamento(map_id)
            atualizar_mapeamentos_ui()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

""" ================== FRAME GERENCIAR PRATOS ================== """
frame_pratos = tk.Frame(root)
tk.Label(frame_pratos, text="Gerenciar Pratos", font=("Arial", 18, "bold")).pack(pady=10)
frame_prato_form = tk.Frame(frame_pratos)
frame_prato_form.pack(pady=10, fill="x")
tk.Label(frame_prato_form, text="Nome:").grid(row=0, column=0)
entry_prato_nome = tk.Entry(frame_prato_form, width=20)
entry_prato_nome.grid(row=0, column=1)
tk.Label(frame_prato_form, text="Preço:").grid(row=0, column=2)
entry_prato_preco = tk.Entry(frame_prato_form, width=10)
entry_prato_preco.grid(row=0, column=3)
tk.Label(frame_prato_form, text="Descrição:").grid(row=0, column=4)
entry_prato_desc = tk.Entry(frame_prato_form, width=25)
entry_prato_desc.grid(row=0, column=5)
tk.Label(frame_prato_form, text="Categoria ID:").grid(row=0, column=6)
entry_prato_cat = tk.Entry(frame_prato_form, width=8)
entry_prato_cat.grid(row=0, column=7)
tk.Button(frame_prato_form, text="Criar Prato", command=lambda: acao_criar_prato()).grid(row=0, column=8, padx=10)
tk.Button(frame_prato_form, text="Voltar", command=voltar_inicio).grid(row=0, column=9, padx=5)

cols_pratos = ("ID", "Nome", "Preço", "Status", "Promo", "Categoria")
tree_pratos = ttk.Treeview(frame_pratos, columns=cols_pratos, show="headings", height=12)
for col in cols_pratos:
    tree_pratos.heading(col, text=col)
    tree_pratos.column(col, width=90)
tree_pratos.pack(expand=True, fill="both", padx=10, pady=10)

frame_prato_btns = tk.Frame(frame_pratos)
frame_prato_btns.pack(pady=5)
tk.Button(frame_prato_btns, text="Atualizar Lista", command=lambda: atualizar_lista_pratos()).pack(side="left", padx=5)
tk.Button(frame_prato_btns, text="Desativar Selecionado", command=lambda: acao_desativar_prato()).pack(side="left", padx=5)
tk.Button(frame_prato_btns, text="Abrir Mapeamento", command=lambda: abrir_mapeamento_do_prato()).pack(side="left", padx=5)

def atualizar_lista_pratos():
    for item in tree_pratos.get_children():
        tree_pratos.delete(item)
    pratos = listar_pratos_admin()
    for p in pratos:
        tree_pratos.insert("", "end", values=(p['id'], p['nome'], p.get('preco',0), p.get('status',''), 'Sim' if p.get('promocao') else 'Não', p.get('categoria_id') or ''))

def acao_criar_prato():
    nome = entry_prato_nome.get().strip()
    preco_txt = entry_prato_preco.get().strip() or '0'
    desc = entry_prato_desc.get().strip() or None
    cat_txt = entry_prato_cat.get().strip() or None
    if not nome:
        messagebox.showwarning("Aviso", "Nome do prato é obrigatório.")
        return
    try:
        preco = float(preco_txt)
        if preco < 0:
            raise ValueError
    except Exception:
        messagebox.showerror("Erro", "Preço inválido.")
        return
    try:
        cat_id = int(cat_txt) if cat_txt else None
    except:
        cat_id = None
    try:
        criar_prato(nome, preco, desc, cat_id)
        entry_prato_nome.delete(0, tk.END)
        entry_prato_preco.delete(0, tk.END)
        entry_prato_desc.delete(0, tk.END)
        entry_prato_cat.delete(0, tk.END)
        atualizar_lista_pratos()
        messagebox.showinfo("Sucesso", "Prato criado!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def acao_desativar_prato():
    sel = tree_pratos.selection()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione um prato.")
        return
    item = tree_pratos.item(sel[0])
    prato_id = item['values'][0]
    if messagebox.askyesno("Confirmar", "Desativar este prato?"):
        try:
            desativar_prato(prato_id)
            atualizar_lista_pratos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

def abrir_mapeamento_do_prato():
    sel = tree_pratos.selection()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione um prato.")
        return
    item = tree_pratos.item(sel[0])
    prato_id = item['values'][0]
    for i in range(list_pratos.size()):
        if list_pratos.get(i).startswith(f"{prato_id} "):
            list_pratos.selection_clear(0, tk.END)
            list_pratos.selection_set(i)
            list_pratos.activate(i)
            break
    atualizar_mapeamentos_ui()
    trocar_tela(frame_prato_map)

list_pratos.bind("<<ListboxSelect>>", lambda e: atualizar_mapeamentos_ui())

root.mainloop()
