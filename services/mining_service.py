from crypt import methods
import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.mining import Mining
import time

# TODO:
# 1. Make as worker service

app = Flask(__name__)
worker = Mining()

# endpoint to mine a block
@app.route('/mine/', methods=['GET'])
def mine_block():
    while True:
        res = worker.start()
        work = res[2]
        if work:
            worker.__resolve_conflicts__(curr_node=res[3])
        if res[0] == 'No mining node found.':
            res = worker.__mine_at_trans_node__()
            work = res[2]
            if work:
                worker.__resolve_conflicts__(curr_node=res[3])
        if not work and res[0] == 'Cannot mine block at any node.':
            return jsonify(res[0]), res[1]
        time.sleep(20)
        
@app.route('/register_node/', methods=['POST'])
def register():
    # node_ip = request.environ['REMOTE_ADDR']
    # node_port = request.environ['REMOTE_PORT']
    # address = f'http//{node_ip}:{node_port}'
    values = request.get_json()
    required = ['node']
    if not all(k in values for k in required):
        return jsonify('Missing values'), 400
    if not worker.__worker_registration__(address=values['node']):
        return jsonify('Node regiteration failed.'), 200
    if not worker.__notify_all_nodes__():
        return jsonify('Blockchain registration failed.'), 400
    return jsonify('Node registered.'), 200

if __name__ == '__main__':
    port = 3000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)