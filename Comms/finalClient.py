from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import socket

HOST = "172.20.10.2"
PORT = 4957
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
var1= "#frontback|10|2|20|300000000000$";
bs = 32
raw_key = "1234567890123456"
key = hashlib.sha256(raw_key.encode()).digest()


def encryptText(plainText, key):
    raw = pad(plainText)
    iv = Random.new().read(AES.block_size) #cryptographically secured keys as opposed to pseudorandome in random class
    cipher = AES.new(key,AES.MODE_CBC,iv)
    return base64.b64encode(iv+cipher.encrypt(raw))

def pad(var1):
    return var1 + (bs - len(var1)%bs)*chr(bs - len(var1)%bs)

finalString = encryptText(var1,key)
print(finalString)
s.send(finalString)