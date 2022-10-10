import requests
from tools.colors import bcolors

class Mining:
    def __init__(self) -> None:
        self.all_nodes = ['http://192.168.100.19:8000', 'http://192.168.100.19:8001']

    def start(self):
        print(f'{bcolors.WARNING}Trying to connect with mining node.{bcolors.ENDC}')
        self.current_nodes = self.__get_availables_nodes__()
        for node in self.current_nodes:
            node = node.split('http://')[-1]
            port = node.split(':')[-1]
            if port[-1] == '0': # minig node
                try:
                    res = requests.get(f'http://{node}/mine_block/')
                    if (res.status_code == 200) or (res.status_code == 400 and res.json() == 'No transactions for mining.'):
                        return [res.json(), res.status_code, True, node]
                except Exception:
                    return ['No mining node found.', 400, False]
        return ['No nodes were found.', 400, False]

    def __get_availables_nodes__(self):
        available_nodes = []
        for node in self.all_nodes:
            node = node.split('http://')[-1]
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    response = requests.get(f'http://{node}/validate/')
                    if response.status_code == 200:
                        available_nodes.append(node)
                        print(f'{bcolors.OKGREEN}Successfully connected with node {node}.{bcolors.ENDC}')
            except Exception:
                print(f'{bcolors.FAIL}Failed to connect with node {node}.{bcolors.ENDC}')
        return available_nodes

    def __resolve_conflicts__(self, curr_node):
        for node in self.current_nodes:
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

    def __mine_at_trans_node__(self):
        print(f'{bcolors.WARNING}Trying to connect with transaction node.{bcolors.ENDC}')
        self.current_nodes = self.__get_availables_nodes__()
        for node in self.current_nodes:
            node = node.split('http://')[-1]
            try:
                res = requests.get(f'http://{node}/mine_block/')
                if (res.status_code == 200) or (res.status_code == 400 and res.json() == 'No transactions for mining.'):
                    print(f'{bcolors.WARNING}Block will be mine at transaction node.{bcolors.ENDC}')
                    return [res.json(), res.status_code, True, node]
            except Exception as e:
                print(e)
                return ['Cannot mine block at any node.', 400, False]