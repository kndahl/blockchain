import hashlib as _hashlib
import random
import datetime
from colors import bcolors
import sqlalchemy
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date
import pandas as pd

class Wallet():

    def __init__(self) -> None:
        self.wallet = self.__fetch_data__()

    def create(self, number: str):
        '''
        Creates an uniqe wallet address.
        Before the creation the function checks if addr is unique.

        Returns address if unique and number wasnt register before.
        Return None if number was registered in DataBase.
        '''
        wallets = self.__fetch_data__()
        if self.__number_already_registered__(wallets=wallets, number=number):
            print(f'{bcolors.WARNING}Number already registered in DataBase.{bcolors.ENDC}')
            return None
        else:
            while True:
                self.addr = self.__address_generator__(data=number)
                if not self.__address_is_unique__(wallets=wallets, addr=self.addr):
                    break
            print(f'{bcolors.OKGREEN}Wallet {self.addr} was created.{bcolors.ENDC}')
            return self.addr

    def register_transaction(self, block):
        '''
        Register transactions in DB 
        and push updated account balances
        '''
        self.wallet = self.__fetch_data__()
        for transaction in block:
            sender = transaction['sender']
            recipient = transaction['recipient']
            amount = transaction['amount']
            self.__update_info__(sender=sender, recipient=recipient, amount=amount)
            self.__push_changes__()
        return True

    def __address_is_unique__(self, wallets, addr):
        '''
        Check if addr already exists in DB.

        Returns True if exists.
        Returns False if doesnt exist.
        '''
        return addr in wallets['wallet'].to_list()

    def __address_generator__(self, data):
        '''
        Generate an unique wallet address.
        '''
        hash = _hashlib.sha256(f'{datetime.datetime.now()}{data}{random.randint(0, 999)}'.encode()).hexdigest()
        return f'jadlen{hash}'

    def __push_wallet_to_database__(self, wallet: str, number: str):
        '''
        Push current changes in DataBase.
        '''
        data = {'wallet': [wallet], 'balance': [0], 'number': [number]}
        df = pd.DataFrame(data=data)
        df.to_sql('wallets', self.engine, if_exists='append', index=False)

    def __update_info__(self, sender, recipient, amount):
        '''
        Check recipient and sender balances.
        Updates balances of registered transactions.
        '''
        recip_balance = self.wallet.loc[self.wallet['wallet'] == recipient]['balance']
        sender_balance = self.wallet.loc[self.wallet['wallet'] == sender]['balance']
        self.wallet.loc[self.wallet['wallet'] == recipient, 'balance'] = recip_balance + amount
        self.wallet.loc[self.wallet['wallet'] == sender, 'balance'] = sender_balance - amount
        print(f'{bcolors.OKCYAN}Wallet {recipient} recieved {amount} from wallet {sender}.{bcolors.ENDC}')

    def __fetch_data__(self):
        '''
        Fetching data from DataBase.
        '''
        #self.engine = create_engine('postgresql://eolika:eolika@localhost:5432/blockchain') #--for local
        self.engine = create_engine('postgresql://admin:admin@postgres_container:5432/blockchain') #--for docker
        if not database_exists(self.engine.url):
            print('DataBase doesnt exists. Create...')
            with sqlalchemy.create_engine(
                #'postgresql:///postgres', #--for local
                'postgresql://admin:admin@postgres_container:5432', #--for docker
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

    def __push_changes__(self):
        '''
        Pushing changes in DataBase.
        '''
        self.wallet.to_sql('wallets', self.engine, if_exists='replace', index=False)

    def __number_already_registered__(self, wallets, number):
        '''
        Check if number aleready registered in DB.

        Returns True if exists.
        Returns False if doesnt exist.
        '''
        return number in wallets['number'].to_list()
