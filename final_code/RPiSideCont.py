import serial
import RingBuffer as RB
import threading
import time
import sys
import socket
import operator
import csv
from Crypto.Cipher import AES
from Crypto import Random
import base64
import numpy as np
import pandas as pd
import math
from scipy.stats import mode as md
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder


mutex = threading.Lock()

class ModelSetUp():
	def __init__(self):
		pass

	def labelling(self):
		le = preprocessing.LabelEncoder()
		le.fit(['busdriver', 'frontback', 'idle', 'jumping', 'jumpingjack', 'logout', 'sidestep',  \
			'squatturnclap', 'turnclap', 'wavehands', 'windowcleaner360', 'windowcleaning'])
		le.transform(['busdriver', 'frontback', 'idle', 'jumping', 'jumpingjack', 'logout', 'sidestep',  \
			'squatturnclap', 'turnclap', 'wavehands', 'windowcleaner360', 'windowcleaning'])

		return le

	def setup(self, le, window_size):
		df = pd.read_csv('features.csv', header=None)
		train_features = df.values
		#print(train_features)
		df = pd.read_csv('moves.csv', header=None)
		train_output = df.values
		#print(train_output)

		return train_features, train_output

class MachineLearning(threading.Thread):
	def __init__(self, le, knn, list, client, period):
		threading.Thread.__init__(self)
		self.le = le
		self.knn = knn
		self.list = list
		self.client = client
		self.period = period
		self.currIndex = 0
		self.idle = 2
		self.window_size = 150
		self.actionList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.waitingTime = 0.6

	def run(self):
                # wait for 50 seconds for action to show up and then start ml 
	        threading.Timer(50, self.ml).start();

	def overlap_segment(self, data, window_size):
		N = data.shape[0]
		dim = data.shape[1]
		K = int(N/window_size)
		halfwindow = math.ceil(window_size/3.0)
		R = int((N-K*window_size)/halfwindow)
		segments = np.empty((K*3+R-2, window_size, dim))
		for i in range(K):
			segment = data[i*window_size:i*window_size+window_size,:]
			segments[i*3] = np.vstack(segment)
			if (i!=K-1) or R>0:
				segment = data[int(i*window_size+halfwindow):int(i*window_size+window_size+halfwindow),:]
				segments[i*3+1] = np.vstack(segment)
			if (i!=K-1) or R>1:
				segment = data[int(i*window_size+halfwindow*2):int(i*window_size+window_size+halfwindow*2),:]
				segments[i*3+2] = np.vstack(segment)
		return segments


	def data_processing(self, data, window_size):
		## assume list object is called data
		x_data = np.asarray(data)
		normalized_X = preprocessing.normalize(x_data)
		x = self.overlap_segment(normalized_X, window_size)
		return x

	def feature_extraction(self, x_data):
		layers = x_data.shape[0]
		rows = x_data.shape[1]
		cols = x_data.shape[2]
		features = []

		for i in range(layers):
			slice_layer = x_data[i,::]
			row = []
			for j in range(cols):
				temp_layer = slice_layer[:,j]
				std = np.std(temp_layer)
				row = np.append(row, [std])
				mean = np.mean(temp_layer)
				row = np.append(row, [mean])
				median = np.median(temp_layer)
				row = np.append(row, [median])
			features = np.append(features, row)
		features = features.reshape(layers, cols*3)

		#df = pd.DataFrame(features)
		#df.to_csv("features.csv")
		return features

	def ml(self):
		nextTime = time.time() + self.period
		length = len(self.list)
		#print("length: " + str(length))
		data = self.list[self.currIndex:length]
		if(length-self.currIndex >= 150):             #process only when having enough data
			self.currIndex = length
			x = self.data_processing(data, 150)
			feature = self.feature_extraction(x)
			pred = self.knn.predict(feature)
			#print(pred)
			for m in pred[:]:
				mode = int(m)
				if mode != self.idle:
					self.actionList[mode] += 1;
					if(self.actionList[mode] >= 10):
						action = self.le.inverse_transform([mode])
						self.client.sendData(action[0])
						#print("predicted!")
						#print(action[0])
                                                # wait for a few second to filter the first few reading during transition 
						threading.Timer(self.waitingTime, self.restartML).start();
						return

		threading.Timer(nextTime-time.time(), self.ml).start()

	def restartML(self):
		self.currIndex = 0
		self.list[:] = []
		self.actionList[:] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.ml()


