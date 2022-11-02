import numbers
import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from wallet import Wallet

app = Flask(__name__)

wallet = Wallet()

# endpoint to create wallet
@app.route('/wallet/new_wallet/', methods=['POST'])
def create_wallet():
    data = request.get_json()
    required = ['number', 'password']
    if not all(k in data for k in required):
        response = {'message': f'Missing value'}
        return jsonify(response), 400
    addr = wallet.create(number=data['number'])
    if addr != None:
        wallet.__push_wallet_to_database__(wallet=addr, number=data['number'], password=data['password'])
        response = {'message': f'Wallet successfully created.', 'addr': addr}
        return jsonify(response), 200
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

# endpoint to check number in DB
@app.route('/wallet/wallet_exist/', methods=['POST'])
def check_number():
    data = request.get_json()
    required = ['number']
    if not all(k in data for k in required):
        response = {'message': f'Missing value'}
        return jsonify(response), 400
    if wallet.check_number(number=data['number']):
        response = {'message': f'Number already exists in DB.'}
        return jsonify(response), 201
    else:
        response = {'message': f'Number doesnt exist in DB.'}
        return jsonify(response), 202

# endpoint to check password for number
@app.route('/wallet/password_check/', methods=['POST'])
def check_password():
    data = request.get_json()
    required = ['number', 'password']
    if not all(k in data for k in required):
        response = {'message': f'Missing value'}
        return jsonify(response), 400
    if wallet.check_password(number=data['number'], password=data['password']):
        response = {'message': f'Key-Lock True.'}
        return jsonify(response), 200
    else:
        response = {'message': f'Key-Lock False.'}
        return jsonify(response), 400 

# endpoint to get current balance
@app.route('/wallet/get_balance/', methods=['POST'])
def get_balance():
    data = request.get_json()
    required = ['number', 'password']
    if not all(k in data for k in required):
        response = {'message': f'Missing value'}
        return jsonify(response), 400
    balance = wallet.get_curr_balance(num=data['number'], pswrd=data['password'])
    if balance == -1941:
        response = {'message': f'Auth error.'}
        return jsonify(response), 400
    else:
        response = {'message': f'Auth ok.', 'balance': balance}
        return jsonify(response), 200

# endpoint to get info of new block mined (fetch)
@app.route('/wallet/wallet_notice/', methods=['GET'])
def notify_wallet():
    wallet.__block_found__()
    return jsonify('The wallet node received a notification.'), 200

if __name__ == '__main__':
    port = 9090
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)