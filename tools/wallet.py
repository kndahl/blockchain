import hashlib as _hashlib
import random
import datetime
from tools.colors import bcolors
import pandas as pd
import os

if not os.path.exists('../database'):
    os.makedirs('../database')

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
        df.to_csv('../database/wallets.csv', mode='a', header=False, index=False)

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
        try:
            wallets = pd.read_csv('../database/wallets.csv')
        except FileNotFoundError:
            data = {'wallet': [0], 'balance': [0], 'number': ['None']}
            df = pd.DataFrame(data=data)
            df.to_csv('../database/wallets.csv', header=True, index=False)
            wallets = pd.read_csv('../database/wallets.csv')
        print(f'{bcolors.UNDERLINE}DataBase was fetched.{bcolors.ENDC}')
        return wallets

    def __push_changes__(self):
        '''
        Pushing changes in DataBase.
        '''
        self.wallet.to_csv('../database/wallets.csv', header=True, index=False)

    def __number_already_registered__(self, wallets, number):
        '''
        Check if number aleready registered in DB.

        Returns True if exists.
        Returns False if doesnt exist.
        '''
        return number in wallets['number'].to_list()
