import json
import keyAPI
import transactionAPI
import hashlib


class Storage:
    """
    Transaction
    {
        index: 1,                       # transaction id, added after mining
        input: [
            {
                from: sender address,
                value: 15,
                transactionIndex: 0,     # n-th transaction,  added after minning
                outputIndex: 0,          # n=th transaction's n-th output,  added after minning
            }
        ]
        outputs: [
            {
                target: addressA
                value : 10
            },
            {
                target: addressB,
                value: 5
            }
        ],
        signatures: [
            sender1's signature, sender2's signature, ...
        ]
    }

    """

    """
        Block
        {
            header: {
                preHeaderHash: '0x12ab321d324',
                rootHash: '0x143f2d23c24',
                target: "0x000000001",
                nonce: 777,
                height: 1,
                time: 1646089826
            },
            Body: {
                transactions: [
                    baseCoin to miner,
                    transaction1,
                    ...,
                    transaction7
                ]
            }
        }
    """


    """
    Output States
    { 
        "addressA" : [{
            transactionId: "txn1 hash",
            vout: 0,
            value : 10,
            spent: false
        }]
    }
    """
    def __init__(self, blocks):
        self.waitingTransactions = []
        self.states = []
        self.transactionMap = {}  # {hash: stateIndex}
        if not blocks or not self.traverseBlocks(blocks):
            f = open('initBlocks.json')
            blocks = json.load(f)
            self.traverseBlocks(blocks)

    def calculateStates(self):
        for block in self.blocks:
            if not self.verifyBlock(block):
                return False

    def traverseBlocks(self, blocks):
        newStates = {}
        newTransactionMap = {}
        preHeaderHash = ""
        for i in range(len(blocks)):
            block = blocks[i]
            # verify block
            if not self.verifyBlock(block, i, preHeaderHash):
                return False
            # update each transaction
            for j in range(len(block.body.transactions)):
                txn = block.body.transactions[j]
                txnHash = keyAPI.transactionHexToHash(txn)
                txnJson = transactionAPI.parseJson(txn)
                newTransactionMap[txnHash] = txnJson
                publicKey = txnJson["publicKey"]
                keyAPI.verifyTxnSignature(txn)  # make sure the public key, content, and signature match

                # process outputs
                totalOutputAmount = 0
                for [amount, publicScript] in txnJson['output']:
                    receiverAddress = keyAPI.scriptPubKeyToAddress(publicScript)
                    if not newStates[receiverAddress]:
                        newStates[receiverAddress] = []
                    newStates[receiverAddress].append({
                        "transactionId": txnHash,
                        "vout": 0,
                        "value" : int(amount),
                        "spent": False
                    })
                    totalOutputAmount += int(amount)

                # ignore input if genesis block
                if j == 0:
                    continue
                # process input
                totalInputAmount = 0
                inputTxnHash = txnJson["prevHash"]
                sourceIndex = int(txnJson["sourceIdx"])   #vout
                # trace back to previous transactions
                inputTxnJson = newTransactionMap[inputTxnHash]
                if not inputTxnJson:
                    print("Input transaction not found "+ inputTxnHash + " for block height "+ i)
                    return False
                # get the nth output in one of previous transactions
                [amount, publicScript] = inputTxnJson['output'][sourceIndex]
                receiverAddress = keyAPI.scriptPubKeyToAddress(publicScript)
                if receiverAddress != keyAPI.publicKeyToAddr(publicKey):
                    print("Receiver address mismatch")
                # update state
                for utxo in newStates[receiverAddress]:
                    if utxo["transactionId"] != inputTxnHash or utxo["vout"] != sourceIndex:
                        continue
                    # found the output
                    if utxo["spent"] == True:
                        print("utxo already spent "+ utxo)
                        return False
                    totalInputAmount += utxo["value"]
                    utxo["spent"] = True
                if totalInputAmount != totalOutputAmount:
                    print("total input not equal to output amount "+ inputTxnHash)
                    print("total income "+totalInputAmount)
                    print("total outcome "+totalOutputAmount)
                    print(inputTxnJson)
                    return False
                

                
            header = json.dumps(block.header) 
            preHeaderHash = hashlib.sha256(header)
        # update blocks 
        self.blocks = blocks
        self.states = newStates
        self.transactionMap = newTransactionMap
        return True
            

        
    def verifyBlock(block, index, preHeaderHash):
        return True

    def getFullBlocks(self):
        return json.dumps(self.blocks)


    def addWaitingTransaction(self, transaction):
        self.waitingTransactions.append(transaction)

        

    

    