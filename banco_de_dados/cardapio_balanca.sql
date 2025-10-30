-- Criação das tabelas principais do cardápio inteligente

DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS categorias;

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    categoria_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Inserindo categorias iniciais
INSERT INTO categorias (nome) VALUES ('Bebidas');
INSERT INTO categorias (nome) VALUES ('Pratos');
INSERT INTO categorias (nome) VALUES ('Sobremesas');

-- Inserindo produtos iniciais
INSERT INTO produtos (nome, preco, categoria_id) VALUES ('Refrigerante Lata', 5.00, 1);
INSERT INTO produtos (nome, preco, categoria_id) VALUES ('Suco Natural', 7.50, 1);
INSERT INTO produtos (nome, preco, categoria_id) VALUES ('Lasanha', 22.00, 2);
INSERT INTO produtos (nome, preco, categoria_id) VALUES ('Bolo de Chocolate', 8.00, 3);
