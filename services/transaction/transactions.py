import requests
from colors import bcolors
import pandas as pd

class TransactChain():
    def __init__(self) -> None:
        self.nodes = set()
        self.available_nodes = self.__get_available_nodes__()
        self.sent_node = ''
        self.current_transactions = {}

    def make_transaction(self, sender, recipient, amount):
        '''
        The function accepts, validates transactions and sends it to any of the available transaction nodes.

        Returns True if transaction is valid and was successfully sent to mining node.
        Return False if transaction is not valid or sending to mining node was failed.
        '''
        nodes = self.available_nodes
        self.wallets = self.__fetch_data__()
        if not self.__validate_wallet__(addr=sender):
            print(f'{bcolors.FAIL}Sender address validation failed.{bcolors.ENDC}')
            return 401
        if not self.__validate_wallet__(addr=recipient):
            print(f'{bcolors.FAIL}Recipient address validation failed.{bcolors.ENDC}')
            return 402
        if not self.__validate_balance__(wallet=sender, sum=amount):
            print(f'{bcolors.FAIL}Not enough funds.{bcolors.ENDC}')
            return 403
        i = 0
        sent_flag = 0
        while i < len(nodes):
            node = nodes[i]
            try:
                req = requests.post(f'http://{node}/blockchain/transactions/new', json={'sender': sender, 'recipient': recipient, 'amount': amount})
                if req.status_code == 200:
                    sent_flag = 1
                    self.sent_node = node
                    # Temporary wallet info
                    sender_balance = self.wallets.loc[self.wallets['wallet'] == sender]['balance'].values[0]
                    self.current_transactions.update({sender: sender_balance-amount})
                    print(f'{bcolors.OKGREEN}Transaction was successfuly sent to node {node}.{bcolors.ENDC}')
                    print(req.json()['message'])
                    break
            except Exception:
                pass
            i += 1
        if sent_flag == 0:
            return 400
        return 200

    def deposit(self, addr, sum):
        '''
        Function accepts depost and sends it to transaction function.
        Deposit sender is 0 wallet.

        Returns True if make_transaction function was success.
        Returns False if __validate_wallet__ or  make_transaction funcrions were failed.
        '''
        self.wallets = self.__fetch_data__()
        if self.__validate_wallet__(addr=addr):
            if self.make_transaction(sender='0', recipient=addr, amount=sum):
                return True
        else:
            print(f'{bcolors.FAIL}Recipient address validation failed.{bcolors.ENDC}')
        return False

    def __get_available_nodes__(self):
        '''
        Return all available nodes.
        '''
        available_nodes = []
        for node in self.nodes:
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

    def __validate_wallet__(self, addr):
        '''
        Returns True if addr in DataBase.
        Returns False if addr not in DataBase.
        '''
        return addr in self.wallets['wallet'].to_list()

    def __validate_balance__(self, wallet, sum):
        '''
        Balance validation function.
        For 0 address if always valid [needs to be validaed in future as well].
        Also here we validate temporary transactions.
        
        Returns True if wallet balance greater than or equal sum.
        Return False if wallet balance less then sum.
        '''
        if wallet == '0':
            return True
        wallet_balance = self.wallets.loc[self.wallets['wallet'] == wallet]['balance'].values[0]
        if wallet_balance >= sum:
            if wallet in self.current_transactions:
                balance = self.current_transactions[wallet]
                if balance >= sum:
                    return True
            else:
                return True
        else:
            return False

    def __add_node__(self, address):
        try:
            self.nodes.update(address)
            self.available_nodes = self.__get_available_nodes__()
            return True
        except Exception as e:
            print(e)
            return False

    def __block_found__(self):
        '''
        Overwrite transactions history.
        '''
        self.current_transactions = {}
        print(f'{bcolors.OKCYAN}New block was found.{bcolors.ENDC}')

    def __fetch_data__(self):
        '''
        Fetching data from DataBase.
        '''
        import sqlalchemy
        from sqlalchemy_utils import database_exists
        from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date

        #self.engine = create_engine('postgresql://eolika:eolika@localhost:5432/blockchain') #--for local
        self.engine = create_engine('postgresql://admin:admin@postgres_container:5432/blockchain') #--for docker
        if not database_exists(self.engine.url):
            print('DataBase doesnt exists. Create...')
            with sqlalchemy.create_engine(
                'postgresql:///postgres',
                isolation_level='AUTOCOMMIT'
            ).connect() as connection:
                connection.execute('CREATE DATABASE blockchain')
            print('DataBase created!')
            
        print('Successfully connected to DB.')

        inspect = sqlalchemy.inspect(self.engine)
        if not inspect.has_table('wallets'):  # If table don't exist, Create.
            print('Table wallets doesnt exsits. Create...')
            metadata = MetaData(self.engine)
            # Create a table with the appropriate Columns
            Table('wallets', metadata,
                Column('number', String, primary_key=True, nullable=False), 
                Column('wallet', String), 
                Column('balance', Float))
            # Implement the creation
            metadata.create_all()

            # Add default wallet
            data = {'wallet': ['0'], 'balance': [0], 'number': ['0']}
            df = pd.DataFrame(data=data)
            df.to_sql('wallets', self.engine, if_exists='replace', index=False)

        print('Successfully inspected the table!')

        connection = self.engine.connect()
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('wallets', metadata, autoload=True, autoload_with=self.engine)
        query = sqlalchemy.select([table])
        wallets = pd.read_sql_query(query, connection)
        print(wallets)
        return wallets