from flask import Flask, jsonify

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

    def join(self, newAddress):
        self.peers.append(newAddress)

    def getPeers(self):
        return jsonify(self.peers)


if __name__ == '__main__':
    myServer = Server("127.0.0.1:3000",["127.0.0.1:3001", "127.0.0.1:3002"], None)
    myServer.run()
