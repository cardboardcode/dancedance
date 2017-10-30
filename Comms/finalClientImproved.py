from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import socket
import time
import sys
#import pandas as pd
import os
import csv

class ClientCommunication:
	def__init__(self,predAction,voltage,current,power,cumpower,host, port):
		self.HOST = host#"172.20.10.2"
		self.PORT = port#4957
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((HOST, PORT))
		self.bs = 32
		self.key = "1234567890123456"
		self.predAction = predAction
		self.voltage = voltage
		self.current = current
		self.power = power
		self.cumpower=cumpower
		self.formattedplaintext = "#"

	def encryptText(self, plainText, key):
	    raw = pad(plainText)
	    iv = Random.new().read(AES.block_size) #cryptographically secured keys as opposed to pseudorandome in random class
	    cipher = AES.new(key,AES.MODE_CBC,iv)
	    return base64.b64encode(iv+cipher.encrypt(raw))

	def pad(self, var1):
	    return var1 + (self.bs - len(var1)%self.bs)*chr(self.bs - len(var1)%self.bs)
# df = pd.read_csv('storageData.csv')

	def formatPlainText(self):
		self.formattedplaintext +=(self.predAction + "|"+self.voltage+"|"+self.current+"|"+self.power+"|"+self.cumpower+"|") 

	def sendData(self, formattedplaintext):
		formatPlainText()
		finalString = encryptText(self.formattedplaintext)
		s.send(finalString)
		time.sleep(1)

		s.close()


