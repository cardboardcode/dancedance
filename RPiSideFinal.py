
import serial
import RingBuffer as RB
import threading
import time
import sys
import operator
import csv
import numpy as np
import pandas as pd
import copy
import math
import Queue
from scipy.stats import mode as md
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder


mutex = threading.Lock()
actionLock = threading.Lock()
cumulativePower=0
averageCurrent = 0
averageVoltage= 0

class ModelSetUp():
	def __init__(self):
		pass

	def labelling(self):
		le = preprocessing.LabelEncoder()
		le.fit(['busdriver','frontback','idle','jumping','sidestep','wavehand'])
		print(le.classes_)
		le.transform(['busdriver','frontback','idle','jumping','sidestep','wavehand'])
		print(le.transform(['busdriver','frontback','idle','jumping','sidestep','wavehand']))
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
	def __init__(self, le, knn, list, period,q):
		threading.Thread.__init__(self)
		self.le = le
		self.knn = knn
		self.list = list
		self.period = period
		self.currIndex = 0
		self.actions = []
		self.actionStart = None
		self.actionEnd = None
		self.num = 0
		self.idle = 2
		self.predictedAction = None
		self.window_size = 150
		self.q = q

	def run(self):
		self.ml()

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

	def therealprediction(self):
		window = 4
		if (self.num == 0) and (len(self.actions)>3):
			for i in range(window,len(self.actions)):
				mode, count = md(self.actions[i-window:i])
				if not self.actionStart and (mode != self.idle):
					self.actionStart = i-window
					while (self.actions[self.actionStart] == self.idle):
						self.actionStart += 1
				if self.actionStart and not self.actionEnd and (mode == self.idle):
					self.actionEnd = i-1
					while (self.actions[self.actionEnd] == self.idle):
						self.actionEnd -= 1
				self.num += 1
		elif (len(self.actions)>3):
			for i in range(self.num+window,len(self.actions)):
				mode, count = md(self.actions[i-window:i])
				if not self.actionStart and (mode != self.idle):
					self.actionStart = i-window
					while (self.actions[self.actionStart] == self.idle):
						self.actionStart += 1
				if self.actionStart and not self.actionEnd and (mode == self.idle):
					self.actionEnd = i-1
					while (self.actions[self.actionEnd] == self.idle):
						self.actionEnd -= 1
				self.num += 1

		if self.actionEnd:
			if self.actionEnd - self.actionStart >= 6:
				mode, count = md(self.actions[self.actionStart:self.actionEnd+1])
				self.predictedAction = self.le.inverse_transform([int(mode)])
			self.actions[:] = []
			#self.actions = self.actions[self.actionEnd+1:len(self.actions)]
			self.actionStart = None
			self.actionEnd = None
			self.num = 0

	def ml(self):
		nextTime = time.time() + self.period
		length = len(self.list)
#		print("length: " + str(length))
		data = self.list[self.currIndex:length]
		if(length-self.currIndex >= 150):
			x = self.data_processing(data, 150)
			feature = self.feature_extraction(x)
			pred = self.knn.predict(feature)
			action = self.le.inverse_transform(pred)
			#print(action)
			self.actions = self.actions + list(pred)
			self.therealprediction()
			
			if self.predictedAction:
				self.list[:] = []
				length = 0
				actionLock.acquire()
				self.q.put(str(self.[predictedAction[0]]))
				actionLock.release()
				print(self.predictedAction)
				#dheeraj does something
				self.predictedAction = None
				
		self.currIndex = length
		threading.Timer(nextTime-time.time(), self.ml).start()


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
	def __init__(self, port, buffer, volCurList, list, _aref, _vref, _RS, _cvref, _cdivide, headers, period):
		threading.Thread.__init__(self)
		self.port = port
		self.buffer = buffer
		self.bufferSize = buffer.getSize()
		self.volCurList = volCurList
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

	def run(self):
		self.nextID = 0
		self.beginningTime=time.time()
		self.storeData()

	def storeData(self):
		nextTime = time.time() + self.period
		energy = 0
		timePrev = time.time()
		mutex.acquire()
		dataList = self.buffer.get()
		mutex.release()
		if dataList:                                   #list is not empty
			ack = False
			for data in dataList:
#				print(", ".join(str(d) for d in data))
				if reduce(operator.xor, data) == 0:                         #pass checksum check
					ack = True                                           #ack current sample
					self.volCurList.append([s*self._cvref/1024.0*self._cdivide for s in data[1:2]]\
							+ [s*self._vref/1023.0/(10*self.RS) for s in data[2:3]])
					sample = ([((s<<2) * self._aref / 1024.0 - self._bias) / self._mvG for s in data[3:-1]])
