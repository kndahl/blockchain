import numbers
import sys
from urllib import response
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.wallet import Wallet

app = Flask(__name__)

wallet = Wallet()

# endpoint to create wallet
@app.route('/wallet/new_wallet/', methods=['POST'])
def create_wallet():
    data = request.get_json()
    required = ['number']
    if not all(k in data for k in required):
        return jsonify('Missing values'), 400
    addr = wallet.create(number=data['number'])
    if addr != None:
        wallet.__push_wallet_to_database__(wallet=addr, number=data['number'])
        return jsonify(addr), 200
    else:
        return jsonify('An error occurred during wallet creation.'), 400

# endpoint to register transactions from the mined block
@app.route('/wallet/register/', methods=['POST'])
def reg_transactions():
    data = request.get_json()
    if wallet.register_transaction(block=data):
        response = {'message': f'Transactions into block were registered.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during transactions registration.'}
        return jsonify(response), 400

if __name__ == '__main__':
    port = 9090
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)