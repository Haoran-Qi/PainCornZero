import json

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
    Output
    {
        transactionIndex: 1,
        target: addressA,
        value : 10,
        spent: false
    }
    """
    def __init__(self, blocks = []):
        self.waitingTransactions = []
        self.states = []
        self.transactionMap = {}  # {hash: stateIndex}
        self.blocks = blocks
        f = open('initBlocks.json')
        blocks = json.load(f)

    def calculateStates(self):
        for block in self.blocks:
            if not self.verifyBlock(block):
                return False
            
        
    def verifyBlock(block):
        return True

    def getFullBlocks(self):
        return json.dumps(self.blocks)


    def addWaitingTransaction(self, transaction):
        self.waitingTransactions.append(transaction)

        

    

    