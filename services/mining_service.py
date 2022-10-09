import sys
sys.path.append("..")

from flask import Flask, jsonify, request
from tools.mining import Mining
import time

app = Flask(__name__)
worker = Mining()

# endpoint to mine a block
@app.route('/mine/', methods=['GET'])
def mine_block():
    while True:
        res = worker.start()
        worker.__resolve_conflicts__(curr_node=res[3])
        work = res[2]
        if work:
            print(f'Status code: {res[1]}. {res[0]}')
            if res[1] == 400:
                time.sleep(20)
        else:
            return jsonify(res[0]), res[1]

if __name__ == '__main__':
    port = 3000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)