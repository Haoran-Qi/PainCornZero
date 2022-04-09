from flask import Flask, jsonify, request, Response
from storage import Storage
import requests
import json


class Server:

    def __init__(self, myAddress, peers):
        self.myAddress = myAddress
        self.peers = peers
        self.storage = Storage()
        self.app = Flask(__name__)
        self.app.add_url_rule('/getPeers', 'getPeers',
                              self.getPeers, methods=["GET"])
        self.app.add_url_rule('/getPendingTxn', 'getPendingTxn',
                              self.getPendingTxn, methods=["GET"])
        self.app.add_url_rule('/getLatestBlock', 'getLatestBlock',
                              self.getLatestBlock, methods=["GET"])
        self.app.add_url_rule('/getFullBlocks', 'getFullBlocks',
                              self.getFullBlocks, methods=["GET"])
        self.app.add_url_rule('/getUtxosForAddress', 'getUtxosForAddress',
                              self.getUtxosForAddress, methods=["GET"])
        self.app.add_url_rule('/getTransactions', 'getTransactions',
                              self.getTransactions, methods=["GET"])
        self.app.add_url_rule('/addPeer', 'addPeer',
                              self.addPeer, methods=["POST"])
        self.app.add_url_rule('/broadcastNewBlock', 'broadcastNewBlock',
                              self.broadcastNewBlock, methods=["POST"])
        self.app.add_url_rule('/receiveNewBlock', 'receiveNewBlock',
                              self.receiveNewBlock, methods=["POST"])
        self.app.add_url_rule('/addWaitingTransaction', 'addWaitingTransaction',
                              self.addWaitingTransaction, methods=["POST"])

    def run(self):
        [ip, port] = self.myAddress.split(':')
        self.app.run(host=ip, port=port)

    """
    Controllers
    """

    def getPeers(self):
        return jsonify(self.peers)

    def addPeer(self):
        newAddress = request.get_json()['newAddress']
        print(newAddress)
        for peerAddress in self.peers:
            if peerAddress == newAddress:
                return Response("peer already exists", status=400, mimetype='application/json')
        self.peers.append(newAddress)
        return Response("peer successfully added", status=201, mimetype='application/json')

    def broadcastNewBlock(self):
        newBlock = request.get_json()['newBlock']
        if not self.storage.addNewBlock(newBlock):
            return Response("Invalid block", status=400)
        # broadcastNewBlock to peers
        for peerUrl in self.peers:
            try:
                requests.post(peerUrl+"/receiveNewBlock", data=newBlock)
            except:
                print("peer not reachable " + peerUrl)
        return Response("peer successfully added and broadcasted", status=201, mimetype='application/json')

    def receiveNewBlock(self):
        newBlock = request.get_json()['newBlock']
        if not self.storage.addNewBlock(newBlock):
            return Response("Invalid block", status=400)
        return Response("peer successfully added", status=201, mimetype='application/json')

    def addWaitingTransaction(self):
        transaction = request.get_json()['transaction']
        if not self.storage.addWaitingTransaction(transaction):
            return Response("Invalid block", status=400)
        return Response("waiting txn successfully added", status=201, mimetype='application/json')

    def getUtxosForAddress(self):
        address = request.args["address"]
        return Response(json.dumps(self.storage.getUtxosForAddress(address)), status=200,  mimetype='application/json')

    def getPendingTxn(self):
        return Response(json.dumps(self.storage.waitingTransactions), status=200, mimetype='application/json')

    def getLatestBlock(self):
        blocks = self.storage.blocks
        latestBlock = blocks[len(blocks) - 1]
        return Response(json.dumps(latestBlock), status=200, mimetype='application/json')

    def getFullBlocks(self):
        blocks = self.storage.blocks
        return Response(json.dumps(blocks), status=200, mimetype='application/json')
        
    def getTransactions(self):
         return Response(json.dumps(self.storage.transactionMap), status=200, mimetype='application/json')


if __name__ == '__main__':
    myServer = Server("127.0.0.1:3000", ["127.0.0.1:3001", "127.0.0.1:3002"])
    myServer.run()
    # myStorage =  Storage()
    # print("states")
    # print(myStorage.states)
    # print("blocks")
    # print(myStorage.blocks)
    # print("transactionMap")
    # print(myStorage.transactionMap)
    # print("my utxos")
    # print(myStorage.getUtxosForAddress("1MMMMSUb1piy2ufrSguNUdFmAcvqrQF8M5"))
