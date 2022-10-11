import time
import requests
from tools.blockchain import Blockchain
from tools.wallet import Wallet
from tools.colors import bcolors
from urllib.parse import urlparse
import pandas as pd
import numpy as np
import os

class TransactChain():
    def __init__(self) -> None:
        self.blockchain = Blockchain()
        self.wallet = Wallet()
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
        self.wallets = self.wallet.__fetch_data__()
        i = 0
        sent_flag = 0
        while i < len(nodes):
            node = nodes[i]
            if self.__validate_wallet__(addr=sender) and self.__validate_wallet__(addr=recipient) and self.__validate_balance__(wallet=sender, sum=amount):
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
                else:
                    if not self.__validate_wallet__(addr=sender):
                        print(f'{bcolors.FAIL}Sender address validation failed.{bcolors.ENDC}')
                    if not self.__validate_wallet__(addr=recipient):
                        print(f'{bcolors.FAIL}Recipient address validation failed.{bcolors.ENDC}')
                    return False
            i += 1
        if sent_flag == 0:
            return False
        return True

    def deposit(self, addr, sum):
        '''
        Function accepts depost and sends it to transaction function.
        Deposit sender is 0 wallet.

        Returns True if make_transaction function was success.
        Returns False if __validate_wallet__ or  make_transaction funcrions were failed.
        '''
        self.wallets = self.wallet.__fetch_data__()
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