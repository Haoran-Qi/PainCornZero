import hashlib
import re
import struct
import base58check
import binascii
import ecdsa

# counting leading characters
def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count

# refer to this https://en.bitcoin.it/wiki/Base58Check_encoding
def base58CheckEncode(version, payload):
    s = bytes.fromhex(version[2:] + payload)
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = (s + checksum)
    return base58check.b58encode(result).decode('utf-8')

# reverse of the base58CheckEncode
def base58CheckDecode(s):
    s = base58check.b58decode(s)
    chk = s[-4:]
    checksum = hashlib.sha256(hashlib.sha256(s[:-4]).digest()).digest()[0:4]
    assert(chk == checksum)
    return hex(int.from_bytes(s[:-4], byteorder='big'))[2:]


# Returns byte string value, not hex string
def varint(n):
    if n < 0xfd:
        return struct.pack('<B', n)
    elif n < 0xffff:
        return struct.pack('<cH', '\xfd', n)
    elif n < 0xffffffff:
        return struct.pack('<cL', '\xfe', n)
    else:
        return struct.pack('<cQ', '\xff', n)

# Takes and returns byte string value, not hex string
def varstr(s):
    return varint(len(s)) + s

# convert DER signature to hex signature 
def derSigToHexSig(s):
    s, junk = ecdsa.der.remove_sequence(binascii.unhexlify(s))
    if junk != b'':
        print ('JUNK' )
    assert(junk == b'')
    x, s = ecdsa.der.remove_integer(s)
    y, s = ecdsa.der.remove_integer(s)
    return '%064x%064x' % (x, y)