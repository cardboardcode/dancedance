from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import socket
import pandas as pd
import os
import csv

HOST = "172.20.10.2"
PORT = 4957
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
bs = 32
raw_key = "1234567890123456"
key = hashlib.sha256(raw_key.encode()).digest()

df = pd.read_csv('storageData.csv')
x=0
while (x<50):
	plainText="#"
	selectedData = df.loc[[x]] #must put in as a list [[]] to get a definite dataframe instead of series. 
	x +=1

	row = next(selectedData.iterrows())[1]
	for y in range(7):
		plainText += str(row[y])	
		plainText +="|"

	var1= plainText
	finalString = encryptText(var1,key)
	s.send(finalString)

s.close()

def encryptText(plainText, key):
    raw = pad(plainText)
    iv = Random.new().read(AES.block_size) #cryptographically secured keys as opposed to pseudorandome in random class
    cipher = AES.new(key,AES.MODE_CBC,iv)
    return base64.b64encode(iv+cipher.encrypt(raw))

def pad(var1):
    return var1 + (bs - len(var1)%bs)*chr(bs - len(var1)%bs)