#					print(", ".join("%.2f"%s for s in sample))
					self.list.append(sample)
					averageCurrent = (averageCurrent*(len(self.volCurList)-1) + self.volCurList[len(self.volCurList)-1][1])/len(self.volCurList)
					averageVoltage = (averageVoltage*(len(self.volCurList)-1) + self.volCurList[len(self.volCurList)-1][0])/len(self.volCurList)
					energy = energy + (averageVoltage * averageCurrent)*(time.time()-timePrev)
					timePrev = time.time()
					self.nextID = (data[0] + 1)%self.bufferSize
						else:
					ack = False                                                  #some samples has problem
					break
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
		cumulativePower = (energy + (time.time() - self.beginningTime - self.period) * (cumulativePower))/(time.time() - self.beginningTime)
		threading.Timer(nextTime - time.time(), self.storeData).start()

class ClientCommunication:
	def __init__(self,predAction,voltage,current,power,cumpower,host, port, period):
		threading.Thread.__init__(self)
		self.period = period
		self.HOST = host  #"172.20.10.2"
		self.PORT = int(port)  #4957
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.HOST, self.PORT))
		self.bs = 32
		self.key = "1234567890123456"
		self.predAction = predAction
		self.voltage = voltage
		self.current = current
		self.power = power
		self.cumpower=cumpower
		self.formattedplaintext = "#"

	def encryptText(self, plainText, key):
		raw = self.pad(plainText)
		iv = Random.new().read(AES.block_size)  #cryptographically secured keys as opposed to pseudorandome in random class
		cipher = AES.new(key,AES.MODE_CBC,iv)
		return base64.b64encode(iv+cipher.encrypt(raw))
	def pad(self, var1):
		return var1 + (self.bs - len(var1)%self.bs)*chr(self.bs - len(var1)%self.bs)

	def run(self):
		self.sendData()
	def sendData(self):
		nextTime = time.time() + self.period
		self.formattedplaintext = (self.formattedplaintext+ self.predAction + "|"+self.voltage+"|"+self.current+"|"+self.power+"|"+self.cumpower+"|")
		finalString = self.encryptText(self.formattedplaintext, self.key)
		self.s.send(finalString)
		time.sleep(0.1)
		threading.Timer(nextTime - time.time() - 0.1, self.sendData).start()

class Raspberry():
	def __init__(self):
		#Dheeraj: the self.curVolList store the vol and cur as a 2D array of size of (size*2)
		#	  please use it to compute the power etc. used to send to server
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
		self.currentAction = Queue.Queue(10)
		self.predAction = ''

	def setUpModel(self):
		setUp = ModelSetUp()
		self.le = le =  setUp.labelling()
		train_features, train_output = setUp.setup(le, 150)
		self.knn = KNeighborsClassifier(n_neighbors=5).fit(train_features, train_output)
	def setUpComms(self):
		print ("Please enter the ip address: ")
		self.socket.append(sys.argv[1])
		print ("Please enter the port number: ")
		self.socket.append(sys.argv[2])
	def main(self):
		try:
			self.setUpModel()
			self.setUpComms()
			print("setup complete")

			#set up port connection
			self.port=serial.Serial("/dev/serial0", baudrate=115200)
			self.port.reset_input_buffer()
			self.port.reset_output_buffer()

			#Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
			while(self.port.in_waiting == 0 or self.port.read() != 'A'):
					print 'Try to connect to Arduino'
					self.port.write('H')
					time.sleep(1)
			self.port.write('A');
			print 'Connected'
			self.time0 = int(round(time.time()*1000))

			#initialize all threads
			commThread = ReceiveData(self.buffer, self.port,  0.004)                           #time to send data should be a bit fast than sample rate
			storageThread = StoreData(self.port, self.buffer, self.volCurList, self.list, self._aref, \
						self._vref, self._RS, self._cvref, self._cdivide, self.headers, 0.04)    #at most comm period * bufferSize
			mlThread = MachineLearning(self.le, self.knn, self.list, 5, self.currentAction)
			power = self.volCurList[1] * self.volCurList[0]
			actionLock.acquire()
			self.predAction = self.currentAction.get()
			self.currentAction.task_done()
			actionLock.release()
			clientThread = ClientCommunication(self.predAction, self.volCurList[0], self.volCurList[1], power, cumulativePower,self.socket[0], self.socket[1], 5)
			self.threads.append(commThread)
			self.threads.append(storageThread)
			self.threads.append(mlThread)
			self.threads.append(clientThread)


			#start all thread
			for thread in self.threads:
				thread.daemon = True
				thread.start()

			#prevent program exit
			while True:
				time.sleep(0.001)

			except KeyboardInterrupt:
			time1 = int(round(time.time()*1000))
#			for sample in self.list:
#				print(", ".join("%.2f"%s for s in sample))
			print("time elapsed: " + str(time1-self.time0))
			print("sample size: " + str(len(self.list)))
			sys.exit(1)



if __name__ == '__main__':
	pi = Raspberry()
	pi.main()