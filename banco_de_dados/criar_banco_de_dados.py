import sqlite3

# Conecta (cria o arquivo cardapio_balanca.db)
con = sqlite3.connect("cardapio_balanca.db")
cur = con.cursor()

# Lê o conteúdo do arquivo SQL
with open("cardapio_balanca.sql", "r", encoding="utf-8") as f:
    script = f.read()

# Executa os comandos SQL
cur.executescript(script)
con.commit()
con.close()

print("Banco de dados 'cardapio_balanca.db' criado com sucesso!")
