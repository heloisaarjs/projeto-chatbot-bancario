# Simulador de Chatbot Bancário com NLP e Python

Projeto acadêmico de um assistente virtual simulador de serviços bancários. O sistema integra Processamento de Linguagem Natural (NLP) para classificar a intenção das mensagens do usuário e realiza consultas dinâmicas em um banco de dados relacional (SQLite), fornecendo dados financeiros reais da base.

## 🚀 Funcionalidades e Foco Técnico

- **Machine Learning (NLP):** Implementação do algoritmo *Naive Bayes* através da biblioteca Scikit-learn para classificar frases, permitindo que o bot entenda o contexto da solicitação.
- **Modelagem de Banco de Dados:** Estruturação em SQLite para gerenciar clientes, cartões, faturas, transações e o histórico de conversas, evidenciando boas práticas de relacionamento de tabelas.
- **Consultas em Tempo Real:** Respostas dinâmicas construídas a partir de dados lidos do banco, retornando valores exatos de faturas e limites.
- **Lógica de Segurança e Autenticação:**
  - Validação de sessão via CPF.
  - Exigência de confirmação (4 últimos dígitos do cartão) para acessar dados como limite disponível e histórico da última transação.
  - Redirecionamento de solicitações sensíveis (senha, aumento de limite) simulando protocolos de segurança bancária.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Flask
- **Ciência de Dados / ML:** Scikit-learn, Pandas, NumPy
- **Banco de Dados:** SQLite3
- **Frontend:** HTML, CSS, JavaScript

## ⚙️ Como executar o projeto

Para facilitar a avaliação, o banco de dados (`operadora.db`) já está incluso e populado no repositório.

**1. Clone o repositório:**
\`\`\`bash
git clone https://github.com/heloisaarjs/projeto-chatbot-bancario.git
\`\`\`

**2. Instale as dependências:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**3. Inicie o servidor da aplicação:**
\`\`\`bash
python app.py
\`\`\`
Acesse o chat pelo navegador no endereço: `http://127.0.0.1:5000/`

*(Opcional: O arquivo `setup_banco.py` está disponível no repositório para consulta da modelagem das tabelas ou caso seja necessário resetar os dados de teste).*

## 🧪 Dados para Testes de Avaliação

O banco de dados contém diferentes cenários para validação das rotas do chatbot. Utilize os CPFs abaixo (apenas números):

* **João Silva (CPF: `11122233344`):** 
  * Possui 1 cartão ativo e fatura fechada. 
  * *Teste de Segurança:* Solicite "ver minha última transação" e digite os 4 últimos dígitos: **`4321`**.
* **Maria Souza (CPF: `99988877766`):** 
  * Possui 2 cartões (ativo e bloqueado) e fatura aberta. O bot listará o status de ambos.
* **Carlos Oliveira (CPF: `55544433322`):** 
  * Possui cartão em trânsito e fatura vencida.
