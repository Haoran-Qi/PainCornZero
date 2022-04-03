import json
import keyAPI
import transactionAPI


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
    def __init__(self, blocks=None):
        self.target = "60235fe120578f43ae80b4ef95101cd5f52d5d988f41419ced1a23d52682c548"
        self.waitingTransactions = []
        self.states = {}  # utxos
        self.transactionMap = {}  # {hash: stateIndex}
        if not blocks or not self.traverseBlocks(blocks):
            f = open('initBlocks.json')
            blocks = json.load(f)
            self.traverseBlocks(blocks)

    def traverseBlocks(self, blocks):
        newStates = {}
        newTransactionMap = {}
        for i in range(len(blocks)):
            block = blocks[i]
            if not self.applyBlockToState(block, blocks, newStates, newTransactionMap):
                return False
        
        # update blocks 
        self.blocks = blocks
        self.states = newStates
        self.transactionMap = newTransactionMap
        return True


    # @sideeffect: update newStates and newTransactionMap
    def applyBlockToState(self, block, blocks, newStates, newTransactionMap):
        preHeaderHash = None
        i = block['header']['height']
        if i > 0:
            preHeader = json.dumps(blocks[i-1]['header'])
            preHeaderHash = keyAPI.stringToHashString(preHeader)
        # verify block
        if not self.verifyBlock(block):
            print("failed to verify block while applyBlockToState "+ str(i))
            return False
        if i>0 and block['preHeaderHash'] != preHeaderHash:
            print("block "+str(i)+ " preHeaderHash mismatch")
            return False
        # update each transaction
        for j in range(len(block["body"]["transactions"])):
            txn = block["body"]["transactions"][j]
            txnHash = keyAPI.transactionHexToHash(txn)
            txnJson = transactionAPI.parseJson(txn)
            newTransactionMap[txnHash] = txnJson
            publicKey = txnJson["publicKey"]
            transactionAPI.verifyTxnSignature(txn)  # make sure the public key, content, and signature match

            # process outputs
            totalOutputAmount = 0
            for [amount, publicScript] in txnJson['output']:
                receiverAddress = keyAPI.scriptPubKeyToAddress(publicScript)
                if receiverAddress not in newStates:
                    newStates[receiverAddress] = []
                newStates[receiverAddress].append({
                    "transactionId": txnHash,
                    "vout": 0,
                    "value" : int(amount),
                    "spent": False
                })
                totalOutputAmount += int(amount)

            # ignore input if genesis block
            if i == 0:
                continue
            # process input
            totalInputAmount = 0
            inputTxnHash = txnJson["prevHash"]
            sourceIndex = int(txnJson["sourceIdx"])   #vout
            # trace back to previous transactions
            if inputTxnHash not in newTransactionMap:
                print("Input transaction not found "+ inputTxnHash + " for block height "+ str(i))
                return False
            inputTxnJson = newTransactionMap[inputTxnHash]
            # get the nth output in one of previous transactions
            [amount, publicScript] = inputTxnJson['output'][sourceIndex]
            receiverAddress = keyAPI.scriptPubKeyToAddress(publicScript)
            if receiverAddress != keyAPI.publicKeyToAddr(publicKey):
                print("Receiver address mismatch")
                return False
            # update state utxo to spent
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
        return True
        
    def verifyBlock(self, block):
        # check markle tree
        txns = block['body']['transactions']
        calculatedRootHash = keyAPI.txnStringsToRootHashString(txns)
        if calculatedRootHash != block['header']['rootHash']:
            print("Markle tree root not match")
            return False
        # check nonce with current target
        target = block['header']['target']
        if self.target != target:
            print("wrong target value")
            return False
        blockHashString = keyAPI.stringToHashString(json.dumps(block))
        if not keyAPI.compareToTarget(blockHashString, target):
            print(blockHashString, target)
            print("hash value not less then target")
            return False
        return True

    def getFullBlocks(self):
        return json.dumps(self.blocks)

    def getUtxosForAddress(self, address):
        if address not in self.states:
            return []
        return json.dumps(self.states[address])


    def addWaitingTransaction(self, transaction):
        self.waitingTransactions.append(transaction)

    def addNewBlock(self, block):
        # verify block
        if not self.verifyBlock(block):
            print("new block not valid")
            return False
        if block["header"]["height"] != len(self.blocks):
            print("new block not on top")
            return False
        # deep clone states
        newStates =  json.loads(json.dumps(self.states))
        # deep clone transactionMap
        newTransactionMap = json.loads(json.dumps(self.transactionMap))
        if not self.applyBlockToState(block, self.blocks, newStates, newTransactionMap):
            return False
        # update real states and blocks
        self.states = newStates
        self.transactionMap = newTransactionMap
        self.blocks.append(block)
        return True
    

    

    