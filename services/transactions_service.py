import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.transactions import TransactChain

app = Flask(__name__)
transact = TransactChain()

# endpoint to create transaction
@app.route('/new_transaction/', methods=['POST'])
def create_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    if transact.make_transaction(sender=values['sender'], recipient=values['recipient'], amount=values['amount']):
        response = {'message': f'Transaction has been send to blockchain.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during sending transactions.'}
        return jsonify(response), 400

# endpoit to deposit account
@app.route('/deposit/', methods=['POST'])
def deposit():
    values = request.get_json()
    required = ['wallet', 'amount']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    if transact.deposit(addr=values['wallet'], sum=values['amount']):
        response = {'message': f'Transaction has been send to blockchain.'}
        return jsonify(response), 200
    else:
        response = {'message': f'An error occurred during sending transactions.'}
        return jsonify(response), 400

if __name__ == '__main__':
    port = 7070
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)