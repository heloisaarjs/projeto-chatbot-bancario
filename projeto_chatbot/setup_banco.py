import sqlite3
import os

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(DIRETORIO, 'operadora.db')

def popular_banco():
    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.executescript('''
        DROP TABLE IF EXISTS historico_chat;
        DROP TABLE IF EXISTS transacoes;
        DROP TABLE IF EXISTS faturas;
        DROP TABLE IF EXISTS cartoes;
        DROP TABLE IF EXISTS clientes;

        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL
        );

        CREATE TABLE cartoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            numero_final TEXT NOT NULL,
            limite_total REAL,
            limite_disponivel REAL,
            status_cartao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE faturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cartao_id INTEGER,
            mes_referencia TEXT,
            valor_total REAL,
            vencimento TEXT,
            fechamento TEXT,
            status_fatura TEXT,
            FOREIGN KEY (cartao_id) REFERENCES cartoes(id)
        );

        CREATE TABLE transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cartao_id INTEGER,
            data_hora TEXT DEFAULT CURRENT_TIMESTAMP,
            estabelecimento TEXT,
            valor REAL,
            FOREIGN KEY (cartao_id) REFERENCES cartoes(id)
        );

        CREATE TABLE historico_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            mensagem_usuario TEXT NOT NULL,
            resposta_bot TEXT NOT NULL,
            data_hora TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );
    ''')

    clientes = [
        ('João Silva', '11122233344'),
        ('Maria Souza', '99988877766'),
        ('Carlos Oliveira', '55544433322')
    ]
    cursor.executemany('INSERT INTO clientes (nome, cpf) VALUES (?, ?)', clientes)

    cartoes = [
        (1, '4321', 5000.00, 3750.00, 'Ativo'),
        (2, '9876', 3000.00, 1200.50, 'Ativo'),
        (2, '1122', 1500.00, 1500.00, 'Bloqueado'),
        (3, '5566', 10000.00, 8500.00, 'Em trânsito') # ID 4
    ]
    cursor.executemany('''
        INSERT INTO cartoes (cliente_id, numero_final, limite_total, limite_disponivel, status_cartao) 
        VALUES (?, ?, ?, ?, ?)
    ''', cartoes)

    # CORREÇÃO: Fatura do Carlos associada ao ID 4
    faturas = [
        (1, '05/2026', 1250.00, '2026-06-15', '2026-06-05', 'Fechada'),
        (2, '05/2026', 1799.50, '2026-06-20', '2026-06-10', 'Aberta'),
        (4, '05/2026', 1500.00, '2026-06-10', '2026-06-01', 'Vencida') 
    ]
    cursor.executemany('''
        INSERT INTO faturas (cartao_id, mes_referencia, valor_total, vencimento, fechamento, status_fatura) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', faturas)

    # CORREÇÃO: Transação do Carlos associada ao ID 4
    transacoes = [
        (1, 'Supermercado Extra', 350.00),
        (1, 'Posto Ipiranga', 150.00),
        (2, 'iFood', 85.50),
        (4, 'Passagens Aéreas', 1200.00) 
    ]
    cursor.executemany('''
        INSERT INTO transacoes (cartao_id, estabelecimento, valor) 
        VALUES (?, ?, ?)
    ''', transacoes)

    conexao.commit()
    conexao.close()
    print("Banco de dados corrigido e populado com sucesso!")

if __name__ == "__main__":
    popular_banco()