class ReceiveData(threading.Thread):
	def __init__(self, buffer, port, period):
		threading.Thread.__init__(self)
		self.buffer = buffer
		self.port = port
		self.period = period

	def run(self):
		self.readData()


	def readData(self):
		#start to receive data from mega
		nextTime = time.time() + self.period
		if not self.buffer.isFull():
			rcv = self.port.read(16)
			mutex.acquire()
			self.buffer.append(rcv)
			mutex.release()
		threading.Timer(nextTime - time.time(), self.readData).start()

class StoreData(threading.Thread):
	def __init__(self, port, buffer, powerList, list, _aref, _vref, _RS, _cvref, _cdivide, headers, period):
		threading.Thread.__init__(self)
		self.port = port
		self.buffer = buffer
		self.bufferSize = buffer.getSize()
		self.powerList = powerList
		self.list = list
		self._aref = _aref            #voltage reference for accelo sensor
		self._bias = _aref/2.0
		self._mvG = _aref/10.0
		self._vref = _vref            #voltage reference for current sensor
		self.RS = _RS                 #shunt resistor value (in ohms)
		self._cvref = _cvref          #calibrated voltage reference for voltage sensor
		self._cdivide = _cdivide      #calibrated voltage divide for voltage sensor
		self.headers = headers
		self.period = period
		self.energy = 0
		self.timePrev = time.time()

	def run(self):
		self.nextID = 0
		self.beginningTime=time.time()
		self.storeData()

	def storeData(self):
		nextTime = time.time() + self.period
		mutex.acquire()
		dataList = self.buffer.get()
		mutex.release()
		if dataList:                                   #list is not empty
			ack = False
			volList = []
			curList = []
			for data in dataList:
#				print(", ".join(str(d) for d in data))
				if reduce(operator.xor, data) == 0:                         #pass checksum check
					ack = True                                           #ack current sample
					volList.append(data[1]*self._cvref/1024.0*self._cdivide)
					curList.append(data[2]*self._vref/1023.0/(10*self.RS))
					sample = ([((s<<2) * self._aref / 1024.0 - self._bias) / self._mvG for s in data[3:-1]])
#					print(", ".join("%.2f"%s for s in sample))
					self.list.append(sample)
					self.nextID = (data[0] + 1)%self.bufferSize
				else:
					ack = False                                                  #some samples has problem
					break
			self.powerList[0] = np.mean(curList)
                        self.powerList[1] = np.mean(volList)
                        self.powerList[2] = self.powerList[0] * self.powerList[1]
                        temp = time.time()
                        self.energy = self.energy + (self.powerList[0] * self.powerList[1])*(temp-self.timePrev)
                        self.timePrev = temp
                        self.powerList[3] = (self.energy/(temp - self.beginningTime))
			if ack:

#				print('A'+str(self.nextID))
				self.port.write('A')
				self.port.write(chr(self.nextID))
				mutex.acquire()
				self.buffer.ack(self.nextID)
				mutex.release()
			else:
#				print('N'+str(self.nextID))
				self.port.write('N')
				self.port.write(chr(self.nextID))
				mutex.acquire()
				self.buffer.nack(self.nextID)
				mutex.release()
		threading.Timer(nextTime - time.time(), self.storeData).start()

