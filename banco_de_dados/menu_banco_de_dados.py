import sqlite3

# ------------------------------
# Função para conectar ao banco
# ------------------------------
def conectar():
    return sqlite3.connect("cardapio_balanca.db")

# ------------------------------
# Função para criar as tabelas (apenas por segurança)
# ------------------------------
def criar_tabelas():
    con = conectar()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS ingrediente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        peso_disponivel REAL NOT NULL,
        validade DATE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS prato (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT
    );

    CREATE TABLE IF NOT EXISTS prato_ingrediente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prato_id INTEGER NOT NULL,
        ingrediente_id INTEGER NOT NULL,
        quantidade_necessaria REAL NOT NULL,
        FOREIGN KEY (prato_id) REFERENCES prato (id),
        FOREIGN KEY (ingrediente_id) REFERENCES ingrediente (id)
    );
    """)
    con.commit()
    con.close()

# ------------------------------
# Adicionar ingrediente
# ------------------------------
def adicionar_ingrediente():
    nome = input("Nome do ingrediente: ").strip()
    peso = float(input("Peso disponível (em gramas): "))

    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO ingrediente (nome, peso_disponivel) VALUES (?, ?)", (nome, peso))
    con.commit()
    con.close()

    print(f"Ingrediente '{nome}' adicionado com sucesso!\n")

# ------------------------------
# Listar ingredientes
# ------------------------------
def listar_ingredientes():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nome, peso_disponivel FROM ingrediente")
    ingredientes = cur.fetchall()
    con.close()

    if not ingredientes:
        print("\n Nenhum ingrediente cadastrado.\n")
        return []

    print("\n Ingredientes disponíveis:")
    for i in ingredientes:
        print(f"  ID {i[0]} - {i[1]} ({i[2]}g disponíveis)")
    print()
    return ingredientes

# ------------------------------
# Adicionar prato
# ------------------------------
def adicionar_prato():
    nome_prato = input("Nome do prato: ").strip()
    descricao = input("Descrição do prato: ").strip()

    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO prato (nome, descricao) VALUES (?, ?)", (nome_prato, descricao))
    prato_id = cur.lastrowid

    print("\nAgora, adicione os ingredientes desse prato.")
    listar_ingredientes()

    while True:
        ingrediente_id = input("Digite o ID do ingrediente (ou '0' para terminar): ")
        if ingrediente_id == "0":
            break

        quantidade = float(input("Quantidade necessária (g): "))
        cur.execute(
            "INSERT INTO prato_ingrediente (prato_id, ingrediente_id, quantidade_necessaria) VALUES (?, ?, ?)",
            (prato_id, ingrediente_id, quantidade)
        )
        con.commit()

    con.close()
    print(f" Prato '{nome_prato}' cadastrado com sucesso!\n")

# ------------------------------
# Listar pratos
# ------------------------------
def listar_pratos():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nome, descricao FROM prato")
    pratos = cur.fetchall()

    if not pratos:
        print("\n Nenhum prato cadastrado.\n")
        return []

    print("\n Pratos cadastrados:")
    for p in pratos:
        print(f"\n {p[0]} - {p[1]} ({p[2]})")
        cur.execute("""
            SELECT ingrediente.nome, prato_ingrediente.quantidade_necessaria
            FROM prato_ingrediente
            JOIN ingrediente ON ingrediente.id = prato_ingrediente.ingrediente_id
            WHERE prato_ingrediente.prato_id = ?
        """, (p[0],))
        ingredientes = cur.fetchall()
        for ing in ingredientes:
            print(f"   - {ing[0]}: {ing[1]}g")
    con.close()
    print()
    return pratos

# ------------------------------
# Verificar disponibilidade de um prato
# ------------------------------
def verificar_prato(prato_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT i.nome, i.peso_disponivel, pi.quantidade_necessaria
        FROM prato_ingrediente pi
        JOIN ingrediente i ON i.id = pi.ingrediente_id
        WHERE pi.prato_id = ?
    """, (prato_id,))
    itens = cur.fetchall()
    con.close()

    if not itens:
        print(" Prato não encontrado.")
        return

    print(f"\n Verificando disponibilidade do prato ID {prato_id}:")
    for nome, disponivel, necessario in itens:
        status = " OK" if disponivel >= necessario else " Insuficiente"
        print(f"{nome}: {disponivel}g disponíveis, {necessario}g necessários → {status}")

# ------------------------------
# Remover ingrediente
# ------------------------------
def remover_ingrediente():
    ingredientes = listar_ingredientes()
    if not ingredientes:
        return

    id_ing = input("Digite o ID do ingrediente que deseja remover: ")
    confirmar = input(f"Tem certeza que deseja remover o ingrediente ID {id_ing}? (s/n): ").lower()

    if confirmar == "s":
        con = conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM prato_ingrediente WHERE ingrediente_id = ?", (id_ing,))
        cur.execute("DELETE FROM ingrediente WHERE id = ?", (id_ing,))
        con.commit()
        con.close()
        print(" Ingrediente removido com sucesso!\n")
    else:
        print(" Remoção cancelada.\n")

# ------------------------------
# Remover prato
# ------------------------------
def remover_prato():
    pratos = listar_pratos()
    if not pratos:
        return

    id_prato = input("Digite o ID do prato que deseja remover: ")
    confirmar = input(f"Tem certeza que deseja remover o prato ID {id_prato}? (s/n): ").lower()

    if confirmar == "s":
        con = conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM prato_ingrediente WHERE prato_id = ?", (id_prato,))
        cur.execute("DELETE FROM prato WHERE id = ?", (id_prato,))
        con.commit()
        con.close()
        print(" Prato removido com sucesso!\n")
    else:
        print(" Remoção cancelada.\n")

# ------------------------------
# Menu principal
# ------------------------------
def menu():
    criar_tabelas()
    while True:
        print("====  MENU CARDÁPIO INTELIGENTE ====")
        print("1️  Adicionar ingrediente")
        print("2️  Adicionar prato")
        print("3️  Listar ingredientes")
        print("4️  Listar pratos e receitas")
        print("5️  Verificar disponibilidade de prato")
        print("6️  Remover ingrediente")
        print("7️  Remover prato")
        print("0️  Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_ingrediente()
        elif opcao == "2":
            adicionar_prato()
        elif opcao == "3":
            listar_ingredientes()
        elif opcao == "4":
            listar_pratos()
        elif opcao == "5":
            id_prato = input("Digite o ID do prato para verificar: ")
            verificar_prato(id_prato)
        elif opcao == "6":
            remover_ingrediente()
        elif opcao == "7":
            remover_prato()
        elif opcao == "0":
            print(" Saindo do sistema. Até logo!")
            break
        else:
            print(" Opção inválida. Tente novamente.\n")

# ------------------------------
# Executar o programa
# ------------------------------
if __name__ == "__main__":
    menu()
