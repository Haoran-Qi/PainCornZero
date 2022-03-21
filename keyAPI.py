import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import binascii
import random

import utils

# convert private_key to WIF
def privateKeyToWif(private_key):
    return utils.base58CheckEncode(hex(128), private_key)
# convert  WIF to private_key
def wifToPrivateKey(wif):
    temp = binascii.unhexlify(utils.base58CheckDecode(wif))
    return binascii.hexlify(temp[1:]).decode('ascii')

# convert private key to public key
def privateKeyToPublicKey(private_key):
    sk = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key), curve=ecdsa.SECP256k1)
    hexsk = binascii.hexlify(sk.verifying_key.to_string())
    return (b'04' + hexsk).decode('ascii')

# conver public key to address
def publicKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(binascii.unhexlify(s)).digest())
    return utils.base58CheckEncode("0x00", binascii.hexlify(ripemd160.digest()).decode('utf-8'))

# convert address to script public key
def addrToScriptPubKey(b58str):
    # 76  A9  14 (20 bytes)               88 AC
    return '76a914' + utils.base58CheckDecode(b58str) + '88ac'


#--------------------------------------------------------------------
# Example
print(hex(random.getrandbits(256)))
private_key = 'ed17812c041ba14ba6cc6e3a1d6e6df50129643109dca5c63fb3ba12a95fcfe3'
wif = privateKeyToWif(private_key)
ptest = wifToPrivateKey(wif)
public_key = privateKeyToPublicKey(private_key)
address = publicKeyToAddr(public_key)
scriptPubKey = addrToScriptPubKey(address)
print(scriptPubKey)

