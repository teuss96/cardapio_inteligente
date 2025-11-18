import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from datetime import datetime # Importação necessária para validação de data

# ---------- Configuração ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

DB_PATH = "cardapio_balanca.db"


# ---------- Banco de dados ----------
def conectar():
    return sqlite3.connect(DB_PATH)



def criar_tabelas():
    con = conectar()
    cur = con.cursor()
    # CORREÇÃO 1: Adicionando 'validade' à tabela ingrediente e 'preco_base' à tabela prato
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS ingrediente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        peso_disponivel REAL NOT NULL,
        quantidade INTEGER 
        validade DATE -- Adicionado para suportar a lógica de preços/vencimento
    );

    CREATE TABLE IF NOT EXISTS prato (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco_base REAL -- Adicionado para armazenar o preço base
    );

    CREATE TABLE IF NOT EXISTS prato_ingrediente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prato_id INTEGER NOT NULL,
        ingrediente_id INTEGER NOT NULL,
        quantidade_necessaria REAL NOT NULL,
        FOREIGN KEY (prato_id) REFERENCES prato (id),
        FOREIGN KEY (ingrediente_id) REFERENCES ingrediente (id)
    );
    """
    )

    con.commit()
    con.close()


# ---------- Funções utilitárias de UI ----------
def show_info(msg):
    messagebox.showinfo("Info", msg)


def show_error(msg):
    messagebox.showerror("Erro", msg)


# ---------- Ações: Ingredientes ----------
def ui_adicionar_ingrediente():
    nome = ing_nome.get().strip()
    peso_txt = ing_peso.get().strip()
    validade_txt = ing_validade.get().strip() # NOVO CAMPO

    if not nome or not peso_txt or not validade_txt:
        show_error("Preencha nome, peso disponível e validade.")
        return

    try:
        peso = float(peso_txt)
    except ValueError:
        show_error("Peso deve ser um número (gramas).")
        return

    try:
        # Valida se a data está no formato YYYY-MM-DD
        datetime.strptime(validade_txt, "%Y-%m-%d") 
    except ValueError:
        show_error("Formato de validade inválido. Use YYYY-MM-DD.")
        return

    con = conectar()
    cur = con.cursor()
    # CORREÇÃO 2: Adicionando validade na inserção
    cur.execute("INSERT INTO ingrediente (nome, peso_disponivel, validade) VALUES (?, ?, ?)", (nome, peso, validade_txt))
    con.commit()
    con.close()

    ing_nome.delete(0, "end")
    ing_peso.delete(0, "end")
    ing_validade.delete(0, "end")
    carregar_ingredientes()
    show_info(f"Ingrediente '{nome}' adicionado com sucesso.")


def carregar_ingredientes():
    for i in tbl_ing.get_children():
        tbl_ing.delete(i)

    con = conectar()
    cur = con.cursor()
    # CORREÇÃO 3: Selecionando a validade
    cur.execute("SELECT id, nome, peso_disponivel, validade FROM ingrediente ORDER BY id")
    for iid, nome, peso, validade in cur.fetchall():
        # CORREÇÃO 4: Inserindo a validade na Treeview
        tbl_ing.insert("", "end", values=(iid, nome, f"{peso:.2f} g", validade))
    con.close()


def ui_remover_ingrediente():
    sel = tbl_ing.selection()
    if not sel:
        show_error("Selecione um ingrediente na tabela.")
        return

    iid = tbl_ing.item(sel[0], "values")[0]
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM prato_ingrediente WHERE ingrediente_id = ?", (iid,))
    cur.execute("DELETE FROM ingrediente WHERE id = ?", (iid,))
    con.commit()
    con.close()

    carregar_ingredientes()
    show_info(f"Ingrediente ID {iid} removido.")


# ---------- Ações: Pratos ----------
def ui_adicionar_prato():
    nome = prato_nome.get().strip()
    desc = prato_desc.get().strip()
    preco_txt = prato_preco.get().strip() # NOVO CAMPO

    if not nome or not preco_txt:
        show_error("Informe o nome e o preço base do prato.")
        return

    try:
        preco_base = float(preco_txt)
    except ValueError:
        show_error("O preço base deve ser um número.")
        return
        
    con = conectar()
    cur = con.cursor()
    # CORREÇÃO 5: Adicionando preco_base na inserção
    cur.execute("INSERT INTO prato (nome, descricao, preco_base) VALUES (?, ?, ?)", (nome, desc, preco_base))
    con.commit()
    con.close()

    prato_nome.delete(0, "end")
    prato_desc.delete(0, "end")
    prato_preco.delete(0, "end") # Limpar campo
    carregar_pratos()
    show_info(f"Prato '{nome}' adicionado com sucesso. Preço base: R${preco_base:.2f}")


def carregar_pratos():
    for i in tbl_pratos.get_children():
        tbl_pratos.delete(i)

    con = conectar()
    cur = con.cursor()
    # CORREÇÃO 6: Selecionando o preco_base
    cur.execute("SELECT id, nome, descricao, preco_base FROM prato ORDER BY id")
    pratos = cur.fetchall()
    # CORREÇÃO 7: Exibindo o preco_base
    for pid, nome, desc, preco in pratos:
        preco_txt = f"R${preco:.2f}" if preco is not None else "-"
        tbl_pratos.insert("", "end", values=(pid, nome, desc, preco_txt))
    con.close()
    carregar_receitas()


def carregar_receitas():
    for i in tbl_receita.get_children():
        tbl_receita.delete(i)

    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT p.id, p.nome, i.nome, pi.quantidade_necessaria
    FROM prato p
    LEFT JOIN prato_ingrediente pi ON pi.prato_id = p.id
    LEFT JOIN ingrediente i ON i.id = pi.ingrediente_id
    ORDER BY p.id
    """)
    for pid, prato_nome_lbl, ing_nome_lbl, qtd in cur.fetchall():
        ing_nome_lbl = ing_nome_lbl if ing_nome_lbl is not None else "-"
        qtd_txt = f"{qtd:.2f} g" if qtd is not None else "-"
        tbl_receita.insert("", "end", values=(pid, prato_nome_lbl, ing_nome_lbl, qtd_txt))
    con.close()


