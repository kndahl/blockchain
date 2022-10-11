import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.blockchain import Blockchain
from tools.wallet import Wallet
from tools.colors import bcolors
from uuid import uuid4
import requests

app = Flask(__name__)

# Генерируем уникальный на глобальном уровне адрес для этого узла
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()
wallet = Wallet()

# endpoint to register node on worker
@app.route('/blockchain/worker/register/')
def register():
    if not blockchain.register_in_worker(host=request.host):
        response = {'message': 'Node registration failed.'}
        return jsonify(response), 400
    else:
        response = {'message': 'Node was successfully registered.'}
        return jsonify(response), 200

# endpoint to register the node
@app.route('/blockchain/nodes/register/', methods=['POST'])
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
@app.route('/blockchain/nodes/resolve/', methods=['GET'])
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
@app.route('/blockchain/transactions/new/', methods=['POST'])
def create_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    index = blockchain.transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}.'}
    return jsonify(response), 200

# endpoint to mine a block
@app.route('/blockchain/mine_block/', methods=['GET'])
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
    # Send block to register transactions
    resp = requests.post('http://127.0.0.1:9090/wallet/register/', 
        json=block['transactions'])
    msg = resp.json().get('message')
    if resp.status_code == 200:
        print(f'{bcolors.OKCYAN}{msg}{bcolors.ENDC}')
    else:
        print(f'{bcolors.FAIL}{msg}{bcolors.ENDC}')
    return jsonify(response), 200

# endpoint to return entire blockchain
@app.route('/blockchain/chain/', methods=['GET'])
def get_blockchain():
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# endpoint to send transaction of current node to the mining node
@app.route('/blockchain/send_transactions/', methods=['POST'])
def send_trans():
    data = request.get_json()
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    if blockchain.__receive_trans__(trans=data):
        response = {'message': f'All transactions were sent.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during sending transactions.'}
        return jsonify(response), 400

# endpoint to see if blockchain is valid
@app.route('/blockchain/validate/', methods=['GET'])
def is_valid():
    if not blockchain.__is_chain_valid__():
        return jsonify('The blockchain is invalid.'), 400
    else:
        return jsonify('The blockchain is valid.'), 200

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)