class ClientCommunication():
	def __init__(self, powerList, host, port):
		self.HOST = host  #"172.20.10.2"
		self.PORT = int(port)  #4957
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.HOST, self.PORT))
		self.bs = 32
		self.key = "1234567890123456"
		self.powerList = powerList
#		self.voltage = 0 #list[len(list)-1][0]
#		self.current = 0 #list[len(list)-1][1]
#		self.power = 0  #self.voltage*self.current
#		self.cumpower=0 #cumpower

	def encryptText(self, plainText, key):
		raw = self.pad(plainText)
		iv = Random.new().read(AES.block_size)  #cryptographically secured keys as opposed to pseudorandome in random class
		cipher = AES.new(key,AES.MODE_CBC,iv)
		return base64.b64encode(iv+cipher.encrypt(raw))

	def pad(self, var1):
		return var1 + (self.bs - len(var1)%self.bs)*chr(self.bs - len(var1)%self.bs)

	def run(self):
		threading.Timer(60, self.sendData).start()

	def sendData(self, predAction):
	#	print(predAction+" inside comms")
		formattedplaintext = ("#"+ str(predAction) + "|"+str(self.powerList[1])\
			+"|"+str(self.powerList[0])+"|"+str(self.powerList[2])+"|"+str(self.powerList[3])+"|")
		print(formattedplaintext)
		finalString = self.encryptText(formattedplaintext, self.key)
		self.s.send(finalString)

class Raspberry():
	def __init__(self):
		self.volCurList = []
		self.list = []
		self.buffer = RB.RingBuffer(32)
		self._aref = 3.3
		self._vref = 5.0
		self._RS = 0.1
		self._cvref = 5.015
		self._cdivide = 11.132
		self.threads = []
		self.headers = ['  X1  ', '  Y1  ', '  Z1  ', '  X2  ', '  Y2  ', '  Z2  ', '  X3  ', '  Y3  ', '  Z3  ', '  X4  ', '  Y4  ', '  Z4  ']
		self.time0 = 0
		self.socket = []
		self.powerList = [0, 0, 0, 0]

	def setUpModel(self):
		setUp = ModelSetUp()
		self.le = le =  setUp.labelling()
		train_features, train_output = setUp.setup(le, 150)
		self.knn = KNeighborsClassifier(n_neighbors=5).fit(train_features, train_output)

	def setUpComms(self):
	#	print ("Please enter the ip address: ")
		self.socket.append(sys.argv[1])
	#	print ("Please enter the port number: ")
		self.socket.append(sys.argv[2])

	def main(self):
		try:
			self.setUpComms()

			client = ClientCommunication(self.powerList, self.socket[0], self.socket[1])

			self.setUpModel()
			print("setup complete")

			#set up port connection
			self.port=serial.Serial("/dev/serial0", baudrate=115200)
			self.port.reset_input_buffer()
			self.port.reset_output_buffer()

			#Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
			while(self.port.in_waiting == 0 or self.port.read() != 'A'):
					print ('Try to connect to Arduino')
					self.port.write('H')
					time.sleep(1)
			self.port.write('A');
			print 'Connected'

			#initialize all threads
			commThread = ReceiveData(self.buffer, self.port,  0.003)                           #time to send data should be a bit fast than sample rate
			storageThread = StoreData(self.port, self.buffer, self.powerList, self.list, self._aref, \
						self._vref, self._RS, self._cvref, self._cdivide, self.headers, 0.03)    #at most comm period * bufferSize
			mlThread = MachineLearning(self.le, self.knn, self.list, client, 2)

			self.threads.append(commThread)
			self.threads.append(storageThread)
			self.threads.append(mlThread)


			#start all thread
			for thread in self.threads:
				thread.daemon = True
				thread.start()

			#prevent program exit
			while True:
				time.sleep(0.001)

		except KeyboardInterrupt:
			sys.exit(1)



if __name__ == '__main__':
	pi = Raspberry()
	pi.main()