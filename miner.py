import json
import requests
import transactionAPI
import keyAPI
import time
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
    selectedTxn = getSelectedTxn(data)
    resp = requests.get("http://localhost:3000/getLatestBlock")
    latestBlock = resp.json()
    print(latestBlock)
    latestBlockHeader = latestBlock['header']
    block = {}
    dic = {}
    dic['preHeaderHash'] = keyAPI.stringToHashString(json.dumps(latestBlockHeader))
    if len(selectedTxn) < 1:
        print("the selected txns are empty")
        return -1
    dic['rootHash'] = keyAPI.txnStringsToRootHashString(selectedTxn)
    dic['target'] = "60235fe120578f43ae80b4ef95101cd5f52d5d988f41419ced1a23d52682c548"
    dic['nonce'] = 0
    dic['height'] = latestBlockHeader['height'] + 1
    dic['time'] =  int(time.time())
    block['header'] = dic
    block['body'] = {
        "transactions":selectedTxn
    }
    max = 300
    for i in range(max):
        block['header']['nonce'] = i
        blockHashString = keyAPI.stringToHashString(json.dumps(block))
        if not keyAPI.compareToTarget(blockHashString, block['header']['target']):
            continue
        else:
            # braodcast to boliu with the this block
            break



        
def getSelectedTxn(data):
    return data[0:3]

getPendingTxn()
    




