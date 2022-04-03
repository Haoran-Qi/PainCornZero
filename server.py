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
        self.app.add_url_rule('/addPeer', 'addPeer',
                              self.addPeer, methods=["POST"])
        self.app.add_url_rule('/broadcastNewBlock', 'broadcastNewBlock',
                              self.broadcastNewBlock, methods=["POST"])

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
        if not self.storage.receiveNewBlock(newBlock):
            return Response("Invalid block", status=400)
        # broadcastNewBlock to peers
        for peerUrl in self.peers:
            try:
                requests.post(peerUrl, data=newBlock)
            except:
                print("peer not reachable " + peerUrl)
        return Response("peer successfully added", status=201, mimetype='application/json')

    def getBalance(self, address):
        pass

    def getPendingTxn(self):
        return Response(json.dumps(self.storage.waitingTransactions), status=200, mimetype='application/json')

    # def getBlocks(self):


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
