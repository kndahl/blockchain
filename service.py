import json
from flask import Flask, jsonify, request
import blockchain as _blockchain
import clients as _clients
from uuid import uuid4
import sys

app = Flask(__name__)

# Генерируем уникальный на глобальном уровне адрес для этого узла
node_identifier = str(uuid4()).replace('-', '')

blockchain = _blockchain.Blockchain()
generator = _clients.Address()

# endpoint to register the node
@app.route('/nodes/register/', methods=['POST'])
def register_nodes():
    values = request.get_json()
 
    nodes = values.get('nodes')
    if nodes is None:
        return jsonify("Error: Please supply a valid list of nodes"), 400
 
    for node in nodes:
        blockchain.register_node(node)
 
    response = {
        'message': 'New nodes have been added.',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200

# Consensus
@app.route('/nodes/resolve/', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
 
    if replaced:
        response = {
            'message': 'Our chain was replaced.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative.',
            'chain': blockchain.chain
        }
 
    return jsonify(response), 200

# endpoint to create transaction
@app.route('/transactions/new/', methods=['POST'])
def create_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    index = blockchain.transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}.'}
    return jsonify(response), 200

# endpoint to mine a block
@app.route('/mine_block/', methods=['GET'])
def mine_block():
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    if len(blockchain.current_transactions) == 0:
        return jsonify('No transactions for mining.'), 400

    block = blockchain.mine_block()

    response = {
        'message': "New Block Mined",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

# endpoint to return entire blockchain
@app.route('/chain/', methods=['GET'])
def get_blockchain():
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# endpoint to fetch all available nodes
@app.route('/fetch/', methods=['POST'])
def fetch_nodes():
    data = request.get_json()
    if blockchain.__update_chain__(block=data):
        response = {'message': f'All nodes were fetch.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during fetching.'}
        return jsonify(response), 400

# endpoint to send transaction of current node to the mining node
@app.route('/send_transactions/', methods=['POST'])
def send_trans():
    data = request.get_json()
    # if not blockchain.__is_chain_valid__():
    #     return jsonify('The blockchain is invalid.'), 400
    if blockchain.__receive_trans__(trans=data):
        response = {'message': f'All transactions were sent.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during sending transactions.'}
        return jsonify(response), 400

# endpoint to see if blockchain is valid
@app.route('/validate/', methods=['GET'])
def is_valid():
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    else:
        return jsonify('The blockchain is valid.'), 200

@app.route('/new_wallet/', methods=['POST'])
def create_wallet():
    data = request.get_json()
    required = ['number']
    if not all(k in data for k in required):
        return jsonify('Missing values'), 400
    addr = generator.create(number=data)
    return jsonify(addr), 200

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)
