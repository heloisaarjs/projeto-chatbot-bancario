import pandas as pd
import json
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import crud

app = Flask(__name__)

# Memória temporária da conversa e do login
sessoes_clientes = {}
cpf_logado = ""


# MACHINE LEARNING (Treinamento do Bot)
perguntas = pd.read_csv('perguntas.csv', sep=',')
with open("respostas.json", "r", encoding="utf-8") as arquivo:
    respostas = json.load(arquivo)

vetorizador = CountVectorizer()
X = vetorizador.fit_transform(perguntas['frase'].astype(str))
modelo = MultinomialNB()
modelo.fit(X, perguntas['categoria'].astype(str))

def classificar_mensagem(texto):
    texto_vetorizado = vetorizador.transform([texto.lower()])
    categoria_prevista = modelo.predict(texto_vetorizado)[0]
    return categoria_prevista, respostas.get(categoria_prevista, "Erro interno.")


# ROTAS FLASK (Comunicação com o Site)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/validar_cpf', methods=['POST'])
def validar_cpf():
    global cpf_logado
    dados = request.get_json()
    cpf_limpo = ''.join(filter(str.isdigit, str(dados.get('cpf'))))
    
    dados_cliente = crud.buscar_dados_cliente(cpf_limpo)
    if dados_cliente:
        cpf_logado = cpf_limpo
        sessoes_clientes[cpf_logado] = 'inicio'
        return jsonify({'sucesso': True, 'nome': dados_cliente['nome']})
    return jsonify({'sucesso': False})

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    global cpf_logado
    dados = request.get_json()
    mensagem_usuario = dados.get('mensagem').lower()
    cpf = cpf_logado 
    
    if not cpf:
        return jsonify({'resposta': "Sessão expirada. Recarregue a página."})

    # 1. COMANDOS GERAIS: LOGOUT E VOLTAR
    if mensagem_usuario in ['encerrar', 'sair', 'logout', 'tchau']:
        resposta_bot = "Atendimento encerrado com sucesso! Recarregue a página (F5) para inserir um novo CPF."
        crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
        
        cpf_logado = "" 
        if cpf in sessoes_clientes:
            del sessoes_clientes[cpf]
            
        return jsonify({'resposta': resposta_bot})

    if mensagem_usuario in ['voltar', 'menu', 'inicio']:
        sessoes_clientes[cpf] = 'inicio'
        resposta_bot = "Voltamos ao menu principal! O que deseja consultar?"
        crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
        return jsonify({'resposta': resposta_bot})

    estado_atual = sessoes_clientes.get(cpf, 'inicio')

    # 2. FLUXO SECUNDÁRIO: OPÇÕES DA FATURA
    if estado_atual == 'fatura_opcoes':
        if '3' in mensagem_usuario:
            sessoes_clientes[cpf] = 'inicio'
            resposta_bot = "Voltamos ao menu principal! O que deseja consultar agora?"
            crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
            return jsonify({'resposta': resposta_bot})
        
        elif '1' in mensagem_usuario or 'pagar' in mensagem_usuario:
            resposta_bot = (
                "Aqui está o seu código de barras:\n"
                "34191.09008.52482.11111\n\n"
                "Deseja fazer mais alguma coisa com a fatura?\n"
                "[ 2 ] Parcelar\n"
                "[ 3 ] Voltar ao menu principal"
            )
            crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
            return jsonify({'resposta': resposta_bot})
        
        elif '2' in mensagem_usuario or 'parcelar' in mensagem_usuario:
            resposta_bot = (
                "Enviamos as opções de parcelamento em até 12x para o seu e-mail cadastrado!\n\n"
                "Deseja fazer mais alguma coisa com a fatura?\n"
                "[ 1 ] Pagar\n"
                "[ 3 ] Voltar ao menu principal"
            )
            crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
            return jsonify({'resposta': resposta_bot})
        
        else:
            resposta_bot = "Opção inválida. Escolha:\n[ 1 ] Pagar\n[ 2 ] Parcelar\n[ 3 ] Voltar"
            crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
            return jsonify({'resposta': resposta_bot})


    # 3. FLUXO SECUNDÁRIO: VALIDAÇÃO DO CARTÃO E TRANSAÇÃO
    if estado_atual == 'aguardando_final_cartao':
        digitos_digitados = ''.join(filter(str.isdigit, mensagem_usuario))
        
        if len(digitos_digitados) >= 4:
            final_buscado = digitos_digitados[-4:] 
            cartoes = crud.buscar_dados_cartoes(cpf)
            
            cartao_encontrado = None
            if cartoes:
                for c in cartoes:
                    if c['numero_final'] == final_buscado:
                        cartao_encontrado = c
                        break
            
            if cartao_encontrado:
                disp = f"R$ {cartao_encontrado['limite_disponivel']:.2f}".replace('.', ',')
                tot = f"R$ {cartao_encontrado['limite_total']:.2f}".replace('.', ',')
                
                ultima_transacao = crud.buscar_ultima_transacao(cartao_encontrado['cartao_id'])
                texto_transacao = "\n  • Última Transação: Nenhuma transação recente encontrada."
                
                if ultima_transacao:
                    valor_trans = f"R$ {ultima_transacao['valor']:.2f}".replace('.', ',')
                    texto_transacao = f"\n  • Última Transação: {ultima_transacao['estabelecimento']} no valor de {valor_trans}"

                resposta_bot = (
                    f"💳 Localizei o cartão final {cartao_encontrado['numero_final']}:\n"
                    f"  • Status: {cartao_encontrado['status_cartao']}\n"
                    f"  • Limite Disponível: {disp}\n"
                    f"  • Limite Total: {tot}{texto_transacao}\n\n"
                    "Posso te ajudar com mais alguma informação? "
                    "(Digite 'SAIR' para reiniciar o atendimento)"
                )
                sessoes_clientes[cpf] = 'inicio' 
            else:
                resposta_bot = "Não localizei nenhum cartão com esse final atrelado ao seu CPF. Digite os 4 últimos dígitos novamente ou digite 'Voltar'."
        else:
            resposta_bot = "Por favor, digite os 4 números finais do seu cartão."
            
        crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
        return jsonify({'resposta': resposta_bot})


    # 4. FLUXO PRINCIPAL (IA + REGRAS DE OURO)
    categoria, resposta_ml = classificar_mensagem(mensagem_usuario)
    
    # REGRAS DE OURO (Overrides): Força a categoria correta através de palavras-chave
    palavras_sensiveis = ['aumentar', 'diminuir', 'senha', 'bloquear', 'roubado', 'cancelar']
    palavras_cartao = ['transação', 'transacao', 'compra', 'limite', 'cartões', 'cartoes', 'cartão', 'cartao']
    palavras_fatura = ['fatura', 'boleto', 'pagar', 'parcelar', 'vencimento', 'fechou']

    if any(p in mensagem_usuario for p in palavras_sensiveis):
        categoria = 'seguranca_app'
    elif any(p in mensagem_usuario for p in palavras_cartao):
        categoria = 'cartao_limite'
    elif any(p in mensagem_usuario for p in palavras_fatura):
        categoria = 'fatura'

    # --- LÓGICA DE DECISÃO ---
    if categoria == 'fatura':
        cliente = crud.buscar_dados_cliente(cpf)
        if cliente:
            v_atual = f"R$ {cliente['fatura_atual']:.2f}".replace('.', ',')
            resposta_bot = (
                f"Aqui estão os dados da sua fatura:\n"
                f"• Status: {cliente['status_fatura']}\n"
                f"• Valor: {v_atual}\n"
                f"• Vencimento: {cliente['vencimento']}\n\n"
                "O que deseja fazer?\n[ 1 ] Pagar\n[ 2 ] Parcelar\n[ 3 ] Voltar"
            )
            sessoes_clientes[cpf] = 'fatura_opcoes'
        else:
            resposta_bot = "Não localizei sua fatura."

    elif categoria == 'cartao_limite':
        resposta_bot = "Para a sua segurança, por favor, digite os **4 últimos dígitos** do cartão que você deseja consultar."
        sessoes_clientes[cpf] = 'aguardando_final_cartao'

    elif categoria == 'seguranca_app':
        resposta_bot = resposta_ml

    else:
        resposta_bot = resposta_ml

    crud.inserir_interacao(cpf, mensagem_usuario, resposta_bot)
    
    return jsonify({'resposta': resposta_bot})

if __name__ == '__main__':
    app.run(debug=True)