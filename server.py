from flask import Flask, jsonify, request

from storage import Storage

class Server:

    def __init__(self, myAddress, peers, storage):
        self.myAddress = myAddress
        self.peers = peers
        self.storage = storage
        self.app = Flask(__name__)
        self.app.add_url_rule('/getPeers', 'getPeers', self.getPeers)
        self.app.add_url_rule('/join', 'join', self.join)



    def run(self):
        [ip, port] = self.myAddress.split(':')
        self.app.run(host=ip, port=port)


    """
    Controllers
    """

    def getPeers(self):
        return jsonify(self.peers)
    
    def addPeer(self, newAddress=None):
        if newAddress is None:
            if request.method != 'POST':
                return False
            newAddress = request.get_json()['newAddress']
        for peerAddress in self.peers:
            if peerAddress == newAddress:
                return False
        self.peers.append(newAddress)

    def join(self):
        self.addPeer()

    def receiveNewBlock(self, newBlock):
        # verify new block
        # update pending pool
        # append blocks array
        pass

    def broadcastNewBlock(self, newBlock):
        # receiveNewBlock
        # broadcastNewBlock to peers
        pass
    
    def getBalance(self, address):
        pass




if __name__ == '__main__':
    myServer = Server("127.0.0.1:3000",["127.0.0.1:3001", "127.0.0.1:3002"], None)
    myServer.run()
