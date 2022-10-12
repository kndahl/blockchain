from crypt import methods
import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.worker import Mining
import time

app = Flask(__name__)
worker = Mining()

# endpoint to mine a block
@app.route('/worker/mine/', methods=['GET'])
def mine_block():
        worker.start()
        
@app.route('/worker/register_node/', methods=['POST'])
def register():
    values = request.get_json()
    required = ['node']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    if not worker.__worker_registration__(address=values['node']):
        return jsonify('Node regiteration failed.'), 400
    if not worker.__notify_all_nodes__():
        return jsonify('Blockchain registration failed.'), 400
    if not worker.__notify_transact_service__():
        return jsonify('Node registration in transact service failed.'), 400
    return jsonify('Node registered.'), 200

# endpoint to get all registered nodes
@app.route('/worker/get_nodes/', methods=['GET'])
def get_nodes():
    return jsonify(worker.__get_available_nodes__()), 200

if __name__ == '__main__':
    port = 3000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)