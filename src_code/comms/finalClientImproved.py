from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import socket
import time
#import pandas as pd
import os
import csv

HOST = "192.168.43.81" ##o or 172.20.10.4
PORT = 4957
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
bs = 32
raw_key = "1234567890123456"
key = hashlib.sha256(raw_key.encode()).digest()
x = 0
f = open('TestData.txt','r')

def encryptText(plainText, key):
    raw = pad(plainText)
    iv = Random.new().read(AES.block_size) #cryptographically secured keys as opposed to pseudorandome in random class
    cipher = AES.new(key,AES.MODE_CBC,iv)
    return base64.b64encode(iv+cipher.encrypt(raw))

def pad(var1):
    return var1 + (bs - len(var1)%bs)*chr(bs - len(var1)%bs)
# df = pd.read_csv('storageData.csv')

while (x<49):	
	plainText = f.readline()
	var1= str(plainText)
	var1 = var1.strip();
	finalString = encryptText(var1,key)
	x=x+1
	s.send(finalString)
	time.sleep(1)

s.close()


