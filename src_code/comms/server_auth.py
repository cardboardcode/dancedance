from Crypto.Cipher import AES
import base64
import sys
import os
import hashlib

class server_auth(object):
    def __init__(self):
        super(server_auth, self).__init__()

    def decryptText(self, cipherText, Key):
        decodedMSG = base64.b64decode(cipherText) #decode message from base64
        iv = decodedMSG[:16] ## first 16 bits are the IV values
        secret_key = hashlib.sha256(Key.encode()).digest(); #the key provided by the receiver will be encoded (not the raw key)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv) #creates a new cipher object
        decryptedText = cipher.decrypt(decodedMSG[16:]).strip() #cipher.decrypt() decrypts data and returns a byte string.
        decryptedTextStr = decryptedText.decode('utf8') # The byte string is decoded to readable unicode characters. 
       # print("This is it: ", not decryptedTextStr[len(decryptedTextStr)-1:].isdigit())
        if (len(decryptedTextStr)%32==0 or not decryptedTextStr[len(decryptedTextStr)-1:].isdigit()):
            print("In condition")
            decryptedTextStr = decryptedTextStr.strip(decryptedTextStr[len(decryptedTextStr)-1:]) ##removes all trailing whitespaces
        print("This is decryptedTextStr: ",decryptedTextStr)
        decryptedTextStr1 = decryptedTextStr[decryptedTextStr.find('#'):] 
        decryptedTextFinal = decryptedTextStr1[1:]#.decode('utf8')
        action = decryptedTextFinal.split('|')[0] ##[0], [1], [2], [3] are there to single out from the array of string returned by the split method.
        voltage = decryptedTextFinal.split('|')[1]
        current = decryptedTextFinal.split('|')[2]
        power = decryptedTextFinal.split('|')[3]
        cumpower = decryptedTextFinal.split('|')[4]
        return {'action': action, 'voltage': voltage, 'current': current, 'power': power, 'cumpower': cumpower}

## Message format: #action | voltage | current | power |cumulativepower|