def ui_vincular_ingrediente():
    pid_txt = vinc_prato_id.get().strip()
    ing_txt = vinc_ing_id.get().strip()
    qtd_txt = vinc_qtd.get().strip()

    if not pid_txt or not ing_txt or not qtd_txt:
        show_error("Informe ID do prato, ID do ingrediente e quantidade (g).")
        return

    try:
        pid = int(pid_txt)
        iid = int(ing_txt)
        qtd = float(qtd_txt)
    except ValueError:
        show_error("IDs devem ser inteiros e quantidade deve ser número.")
        return

    con = conectar()
    cur = con.cursor()

    # valida existência de prato e ingrediente (melhor prática de verificação)
    cur.execute("SELECT 1 FROM prato WHERE id = ?", (pid,))
    if not cur.fetchone():
        con.close()
        show_error(f"Prato ID {pid} não existe.")
        return

    cur.execute("SELECT 1 FROM ingrediente WHERE id = ?", (iid,))
    if not cur.fetchone():
        con.close()
        show_error(f"Ingrediente ID {iid} não existe.")
        return

    # CORREÇÃO 8: Verifica se já existe o vínculo para fazer um UPDATE ou INSERT
    cur.execute("SELECT id FROM prato_ingrediente WHERE prato_id = ? AND ingrediente_id = ?", (pid, iid))
    existe = cur.fetchone()

    if existe:
        cur.execute("""
        UPDATE prato_ingrediente SET quantidade_necessaria = ?
        WHERE prato_id = ? AND ingrediente_id = ?
        """, (qtd, pid, iid))
        msg = f"Vínculo Prato {pid}/Ingrediente {iid} atualizado para {qtd}g."
    else:
        cur.execute("""
        INSERT INTO prato_ingrediente (prato_id, ingrediente_id, quantidade_necessaria)
        VALUES (?, ?, ?)
        """, (pid, iid, qtd))
        msg = f"Ingrediente {iid} vinculado ao prato {pid} com {qtd}g."
        
    con.commit()
    con.close()

    vinc_prato_id.delete(0, "end")
    vinc_ing_id.delete(0, "end")
    vinc_qtd.delete(0, "end")
    carregar_receitas()
    show_info(msg)


