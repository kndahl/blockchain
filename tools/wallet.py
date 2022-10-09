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
        self.addr = self.__address_generator__(data=number)
        print(f'{bcolors.OKGREEN}Wallet {self.addr} was created.{bcolors.ENDC}')
        return self.addr

    def register_transaction(self, block):
        self.wallet = self.__fetch_data__()
        for transaction in block:
            sender = transaction['sender']
            recipient = transaction['recipient']
            amount = transaction['amount']
            self.__update_info__(sender=sender, recipient=recipient, amount=amount)
            self.__push_changes__()
        return True

    def __register_address__(self):
        pass

    def __address_is_unique__(self):
        pass

    def __address_generator__(self, data):
        hash = _hashlib.sha256(f'{datetime.datetime.now()}{data}{random.randint(0, 999)}'.encode()).hexdigest()
        return f'jadlen{hash}'

    def __push_wallet_to_database__(self, wallet):
        data = {'wallet': [wallet], 'balance': [0]}
        df = pd.DataFrame(data=data)
        df.to_csv('../database/wallets.csv', mode='a', header=False, index=False)

    def __update_info__(self, sender, recipient, amount):
        recip_balance = self.wallet.loc[self.wallet['wallet'] == recipient]['balance']
        sender_balance = self.wallet.loc[self.wallet['wallet'] == sender]['balance']
        self.wallet.loc[self.wallet['wallet'] == recipient, 'balance'] = recip_balance + amount
        self.wallet.loc[self.wallet['wallet'] == sender, 'balance'] = sender_balance - amount
        print(f'{bcolors.OKCYAN}Wallet {recipient} recieved {amount} from wallet {sender}.{bcolors.ENDC}')

    def __fetch_data__(self):
        try:
            wallets = pd.read_csv('../database/wallets.csv')
        except FileNotFoundError:
            data = {'wallet': [0], 'balance': [0]}
            df = pd.DataFrame(data=data)
            df.to_csv('../database/wallets.csv', header=True, index=False)
            wallets = pd.read_csv('../database/wallets.csv')
        return wallets

    def __push_changes__(self):
        self.wallet.to_csv('../database/wallets.csv', header=True, index=False)
