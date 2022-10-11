import datetime as _dt
import hashlib as _hashlib
import json as _json
from urllib.parse import urlparse
import requests
from tools.colors import bcolors
from tools.wallet import Wallet
import time
import datetime

class Blockchain:

    def __init__(self) -> None:
        self.nodes = set()
        self.chain = list()
        self.wallet = Wallet()
        self.current_transactions = []
        genesis_block = self.__create_block__(data='Genesis Block', proof=1, prev_hash=0, index=1)
        self.chain.append(genesis_block)

    def register_node(self, address):
        """
        Register new node
 
        :param address: <str> адрес узла , другими словами: 'http://192.168.0.5:5000'
        :return: None
        """
 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def register_in_worker(self, host):
        try:
            host = f'http://{host}'
            resp = requests.post('http://127.0.0.1:3000/worker/register_node/', json={'node': host})
            print(f'{bcolors.WARNING}{resp.json()}{bcolors.ENDC}')
            if resp.status_code == 200:
                return True
        except Exception as e:
            print(e)
            return False

    def transaction(self, sender, recipient, amount) -> int:
        '''
        Get transaction.

        If array of transactions > 0 -> try to send them to the mining node.

        Returns next block index.
        '''
        data = {
            'amount': amount,
            'recipient': recipient,
            'sender': sender

        }
        self.current_transactions.append(data)
        print(f'{bcolors.HEADER}A new transaction has been added to the queue.{bcolors.ENDC}')
        return self.__get_prev_block__()['index'] + 1

    def mine_block(self) -> dict:
        break_time = 5
        prev_block = self.__get_prev_block__()
        # timer between blocks
        prev_block_time = datetime.datetime.strptime(prev_block['timestamp'],"%Y-%m-%d %H:%M:%S.%f")
        prev_block_timestamp = datetime.datetime.timestamp(prev_block_time)
        current_timestamp = time.time()
        if current_timestamp - prev_block_timestamp < break_time:
            time.sleep(break_time - (current_timestamp - prev_block_timestamp)) # 5 sec
        prev_proof = prev_block['proof']
        index = len(self.chain) + 1
        proof = self.__proof_of_work__(prev_proof, index, self.current_transactions)
        prev_hash = self.__hash__(block=prev_block)
        block = self.__create_block__(
            data=self.current_transactions, proof=proof, 
            prev_hash=prev_hash, 
            index=index)
        self.chain.append(block)
        self.current_transactions = []
        print(f'{bcolors.OKGREEN}Block {index} mined.{bcolors.ENDC}')
        # Notify transaction service
        self.__notify_trans__()
        return block

    def resolve_conflicts(self):
        """
        Это наш алгоритм Консенсуса, он разрешает конфликты, 
        заменяя нашу цепь на самую длинную в цепи
 
        :return: <bool> True, если бы наша цепь была заменена, False, если нет.
        """
 
        neighbours = self.nodes
        print(f'Known hosts: {neighbours}')
        new_chain = None
        # Ищем только цепи, длиннее нашей
        max_length = len(self.chain)
        # Захватываем и проверяем все цепи из всех узлов сети
        for node in neighbours:
            response = requests.get(f'http://{node}/blockchain/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Проверяем, является ли длина самой длинной, а цепь - валидной
                if length > max_length and self.__is_chain_valid__(chain):
                    max_length = length
                    new_chain = chain
        # Заменяем нашу цепь, если найдем другую валидную и более длинную
        if new_chain:
            self.chain = new_chain
            print(f'{bcolors.WARNING}Chain has been repalced.{bcolors.ENDC}')
            return True
        return False


    def __receive_trans__(self, trans):
        for deal in trans:
            self.current_transactions.append(deal)
        if self.__is_chain_valid__(self.chain):
            print(f'{bcolors.BOLD}Node received transaction.{bcolors.ENDC}')
            return True
        else:
            del self.current_transactions[-len(trans)]
            return False

    def __hash__(self, block: dict) -> str:
        enc_block = _json.dumps(block, sort_keys=True).encode()
        return _hashlib.sha256(enc_block).hexdigest()

    def __to_digest__(self, new_proof: int, prev_proof: int, index: str, data: str) -> bytes:
        to_digest = '2011' + str(new_proof ** 2 - prev_proof ** 2 + index) + '11' + str(data) + '13'
        return to_digest.encode()

    def __proof_of_work__(self, prev_proof: str, index: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self.__to_digest__(
                new_proof=new_proof, 
                prev_proof=prev_proof, 
                index=index, 
                data=data)
            hash_val = _hashlib.sha256(to_digest).hexdigest()
            if (hash_val[2:4] == '13') & (hash_val[-4:-2] == '11') & (('j' in hash_val) | ('e' in hash_val)):
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def __get_prev_block__(self) -> dict:
        return self.chain[-1]

    def __create_block__(self, data: str, proof: int, prev_hash: str, index: int) -> dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
            "transactions": data,
            "proof": proof,
            "previous_hash": prev_hash,
        }
        return block
    
    def __is_chain_valid__(self, cons_chain=None) -> bool:
        if cons_chain is None:
            curr_block = self.chain[0]
        else:
            curr_block = cons_chain[0]
        block_index = 1

        while block_index < len(self.chain):
            next_block = self.chain[block_index]
            if next_block['previous_hash'] != self.__hash__(curr_block):
                return False
            curr_proof = curr_block['proof']
            next_index, next_trans, next_proof = (
                                next_block['index'], 
                                next_block['transactions'], 
                                next_block['proof']
                                )
            hash_val = _hashlib.sha256(self.__to_digest__(next_proof, 
                                                        curr_proof, 
                                                        next_index, 
                                                        next_trans)
                                        ).hexdigest()
            if (hash_val[2:4] != '13') & (hash_val[-4:-2] != '11') & (('j' not in hash_val) | ('e' not in hash_val)):
                return False
            
            curr_block = next_block
            block_index += 1
        return True

    def __notify_trans__(self):
        transact_service = 'http://127.0.0.1:7070'
        try:
            requests.get(f'{transact_service}/transaction/block_notice')
        except Exception as e:
            print(e)