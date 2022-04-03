import json

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



for i in range(0, max):
    extract(obj)

