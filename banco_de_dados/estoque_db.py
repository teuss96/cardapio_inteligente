import tkinter as tk

from tkinter import ttk, messagebox

import sqlite3



# === Banco de Dados ===

conn = sqlite3.connect("estoque.db")

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS produtos (

    codigo TEXT PRIMARY KEY,

    nome TEXT NOT NULL,

    validade TEXT,

    Peso TEXT,

    quantidade INTEGER DEFAULT 0

)

""")

conn.commit()



# === Funções Gerais ===

def trocar_tela(frame_destino):

    for frame in [frame_inicio, frame_cadastrar, frame_buscar, frame_listar]:

        frame.pack_forget()

    frame_destino.pack(fill="both", expand=True)



def voltar_inicio():

    limpar_campos()

    frame_detalhes.pack_forget()

    resultado.set("")

    trocar_tela(frame_inicio)



# === Cadastro Inteligente ===

def verificar_codigo(event=None):

    codigo = entry_codigo.get().strip()

    if not codigo:

        return



    cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))

    produto = cursor.fetchone()



    if produto:

        # Produto existe -> pedir quantidade a adicionar

        frame_adicionar.pack(pady=10)

        lbl_nome_existente.configure(text=f"Produto: {produto[1]}")

        entry_qtd_add.focus()

    else:

        # Produto novo -> mostrar campos de cadastro

        frame_detalhes.pack(pady=10)

        entry_nome.focus()



def adicionar_existente():

    codigo = entry_codigo.get().strip()

    try:

        qtd_add = int(entry_qtd_add.get())

        if qtd_add <= 0:

            raise ValueError

    except ValueError:

        messagebox.showerror("Erro", "Informe uma quantidade válida (inteiro positivo).")

        return



    cursor.execute("SELECT quantidade FROM produtos WHERE codigo = ?", (codigo,))

    produto = cursor.fetchone()

    if not produto:

        messagebox.showerror("Erro", "Produto não encontrado!")

        return



    nova_qtd = produto[0] + qtd_add

    cursor.execute("UPDATE produtos SET quantidade = ? WHERE codigo = ?", (nova_qtd, codigo))

    conn.commit()



    messagebox.showinfo("Atualizado", f"Quantidade atualizada: {nova_qtd} unidades.")

    limpar_campos()

    frame_adicionar.pack_forget()



def cadastrar_produto():

    codigo = entry_codigo.get().strip()

    nome = entry_nome.get().strip()

    validade = entry_validade.get().strip()

    Peso = entry_Peso.get().strip()

    qtd_txt = entry_qtd.get().strip()



    if not codigo or not nome:

        messagebox.showwarning("Aviso", "Preencha o código e o nome.")

        return



    try:

        quantidade = int(qtd_txt) if qtd_txt else 1

        if quantidade <= 0:

            raise ValueError

    except ValueError:

        messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo.")

        return



    cursor.execute("""

        INSERT INTO produtos (codigo, nome, validade, Peso, quantidade)

        VALUES (?, ?, ?, ?, ?)

    """, (codigo, nome, validade, Peso, quantidade))

    conn.commit()



    messagebox.showinfo("Cadastrado", f"Produto '{nome}' cadastrado com sucesso!")

    limpar_campos()

    frame_detalhes.pack_forget()



def limpar_campos():

    entry_codigo.delete(0, tk.END)

    entry_nome.delete(0, tk.END)

    entry_validade.delete(0, tk.END)

    entry_Peso.delete(0, tk.END)

    entry_qtd.delete(0, tk.END)

    entry_qtd_add.delete(0, tk.END)

    lbl_nome_existente.configure(text="")



# === Função de Busca ===

def buscar_produto():

    codigo = entry_busca.get().strip()

    cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))

    produto = cursor.fetchone()



    if produto:

        resultado.set(f"Produto: {produto[1]}\nValidade: {produto[2]}\nPeso: {produto[3]}\nQuantidade: {produto[4]}")

    else:

        resultado.set("Produto não encontrado.")

   

# === Função de Listagem ===

def listar_produtos():

    for item in tree.get_children():

        tree.delete(item)

    cursor.execute("SELECT * FROM produtos")

    for p in cursor.fetchall():

        tree.insert("", "end", values=p)



# === Interface ===

root = tk.Tk()

root.title("Sistema de Estoque com Leitor")

root.geometry("700x500")



# --- Tela Inicial ---

frame_inicio = tk.Frame(root)

frame_inicio.pack(fill="both", expand=True)

tk.Label(frame_inicio, text="📦 Sistema de Estoque", font=("Arial", 20, "bold")).pack(pady=40)

tk.Button(frame_inicio, text="1 - Cadastrar com Leitor", width=30, height=2, command=lambda: trocar_tela(frame_cadastrar)).pack(pady=10)

tk.Button(frame_inicio, text="2 -  Buscar Produto", width=30, height=2, command=lambda: trocar_tela(frame_buscar)).pack(pady=10)

tk.Button(frame_inicio, text="3 - Listar Produtos", width=30, height=2, command=lambda: [trocar_tela(frame_listar), listar_produtos()]).pack(pady=10)



# --- Tela de Cadastro ---

frame_cadastrar = tk.Frame(root)

tk.Label(frame_cadastrar, text="Cadastrar com Leitor", font=("Arial", 18, "bold")).pack(pady=10)



tk.Label(frame_cadastrar, text="Passe o código de barras:").pack()

entry_codigo = tk.Entry(frame_cadastrar, width=30)

entry_codigo.pack(pady=5)

entry_codigo.bind("<Return>", verificar_codigo)



# Campos para adicionar quantidade ao existente

frame_adicionar = tk.Frame(frame_cadastrar)

lbl_nome_existente = tk.Label(frame_adicionar, text="", font=("Arial", 12))

lbl_nome_existente.grid(row=0, column=0, columnspan=2, pady=5)

tk.Label(frame_adicionar, text="Quantidade a adicionar:").grid(row=1, column=0)

entry_qtd_add = tk.Entry(frame_adicionar, width=10)

entry_qtd_add.grid(row=1, column=1)

tk.Button(frame_adicionar, text="Adicionar", command=adicionar_existente).grid(row=2, column=0, columnspan=2, pady=8)



# Campos para novo produto

frame_detalhes = tk.Frame(frame_cadastrar)

tk.Label(frame_detalhes, text="Nome:").grid(row=0, column=0)

entry_nome = tk.Entry(frame_detalhes)

entry_nome.grid(row=0, column=1)



tk.Label(frame_detalhes, text="Validade (AAAA-MM-DD):").grid(row=1, column=0)

entry_validade = tk.Entry(frame_detalhes)

entry_validade.grid(row=1, column=1)



tk.Label(frame_detalhes, text="Peso:").grid(row=2, column=0)

entry_Peso = tk.Entry(frame_detalhes)

entry_Peso.grid(row=2, column=1)



tk.Label(frame_detalhes, text="Quantidade inicial:").grid(row=3, column=0)

entry_qtd = tk.Entry(frame_detalhes)

entry_qtd.grid(row=3, column=1)



tk.Button(frame_detalhes, text="Salvar Novo Produto", command=cadastrar_produto).grid(row=4, column=0, columnspan=2, pady=10)



tk.Button(frame_cadastrar, text="Voltar", command=voltar_inicio).pack(pady=10)



# --- Tela de Busca ---

frame_buscar = tk.Frame(root)

tk.Label(frame_buscar, text="Buscar Produto", font=("Arial", 18, "bold")).pack(pady=10)

entry_busca = tk.Entry(frame_buscar, width=40)

entry_busca.pack(pady=5)

entry_busca.bind("<Return>", buscar_produto)

# tk.Button(frame_buscar, text="Buscar", command=buscar_produto).pack(pady=5)

resultado = tk.StringVar()


tk.Label(frame_buscar, textvariable=resultado, font=("Arial", 12), justify="left").pack(pady=10)

tk.Button(frame_buscar, text="Voltar", command=voltar_inicio).pack()



# --- Tela de Listagem ---

frame_listar = tk.Frame(root)

tk.Label(frame_listar, text="Lista de Produtos", font=("Arial", 18, "bold")).pack(pady=10)

cols = ("Código", "Nome", "Validade", "Peso", "Quantidade")

tree = ttk.Treeview(frame_listar, columns=cols, show="headings")

for col in cols:

    tree.heading(col, text=col)

tree.pack(expand=True, fill="both", padx=10, pady=10)

tk.Button(frame_listar, text="Voltar", command=voltar_inicio).pack(pady=10)



root.mainloop()

conn.close()