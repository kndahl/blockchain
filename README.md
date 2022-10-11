# Architecture
![Architecture](docs/scheme.png)

The service consists of the following nodes:
1. Blockchain nodes
2. Transaction node
3. Worker node
4. Wallet node

For the security of the system, it is better to have as many blockchain nodes available as possible.

Transaction node recieves transactions from User and send it at one of available blockchain node.
Blockchain nodes make a connection with Worker, so Worker knows every blockchain node.
As Worker know wach blockchain node, Worker is trying to mine a block in each node every 15 sec.
If a new block has been found, the node that found this block sends information to all other nodes, thereby starting the Consensus algorithm.
New mined block information registering in DB and sends in Wallet.
To avoid double or more spending Transaction Service saves all current deals. Every transaction is validated.
When new block mined Transaction Service overwrite current deals.

# Usage

1. Blockchain nodes must be on ports 8***.
3. Transaction service must be on port 7070.
4. Wallet service must be on port 9090.
5. Mining service better to launch on port 3000.

We always have to register our blockchain node after the launch:
Example:
```python
import requests
req = requests.get('http://127.0.0.1:8000/worker/register')
print(req.status_code)
print(req.json())

req = requests.get('http://127.0.0.1:8001/worker/register')
print(req.status_code)
print(req.json())
```

Thus our nodes became connected.

# Endpoints
## Create wallet [POST]:
```
http://127.0.0.1:9090/wallet/new_wallet/
```
JSON must contains phone number.
```python
json={'number': '89057731311'}
```
## Deposit [POST]:
```
http://127.0.0.1:7070/transaction/deposit/
```
JSON must contains wallet and amount.
```python
json = 
{
    'wallet': 'jadlen0c1a868d87b6d8cf7223f1e8d1b939e3d832a61aab15d0cddaa9b55e30f33e17', 
    'amount': 100
}
```
## Transaction [POST]
```
http://127.0.0.1:7070/transaction/new_transaction/
```
JSON must contains sender, recipient and amount.
```python
json = 
{
    'sender': 'jadlen0c1a868d87b6d8cf7223f1e8d1b939e3d832a61aab15d0cddaa9b55e30f33e17', 
    'recipient': 'jadlen762a33e69f902d887bfb64809d402ed67296876664b3550279e43d35a1ba8358', 
    'amount': 14
}
```
## Chain [GET]
```
http://127.0.0.1:8000/blockchain/chain/ 

or

http://127.0.0.1:8001/blockchain/chain/
```

# TODO
1. Fully node auto-registration.
2. Add certificates support.