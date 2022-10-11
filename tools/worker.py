import requests
from tools.colors import bcolors
from urllib.parse import urlparse

class Mining:
    def __init__(self) -> None:
        self.all_nodes = set()

    def start(self):
        print(f'{bcolors.WARNING}Trying to connect with mining node.{bcolors.ENDC}')
        self.current_nodes = self.__get_available_nodes__()
        for node in self.current_nodes:
            node = node.split('http://')[-1]
            port = node.split(':')[-1]
            if port[-1] == '0': # minig node
                try:
                    res = requests.get(f'http://{node}/blockchain/mine_block/')
                    if (res.status_code == 200) or (res.status_code == 400 and res.json() == 'No transactions for mining.'):
                        return [res.json(), res.status_code, True, node]
                except Exception:
                    return ['No mining node found.', 400, False]
        return ['No nodes were found.', 400, False]

    def __get_available_nodes__(self):
        available_nodes = []
        for node in self.all_nodes:
            node = node.split('http://')[-1]
            try:
                response = requests.get(f'http://{node}/blockchain/chain')
                if response.status_code == 200:
                    response = requests.get(f'http://{node}/blockchain/validate/')
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
                node_chain = requests.get(f'http://{node}/blockchain/chain')
                curr_node_chain = requests.get(f'http://{curr_node}/blockchain/chain')
                if (curr_node_chain.json() != node_chain.json()):
                    print(f'{bcolors.WARNING}Conflict between {curr_node} and {node}!{bcolors.ENDC}')
                    req = requests.get(f'http://{node}/blockchain/nodes/resolve/')
                    if req.status_code == 200:
                        print(f'{bcolors.OKCYAN}Conflict between {curr_node} and {node} has been resolved.{bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKBLUE}No conflicts between {curr_node} and {node}.{bcolors.ENDC}')

    def __mine_at_trans_node__(self):
        print(f'{bcolors.WARNING}Trying to connect with transaction node.{bcolors.ENDC}')
        self.current_nodes = self.__get_available_nodes__()
        for node in self.current_nodes:
            node = node.split('http://')[-1]
            try:
                res = requests.get(f'http://{node}/blockchain/mine_block/')
                if (res.status_code == 200) or (res.status_code == 400 and res.json() == 'No transactions for mining.'):
                    print(f'{bcolors.WARNING}Block will be mine at transaction node.{bcolors.ENDC}')
                    return [res.json(), res.status_code, True, node]
            except Exception as e:
                print(e)
                return ['Cannot mine block at any node.', 400, False]

    def __worker_registration__(self, address):
        try:
            import requests
            req = requests.get(f'{address}/blockchain/chain')
            if req.status_code == 200:
                parsed_url = urlparse(address)
                self.all_nodes.add(parsed_url.netloc)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def __notify_all_nodes__(self):
        list_hosts = list(self.all_nodes)
        full_named_hosts = [f'http://{host}' for host in list_hosts]
        for host in full_named_hosts:
            try:
                requests.post(f'{host}/blockchain/nodes/register', json={'nodes': full_named_hosts})
                for sub_host in full_named_hosts:
                        requests.get(f'{sub_host}/blockchain/nodes/resolve/')
            except Exception:
                return False
        return True

    def __notify_transact_service__(self):
        try:
            #transact_service = 'http://127.0.0.1:7070'
            req = requests.post(f'http://127.0.0.1:7070/transaction/add_node/', json={'nodes': list(self.all_nodes)})
            if req.status_code == 200:
                return True
        except Exception as e:
            print(e)
            return False
