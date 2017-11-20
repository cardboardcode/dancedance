import serial
import RingBuffer as RB
import threading
import time
import sys
import operator

mutex = threading.Lock()

class ReceiveData(threading.Thread):
	def __init__(self, buffer, port, period):
		threading.Thread.__init__(self)
		self.buffer = buffer
		self.port = port
		self.time0 = 
		self.period = period

	def run(self):
		#Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
		while(self.port.in_waiting == 0 or self.port.read() != 'A'):
        		print 'Try to connect to Arduino'
        		self.port.write('H')
        		time.sleep(1)
		self.port.write('A');
		print 'Connected'
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
	def __init__(self, port, buffer, list, _aref, _vref, _cvref, _cdivide,  _RS, period):
		threading.Thread.__init__(self)
		self.port = port
		self.buffer = buffer
		self.bufferSize = buffer.getSize()
		self.list = list
		self._aref = _aref                  #voltage reference for accelo sensor
		self._vref = _vref                  #voltage reference for current sensor
		self._cvref = _cvref                #calibrated voltage reference for voltage sensor
		self._cdivide = _cdivide          #calibrated voltage divide for voltage sensor
		self.RS = _RS
		self._bias = _aref/2.0
		self._mvG = _aref/10.0
		self.period = period

	def run(self):
		self.nextID = 0
		self.storeData()

	def storeData(self):
		nextTime = time.time() + self.period
		mutex.acquire()
		dataList = self.buffer.get()
		mutex.release()
		if dataList:                                   #list is not empty
#			print(", ".join(str(d) for d in dataList))
#			print(len(dataList))
			ack = False
			for data in dataList:
				print(", ".join(str(d) for d in dataList))
				if reduce(operator.xor, data) == 0:                         #pass checksum check
					ack = True                                           #ack current sample
					sample = [(s<<2)*self._cvref/1024.0*self.cdivide for s in data[1:2]] \
							+ [(s<<2)*self._vref/1023.0/(10*self.RS) for s in data[2:3]] \
							+ [(((s<<2) * self._aref / 1024.0 - self._bias) / self._mvG) for s in data[3:-1]]
					print(", ".join(str(d) for d in sample))
                			self.list.append(sample)                                  #store the 12 reading
					self.nextID = (data[0] + 1)%self.bufferSize
               			else:
					ack = False                                                  #some samples has problem
					break
			if ack:
				print('A'+str(self.nextID))
				self.port.write('A')
				self.port.write(chr(self.nextID))
				mutex.acquire()
				self.buffer.ack(self.nextID)
				mutex.release()
			else:
				print('N'+str(self.nextID))
				self.port.write('N')
				self.port.write(chr(self.nextID))
				mutex.acquire()
				self.buffer.nack(self.nextID)
				mutex.release()
		threading.Timer(nextTime - time.time(), self.storeData).start()


class Raspberry():
	def __init__(self):
		self.list = [[]]
		self.buffer = RB.RingBuffer(16)
		self._aref = 3.3
		self._vref = 5.0
		self._RS = 0.1
		self._cvref = 5.015
		self._cdivide = 11.132
		self.threads = []

	def main(self):
		try:
			time0 = int(round(time.time()*1000))

			#set up port connection
			self.port=serial.Serial("/dev/serial0", baudrate=115200)
			self.port.reset_input_buffer()
			self.port.reset_output_buffer()

			#initialize all threads
			commThread = ReceiveData(self.buffer, self.port, 0.1)                           #time to send data should be a bit fast than sample rate
			storageThread = StoreData(self.port, self.buffer, self.list, self._aref, \
					self._vref, self._RS, self._cvref, self._cdivide, 0.5)    #at most comm period * bufferSize

			self.threads.append(commThread)
			self.threads.append(storageThread)

			#start all thread
			for thread in self.threads:
				thread.daemon = True
				thread.start()

			#prevent program exit
			while True:
				time.sleep(1)

        	except KeyboardInterrupt:
			time1 = int(round(time.time()*1000))
			print("time elapsed: " + str(time1-time0))
			for sample in self.list:
				print(", ".join(str(f) for f in sample))
			print len(self.list)
			sys.exit(1)



if __name__ == '__main__':
	pi = Raspberry()
	pi.main()