def ui_remover_prato():
    sel = tbl_pratos.selection()
    if not sel:
        show_error("Selecione um prato na tabela.")
        return

    pid = tbl_pratos.item(sel[0], "values")[0]
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM prato_ingrediente WHERE prato_id = ?", (pid,))
    cur.execute("DELETE FROM prato WHERE id = ?", (pid,))
    con.commit()
    con.close()

    carregar_pratos()
    show_info(f"Prato ID {pid} removido.")


# ---------- Ações: Verificação ----------
def ui_verificar_disponibilidade():
    pid_txt = verif_prato_id.get().strip()
    if not pid_txt:
        show_error("Informe o ID do prato para verificar.")
        return

    try:
        pid = int(pid_txt)
    except ValueError:
        show_error("ID do prato deve ser inteiro.")
        return

    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT 
        i.nome, 
        i.peso_disponivel, 
        pi.quantidade_necessaria,
        p.nome
    FROM prato_ingrediente pi
    JOIN ingrediente i ON i.id = pi.ingrediente_id
    JOIN prato p ON p.id = pi.prato_id
    WHERE pi.prato_id = ?
    """, (pid,))
    itens = cur.fetchall()
    con.close()

    if not itens:
        show_error("Prato não encontrado ou sem ingredientes vinculados.")
        return
    
    # Pega o nome do prato para exibir no resultado
    prato_nome_verif = itens[0][3]

    linhas = []
    pode = True
    for nome, disp, nec, _ in itens:
        ok = disp >= nec
        if not ok:
            pode = False
        linhas.append(f"- {nome}: {disp:.2f} g disp. / {nec:.2f} g nec. → {'OK' if ok else 'Insuficiente'}")

    resumo = "\n".join(linhas)
    status_final = "\n\n🍽️ Pode preparar!" if pode else "\n\n⚠️ Ingredientes insuficientes."
    verif_result.configure(text=f"Verificação do prato {pid} ({prato_nome_verif}):\n{resumo}{status_final}")


# ---------- Interface ----------
janela = ctk.CTk()
janela.title("🍳 Gerenciador de Cardápio (Estoque e Receitas)")
janela.geometry("1200x700") # Aumentando a largura

tabs = ctk.CTkTabview(janela)
tabs.pack(padx=12, pady=12, fill="both", expand=True)

# --- Aba Ingredientes ---
aba_ing = tabs.add("Ingredientes")

frm_ing_left = ctk.CTkFrame(aba_ing)
frm_ing_left.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(frm_ing_left, text="Adicionar ingrediente", font=("Segoe UI", 14, "bold")).pack(pady=(0, 8))
ing_nome = ctk.CTkEntry(frm_ing_left, placeholder_text="Nome")
ing_nome.pack(pady=4)
ing_peso = ctk.CTkEntry(frm_ing_left, placeholder_text="Peso disponível (g)")
ing_peso.pack(pady=4)
# NOVO CAMPO: Validade
ing_validade = ctk.CTkEntry(frm_ing_left, placeholder_text="Validade (YYYY-MM-DD)")
ing_validade.pack(pady=4)
# FIM NOVO CAMPO
ctk.CTkButton(frm_ing_left, text="➕ Adicionar", command=ui_adicionar_ingrediente).pack(pady=8)
ctk.CTkButton(frm_ing_left, text="🗑️ Remover selecionado", fg_color="red", command=ui_remover_ingrediente).pack(pady=4)
ctk.CTkButton(frm_ing_left, text="🔄 Atualizar lista", command=carregar_ingredientes).pack(pady=4)

frm_ing_right = ctk.CTkFrame(aba_ing)
frm_ing_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
# CORREÇÃO 9: Adicionando a coluna Validade
tbl_ing = ttk.Treeview(frm_ing_right, columns=("ID", "Nome", "Disponível", "Validade"), show="headings", height=18)
tbl_ing.heading("ID", text="ID")
tbl_ing.heading("Nome", text="Nome")
tbl_ing.heading("Disponível", text="Disponível")
tbl_ing.heading("Validade", text="Validade")
tbl_ing.column("ID", width=40, anchor="center")
tbl_ing.column("Nome", width=200, anchor="w")
tbl_ing.column("Disponível", width=120, anchor="center")
tbl_ing.column("Validade", width=120, anchor="center")
tbl_ing.pack(fill="both", expand=True)

# --- Aba Pratos e Receitas ---
aba_pratos = tabs.add("Pratos e receitas")

frm_prato_left = ctk.CTkFrame(aba_pratos)
frm_prato_left.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(frm_prato_left, text="Adicionar prato", font=("Segoe UI", 14, "bold")).pack(pady=(0, 8))
prato_nome = ctk.CTkEntry(frm_prato_left, placeholder_text="Nome do prato")
prato_nome.pack(pady=4)
prato_desc = ctk.CTkEntry(frm_prato_left, placeholder_text="Descrição")
prato_desc.pack(pady=4)
# NOVO CAMPO: Preço Base
prato_preco = ctk.CTkEntry(frm_prato_left, placeholder_text="Preço Base (R$)")
prato_preco.pack(pady=4)
# FIM NOVO CAMPO
ctk.CTkButton(frm_prato_left, text="➕ Adicionar prato", command=ui_adicionar_prato).pack(pady=8)
ctk.CTkButton(frm_prato_left, text="🗑️ Remover prato (selecionado)", fg_color="red", command=ui_remover_prato).pack(pady=4)
ctk.CTkButton(frm_prato_left, text="🔄 Atualizar listas", command=carregar_pratos).pack(pady=4)

ctk.CTkLabel(frm_prato_left, text="Vincular ingrediente ao prato", font=("Segoe UI", 14, "bold")).pack(pady=(16, 8))
vinc_prato_id = ctk.CTkEntry(frm_prato_left, placeholder_text="ID do prato")
vinc_prato_id.pack(pady=4)
vinc_ing_id = ctk.CTkEntry(frm_prato_left, placeholder_text="ID do ingrediente")
vinc_ing_id.pack(pady=4)
vinc_qtd = ctk.CTkEntry(frm_prato_left, placeholder_text="Quantidade (g)")
vinc_qtd.pack(pady=4)
ctk.CTkButton(frm_prato_left, text="🔗 Vincular/Atualizar", command=ui_vincular_ingrediente).pack(pady=8)

frm_prato_right = ctk.CTkFrame(aba_pratos)
frm_prato_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
ctk.CTkLabel(frm_prato_right, text="Pratos", font=("Segoe UI", 13, "bold")).pack(anchor="w")
# CORREÇÃO 10: Adicionando a coluna Preço Base
tbl_pratos = ttk.Treeview(frm_prato_right, columns=("ID", "Nome", "Descrição", "Preço Base"), show="headings", height=10)
tbl_pratos.heading("ID", text="ID")
tbl_pratos.heading("Nome", text="Nome")
tbl_pratos.heading("Descrição", text="Descrição")
tbl_pratos.heading("Preço Base", text="Preço Base")
tbl_pratos.column("ID", width=40, anchor="center")
tbl_pratos.column("Nome", width=150, anchor="w")
tbl_pratos.column("Descrição", width=250, anchor="w")
tbl_pratos.column("Preço Base", width=80, anchor="center")
tbl_pratos.pack(fill="x", padx=0, pady=(4, 12))

ctk.CTkLabel(frm_prato_right, text="Receitas (ingredientes por prato)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
tbl_receita = ttk.Treeview(frm_prato_right, columns=("Prato ID", "Prato", "Ingrediente", "Qtd (g)"), show="headings", height=10)
for col in ("Prato ID", "Prato", "Ingrediente", "Qtd (g)"):
    tbl_receita.heading(col, text=col)
    tbl_receita.column(col, anchor="center")
tbl_receita.pack(fill="both", expand=True, pady=(4, 0))

# --- Aba Verificação ---
aba_verif = tabs.add("Verificar disponibilidade")
verif_prato_id = ctk.CTkEntry(aba_verif, placeholder_text="ID do prato")
verif_prato_id.pack(pady=10)
ctk.CTkButton(aba_verif, text="Verificar", command=ui_verificar_disponibilidade).pack(pady=6)
verif_result = ctk.CTkLabel(aba_verif, text="", justify="left")
verif_result.pack(pady=10, fill="x")

# ---------- Inicialização ----------
criar_tabelas()
carregar_ingredientes()
carregar_pratos()

janela.mainloop()