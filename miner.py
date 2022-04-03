import json
import requests

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


# Get request
def getPendingTxn(self):
    url = "localhost:3000/getPendingTxn"
    resp = requests.get(url)
    data = resp.json()


