import sqlite3
import os

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(DIRETORIO, 'operadora.db')

def conectar():
    return sqlite3.connect(BANCO)

def buscar_dados_cliente(cpf):
    """Busca dados usando LEFT JOIN para evitar bloqueio de login se faltar fatura."""
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    query = '''
        SELECT 
            c.nome, 
            IFNULL(f.valor_total, 0.0) as fatura_atual, 
            0.00 as fatura_proxima, 
            IFNULL(substr(f.vencimento, 9, 2) || '/' || substr(f.vencimento, 6, 2) || '/' || substr(f.vencimento, 1, 4), 'Sem vencimento') as vencimento,
            IFNULL(substr(f.fechamento, 9, 2) || '/' || substr(f.fechamento, 6, 2) || '/' || substr(f.fechamento, 1, 4), 'Sem fechamento') as fechamento,
            IFNULL(f.status_fatura, 'Nenhuma fatura em aberto') as status_fatura
        FROM clientes c
        LEFT JOIN cartoes ct ON c.id = ct.cliente_id
        LEFT JOIN faturas f ON ct.id = f.cartao_id
        WHERE c.cpf = ?
        LIMIT 1
    '''
    
    cursor.execute(query, (cpf,))
    resultado = cursor.fetchone()
    conexao.close()
    
    if resultado:
        return dict(resultado)
    return None

def buscar_dados_cartoes(cpf):
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    query = '''
        SELECT 
            ct.id as cartao_id, 
            ct.numero_final, 
            ct.limite_total, 
            ct.limite_disponivel, 
            ct.status_cartao
        FROM clientes c
        INNER JOIN cartoes ct ON c.id = ct.cliente_id
        WHERE c.cpf = ?
    '''
    
    cursor.execute(query, (cpf,))
    resultado = cursor.fetchall()
    conexao.close()
    
    if resultado:
        return [dict(linha) for linha in resultado]
    return None

def buscar_ultima_transacao(cartao_id):
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    query = '''
        SELECT estabelecimento, valor, data_hora 
        FROM transacoes 
        WHERE cartao_id = ? 
        ORDER BY id DESC LIMIT 1
    '''
    
    cursor.execute(query, (cartao_id,))
    resultado = cursor.fetchone()
    conexao.close()
    
    if resultado:
        return dict(resultado)
    return None

def inserir_interacao(cpf_cliente, mensagem_usuario, resposta_bot):
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT id FROM clientes WHERE cpf = ?', (cpf_cliente,))
    cliente = cursor.fetchone()
    
    if cliente:
        cliente_id = cliente[0]
        cursor.execute('''
            INSERT INTO historico_chat (cliente_id, mensagem_usuario, resposta_bot)
            VALUES (?, ?, ?)
        ''', (cliente_id, mensagem_usuario, resposta_bot))
        conexao.commit()
        
    conexao.close()