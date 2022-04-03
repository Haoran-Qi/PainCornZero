import json
import requests
import transactionAPI

example = {
    'header': {
        'preHeaderHash': '0x12ab321d324',
        'rootHash': '0x143f2d23c24',
        'target': "0x000000001",
        'nonce': 777,
        'height': 1,
        'time': 1646089826
    },
    'Body': {
        'transactions': [
            'baseCoin to miner',
            'transaction1',
            'transaction7'
        ]
    }
}

max = 3000

abc = json.dumps(example)
#print(type(abc))
# print(type(json.loads(abc)))

nonce = json.loads(abc)['header']['nonce']
# print(nonce)

# get txn from the waiting pool whose price is the highest
# construct this txn into a new block

# Get request
def getPendingTxn():
    url = "http://localhost:3000/getPendingTxn"
    resp = requests.get(url)
    data = resp.json()
    print(type(data))
    for txn in data:
        txnJson = transactionAPI.parseJson(txn)
        txnOutput = txnJson['output']
    




