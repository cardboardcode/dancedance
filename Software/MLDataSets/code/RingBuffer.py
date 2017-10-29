import struct
class RingBuffer():
	""" class that implements a not-yet-full buffer """
    	def __init__(self, bufferSize):
        	self.size = bufferSize
       	 	self.buffer = [None]*bufferSize
		self.ackID = 0
		self.full = False
		self.nextID = 0

   	def append(self, x):
                """append an element at the end of the buffer"""
		data = [int(d) for d in struct.unpack("!16B", x)]
#		print(", ".join(str(d) for d in data))
		if self.nextID == data[0]:                                 #keep dropping the packet until the one we want
	 	        if self.ackID == (self.nextID + 1) % self.size:       #buffer full
				self.full = True
				print("buffer full")
	        	else:
				self.buffer[self.nextID] = data
				self.nextID = (self.nextID + 1) % self.size

    	def get(self):
        	""" Return a list of elements from the oldest to the newest. """
		if(self.ackID <= self.nextID):
       			return self.buffer[self.ackID:self.nextID]
		else:
			return self.buffer[self.ackID:self.size] + self.buffer[:self.nextID]

   	def ack(self, index):
		self.ackID = index
		self.full = False

    	def nack(self, index):
		self.ackID = index;
		self.nextID = index;    #discard all of the frame after
		self.full = False

	def getSize(self):
		return self.size

	def isFull(self):
		return self.full
