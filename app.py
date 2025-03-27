from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

## Função para conectar no banco de dados
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

# Criando tabelas - EXECUTADO APENAS UMA VEZ
def init_db():
    conn = connect_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    fornecedor TEXT NOT NULL,
                    endereco_fornecedor TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    endereco TEXT NOT NULL,
                    preco_unitario REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Rota para adicionar produto
@app.route('/produtos', methods=['POST'])
def add_produto():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Corpo da requisição inválido!'}), 400

        nome = data.get('nome')
        fornecedor = data.get('fornecedor')
        endereco_fornecedor = data.get('endereco_fornecedor')
        quantidade = data.get('quantidade')
        endereco = data.get('endereco')
        preco_unitario = data.get('preco_unitario')

        # Validação básica
        if not all([nome, fornecedor, endereco_fornecedor, quantidade, endereco, preco_unitario]):
            return jsonify({'message': 'Todos os campos são obrigatórios!'}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO produtos (nome, fornecedor, endereco_fornecedor, quantidade, endereco, preco_unitario) VALUES (?, ?, ?, ?, ?, ?)', 
                       (nome, fornecedor, endereco_fornecedor, quantidade, endereco, preco_unitario))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200

    except sqlite3.Error as e:
        return jsonify({'message': f'Erro no banco de dados: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

# Rota para listar todos os produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    try:
        conn = connect_db()
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        conn.close()

        produtos_list = [
            {
                "id": produto["id"],
                "nome": produto["nome"],
                "fornecedor": produto["fornecedor"],
                "endereco_fornecedor": produto["endereco_fornecedor"],
                "quantidade": produto["quantidade"],
                "endereco": produto["endereco"],
                "preco_unitario": produto["preco_unitario"]
            }
            for produto in produtos
        ]
        
        return jsonify(produtos_list), 200

    except sqlite3.Error as e:
        return jsonify({'message': f'Erro no banco de dados: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500
    
# Rota para métodos não implementados em /produtos
@app.route('/produtos', methods=['PUT', 'DELETE', 'PATCH'])
def metodo_nao_implementado():
    return jsonify({'message': f'Método {request.method} não implementado para esta rota!'}), 501
    
# Rota para obter um produto específico pelo ID
@app.route('/produtos/<int:id>', methods=['GET'])
def get_produto(id):
    try:
        conn = connect_db()
        produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
        conn.close()

        if produto is None:
            return jsonify({'message': 'Produto não encontrado!'}), 404

        produto_dict = {
            "id": produto["id"],
            "nome": produto["nome"],
            "fornecedor": produto["fornecedor"],
            "endereco_fornecedor": produto["endereco_fornecedor"],
            "quantidade": produto["quantidade"],
            "endereco": produto["endereco"],
            "preco_unitario": produto["preco_unitario"]
        }
        
        return jsonify(produto_dict), 200

    except sqlite3.Error as e:
        return jsonify({'message': f'Erro no banco de dados: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500
    
# Rota para atualizar um produto pelo ID
@app.route('/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Corpo da requisição inválido!'}), 400

        nome = data.get('nome')
        fornecedor = data.get('fornecedor')
        endereco_fornecedor = data.get('endereco_fornecedor')
        quantidade = data.get('quantidade')
        endereco = data.get('endereco')
        preco_unitario = data.get('preco_unitario')

        # Validação básica
        if not all([nome, fornecedor, endereco_fornecedor, quantidade, endereco, preco_unitario]):
            return jsonify({'message': 'Todos os campos são obrigatórios!'}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
        produto = cursor.fetchone()

        if produto is None:
            conn.close()
            return jsonify({'message': 'Produto não encontrado!'}), 404

        cursor.execute('''UPDATE produtos 
                          SET nome = ?, fornecedor = ?, endereco_fornecedor = ?, quantidade = ?, endereco = ?, preco_unitario = ?
                          WHERE id = ?''', 
                       (nome, fornecedor, endereco_fornecedor, quantidade, endereco, preco_unitario, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Produto atualizado com sucesso!'}), 200

    except sqlite3.Error as e:
        return jsonify({'message': f'Erro no banco de dados: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

# Rota para deletar um produto pelo ID
@app.route('/produtos/<int:id>', methods=['DELETE'])
def delete_produto(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
        produto = cursor.fetchone()

        if produto is None:
            conn.close()
            return jsonify({'message': 'Produto não encontrado!'}), 404

        cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Produto deletado com sucesso!'}), 200

    except sqlite3.Error as e:
        return jsonify({'message': f'Erro no banco de dados: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500
    
# Rota para métodos não implementados em /produtos/<id>
@app.route('/produtos/<int:id>', methods=['POST', 'PATCH'])
def not_implemented_for_resource(id):
    return jsonify({'message': f'Método {request.method} não implementado para esta rota!'}), 501

if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados na primeira execução
    app.run(debug=True)