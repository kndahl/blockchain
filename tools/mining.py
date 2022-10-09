import requests
from tools.colors import bcolors

class Mining:
    def __init__(self) -> None:
        self.mining_nodes = ['http://192.168.100.19:8000']
        self.all_nodes = ['http://192.168.100.19:8000', 'http://192.168.100.19:8001']

    def add_mining_node(self, addr):
        pass

    def add_trans_node(self, addr):
        pass

    def start(self):
        current_nodes = self.__get_availables_nodes__(nodes=self.mining_nodes)
        for node in current_nodes:
            node = node.split('http://')[-1]
            res = requests.get('http://127.0.0.1:8000/mine_block/')
            if (res.status_code == 200) or (res.status_code == 400 and res.json() == 'No transactions for mining.'):
                return [res.json(), res.status_code, True, node]
        return ['No mining node found.', 400, False]

    def __get_availables_nodes__(self, nodes):
        available_nodes = []
        for node in nodes:
            node = node.split('http://')[-1]
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                response = requests.get(f'http://{node}/validate/')
                if response.status_code == 200:
                    available_nodes.append(node)
        return available_nodes

    def __resolve_conflicts__(self, curr_node):
        availables_nodes = self.__get_availables_nodes__(nodes=self.all_nodes)
        for node in availables_nodes:
            node = node.split('http://')[-1]
            if node == curr_node:
                pass
            else:
                print(f'{bcolors.UNDERLINE}Check conflict with node {node}.{bcolors.ENDC}')
                node_chain = requests.get(f'http://{node}/chain')
                curr_node_chain = requests.get(f'http://{curr_node}/chain')
                if (curr_node_chain.json() != node_chain.json()):
                    print(f'{bcolors.WARNING}Conflict between {curr_node} and {node}!{bcolors.ENDC}')
                    req = requests.get(f'http://{node}/nodes/resolve/')
                    if req.status_code == 200:
                        print(f'{bcolors.OKCYAN}Conflict between {curr_node} and {node} has been resolved.{bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKBLUE}No conflicts between {curr_node} and {node}.{bcolors.ENDC}')
