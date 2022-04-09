from cv2 import add
import ecdsa
import hashlib
import struct

import utils
import keyAPI
import binascii

# parse transaction to json
def parseJson(transaction):
    parsed = parseTxn(transaction)
    numOutputs = int(parsed[3][8:10], 16)
    outputs = []
    accIdx = 10
    for i in range(numOutputs):
        value = parsed[3][accIdx:accIdx + 16]
        addressLen = int(parsed[3][accIdx+16:accIdx + 18], 16) * 2
        address = parsed[3][accIdx + 18:accIdx +18+ addressLen ] 
        valueInt = int.from_bytes(binascii.unhexlify(value),"little")
        outputs.append([valueInt, address])
        accIdx = accIdx +18+ addressLen
    return{
        "prevHash": parsed[0][10:74],
        "sourceIdx":  parsed[0][74:],
        "signature": parsed[1],
        "publicKey": parsed[2],
        "output": outputs
    }

# parse transaction information
def parseTxn(txn):
    first = txn[0:41*2]
    scriptLen = int(txn[41*2:42*2], 16)
    script = txn[42*2:42*2+2*scriptLen]
    sigLen = int(script[0:2], 16)
    sig = script[2:2+sigLen*2]
    pubLen = int(script[2+sigLen*2:2+sigLen*2+2], 16)
    pub = script[2+sigLen*2+2:]
            
    assert(len(pub) == pubLen*2)
    rest = txn[42*2+2*scriptLen:]
    return [first, sig, pub, rest]         

# compose signable transaction from parsed transaction
def getSignableTxn(parsed):
    first, sig, pub, rest = parsed
    inputAddr = utils.base58CheckDecode(keyAPI.publicKeyToAddr(pub))
    return first + "1976a914" + inputAddr + "88ac" + rest + "01000000"

# construct raw transaction
def makeRawTransaction(outputTransactionHash, sourceIndex, scriptSig, outputs):
    def makeOutput(data):
        redemptionSatoshis, outputScript = data
        return (binascii.hexlify(struct.pack("<Q", redemptionSatoshis)).decode("utf-8") +
        '%02x' % len(binascii.unhexlify(outputScript)) + outputScript)
    formattedOutputs = ''.join(map(makeOutput, outputs))
    return (
        "01000000" + # 4 bytes version
        "01" + # varint for number of inputs
        binascii.hexlify(binascii.unhexlify(outputTransactionHash)[::-1]).decode('utf-8') + # reverse outputTransactionHash
        binascii.hexlify(struct.pack('<L', sourceIndex)).decode('utf-8') +
        '%02x' % len(binascii.unhexlify(scriptSig)) + scriptSig +
        "ffffffff" + # sequence
        "%02x" % len(outputs) + # number of outputs
        formattedOutputs +
        "00000000" # lockTime
    )

# verify if a transaction is valid
def verifyTxnSignature(txn):                    
    parsed = parseTxn(txn)      
    signableTxn = getSignableTxn(parsed)
    hashToSign = binascii.hexlify(hashlib.sha256(hashlib.sha256(binascii.unhexlify(signableTxn)).digest()).digest())
    assert(parsed[1][-2:] == '01') # hashtype
    sig = utils.derSigToHexSig(parsed[1][:-2])
    public_key = parsed[2]
    vk = ecdsa.VerifyingKey.from_string(binascii.unhexlify(public_key[2:]), curve=ecdsa.SECP256k1)
    assert(vk.verify_digest(binascii.unhexlify(sig), binascii.unhexlify(hashToSign)))


# create a transaction
def makeSignedTransaction(privateKey, outputTransactionHash, sourceIndex, scriptPubKey, outputs):
    myTxn_forSig = (makeRawTransaction(outputTransactionHash, sourceIndex, scriptPubKey, outputs)
         + "01000000") # hash code

    s256 = hashlib.sha256(hashlib.sha256(binascii.unhexlify(myTxn_forSig)).digest()).digest()
    sk = ecdsa.SigningKey.from_string(binascii.unhexlify(privateKey), curve=ecdsa.SECP256k1)
    sig = sk.sign_digest(s256, sigencode=ecdsa.util.sigencode_der) + b'\01' # 01 is hashtype
    pubKey = keyAPI.privateKeyToPublicKey(privateKey)
    scriptSig = (binascii.hexlify(utils.varstr(sig)) + binascii.hexlify(utils.varstr(binascii.unhexlify(pubKey)))).decode('utf8')
    signed_txn = makeRawTransaction(outputTransactionHash, sourceIndex, scriptSig, outputs)
    verifyTxnSignature(signed_txn)
    return signed_txn

#--------------------------------------------------------------------
# Example


# main function
if __name__ == '__main__':

    # receiver
    private_key = 'ed17812c041ba14ba6cc6e3a1d6e6df50129643109dca5c63fb3ba12a95fcfe3'
    wif = keyAPI.privateKeyToWif(private_key)
    public_key = keyAPI.privateKeyToPublicKey(private_key)
    address = keyAPI.publicKeyToAddr(public_key)
    scriptPubKey = keyAPI.addrToScriptPubKey(address)


    # sender
    prevHash = "81b4c832d70cb56ff957589752eb4125a4cab78a25a8fc52d6a09e5bd4404d48"
    senderAddress = "1MMMMSUb1piy2ufrSguNUdFmAcvqrQF8M5"
    senderWif = "5HusYj2b2x4nroApgfvaSfKYZhRbKFH41bVyPooymbC6KfgSXdD"
    senderScriptPubKey = keyAPI.addrToScriptPubKey(senderAddress)
    sprivatekey = keyAPI.wifToPrivateKey(senderWif)
    spublick = keyAPI.privateKeyToPublicKey(sprivatekey)

    # make transaction
    txn = makeSignedTransaction(sprivatekey, prevHash, 0, keyAPI.addrToScriptPubKey(senderAddress), [[50000000, keyAPI.addrToScriptPubKey(address)]])

    # verrify transaction
    verifyTxnSignature(txn)
    print("to receiver")
    print(txn)


    # parse transaction
    parsed = parseJson(txn)
    # print(parsed)
    # print(address)
    # print(keyAPI.scriptPubKeyToAddress(keyAPI.addrToScriptPubKey(address)))


    # txn = makeSignedTransaction(sprivatekey, prevHash, 0, keyAPI.addrToScriptPubKey(senderAddress), [[100000000, keyAPI.addrToScriptPubKey(senderAddress)]])
    # print("to sender")
    # print(txn)