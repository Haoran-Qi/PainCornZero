import json
import keyAPI
import transactionAPI
import requests
from threading import Timer

class Account:
    def __init__(self, privateKey, baseUrl):
        self.baseUrl = baseUrl
        self.privateKey = privateKey
        self.wif = keyAPI.privateKeyToWif(privateKey)
        self.publicKey = keyAPI.privateKeyToPublicKey(privateKey)
        self.address = keyAPI.publicKeyToAddr(self.publicKey)

    # get account address
    def getAddress(self):
        return self.address

    def getUtxosForAddress(self):
        url = self.baseUrl + '/getUtxosForAddress'
        utxos = requests.get(url,params={"address": self.address}).json()
        return utxos

    def getUnspentUtxosForAddress(self):
        utxos = self.getUtxosForAddress()
        unspentUtxos= []
        for utxo in utxos:
            if not utxo['spent']:
                unspentUtxos.append(utxo)
        return unspentUtxos

    # get account's current balance
    def getBalance(self):
        unspentUtxos = self.getUnspentUtxosForAddress()
        balance = 0
        for utxo in unspentUtxos:
            balance += utxo['value']
        return balance

    # send money to toAddress
    def sendTransaction(self, toAddress, amount):
        # pick input from unspent outputs
        utxos = self.getUnspentUtxosForAddress()
        utxoSelected = None
        for utxo in utxos:
            if utxo['value'] >= amount:
                utxoSelected = utxo
        if not utxoSelected:
            return False
        # generate outputs
        change = utxoSelected['value'] - amount
        txn = transactionAPI.makeSignedTransaction(
            self.privateKey, 
            utxoSelected['transactionId'], 
            utxoSelected['vout'], 
            keyAPI.addrToScriptPubKey(self.address), 
            [[amount, keyAPI.addrToScriptPubKey(toAddress)],[change, keyAPI.addrToScriptPubKey(self.address)]])
        # send post request to server

        newTxnJson = transactionAPI.parseJson(txn)
        prevHash = newTxnJson["prevHash"]
        print("txn", txn)
        print("prevHash",prevHash, utxoSelected['transactionId'])
        print("utxoSelected['transactionId']", utxoSelected['transactionId'])

        url = self.baseUrl + "/addWaitingTransaction"
        requests.post(url, json= {"transaction": txn})


        return utxoSelected







if __name__ == '__main__':
    baseUrl = "http://localhost:3000"
    account1 =  Account("ed17812c041ba14ba6cc6e3a1d6e6df50129643109dca5c63fb3ba12a95fcfe3", baseUrl)
    account2 =  Account("0caecf01d74102a28aed6a64dcf1cf7b0e41c4dd6c62f70f46febdc32514f0bd", baseUrl)
    print("balance1",account1.getBalance())
    print("balance2",account2.getBalance())
    account1.sendTransaction(account2.getAddress(), 200)
    

    def pollingBalance():
        global account1, account2
        print("balance1",account1.getBalance())
        print("balance2",account2.getBalance())
        Timer(10.0, pollingBalance).start()
    pollingBalance()


    