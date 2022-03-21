import ecdsa
import hashlib
import struct

import utils
import keyAPI
import binascii

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

# # receiver
# private_key = 'ed17812c041ba14ba6cc6e3a1d6e6df50129643109dca5c63fb3ba12a95fcfe3'
# wif = keyAPI.privateKeyToWif(private_key)
# public_key = keyAPI.privateKeyToPublicKey(private_key)
# address = keyAPI.publicKeyToAddr(public_key)
# scriptPubKey = keyAPI.addrToScriptPubKey(address)

# # sender
# prevHash = "81b4c832d70cb56ff957589752eb4125a4cab78a25a8fc52d6a09e5bd4404d48"
# senderAddress = "1MMMMSUb1piy2ufrSguNUdFmAcvqrQF8M5"
# senderWif = "5HusYj2b2x4nroApgfvaSfKYZhRbKFH41bVyPooymbC6KfgSXdD"
# senderScriptPubKey = keyAPI.addrToScriptPubKey(senderAddress)
# sprivatekey = keyAPI.wifToPrivateKey(senderWif)
# spublick = keyAPI.privateKeyToPublicKey(sprivatekey)

# tpublic = '14e301b2328f17442c0b8310d787bf3d8a404cfbd0704f135b6ad4b2d3ee751310f981926e53a6e8c39bd7d3fefd576c543cce493cbac06388f2651d1aacbfcd'
# tprivate = '0caecf01d74102a28aed6a64dcf1cf7b0e41c4dd6c62f70f46febdc32514f0bd'

# txn = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
#         "8a47" +
#         "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
#         "41" +
#         "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
#         "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
#         "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

# verifyTxnSignature(txn)
