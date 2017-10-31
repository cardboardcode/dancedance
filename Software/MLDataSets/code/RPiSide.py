import csv
import numpy as np
import pandas as pd
import math

from scipy.stats import mode as md
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder


class MachineLearning():
	def __init__(self):
		self.currIndex = 0
		self.actions = []
		self.actionStart = None
		self.actionEnd = None
		self.num = 0
		self.idle = 2
		self.predictedAction = None
		self.window_size = 150

	def run(self):

		le = self.labelling()
		train_features, train_output = self.setup(le, self.window_size)
		knn = KNeighborsClassifier(n_neighbors=5).fit(train_features, train_output)
		print("setup complete")
		self.ml(knn, le)

	def overlap_segment(self, data, window_size):
		N = data.shape[0]
		dim = data.shape[1]
		K = int(N/window_size)
		halfwindow = math.ceil(window_size/3.0)
		R = int((N-K*window_size)/halfwindow)
		print(R)
		segments = np.empty((K*3+R-2, window_size, dim))
		for i in range(K):
			segment = data[i*window_size:i*window_size+window_size,:]
			segments[i*3] = np.vstack(segment)
			if (i!=K-1) or R>0:
				segment = data[i*window_size+halfwindow:i*window_size+window_size+halfwindow,:]
				segments[i*3+1] = np.vstack(segment)
			if (i!=K-1) or R>1:
				segment = data[i*window_size+halfwindow*2:i*window_size+window_size+halfwindow*2,:]
				segments[i*3+2] = np.vstack(segment)
		return segments


	def labelling(self):
		le = preprocessing.LabelEncoder()
		le.fit(['busdriver','frontback','idle','jumping','sidestep','wavehand'])
		#print(le.classes_)
		le.transform(['busdriver','frontback','idle','jumping','sidestep','wavehand'])
		#print(le.transform(['busdriver','frontback','idle','jumping','sidestep','wavehand']))
		return le

	def setup(self, le, window_size):
		df = pd.read_csv('features.csv', header=None)
		train_features = df.values
		#print(train_features)
		df = pd.read_csv('moves.csv', header=None)
		train_output = df.values
		#print(train_output)

		return train_features, train_output

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

	def therealprediction(self, le):
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
				if (mode != self.idle):
					self.actionStart = i-window
					while (self.actions[self.actionStart] == self.idle):
						self.actionStart += 1
				if self.actionStart and not self.actionEnd and (mode == self.idle):
					self.actionEnd = i-1
					while (self.actions[self.actionEnd] == self.idle):
						self.actionEnd -= 1
				self.num += 1

		if self.actionEnd:
			mode, count = md(self.actions[self.actionStart:self.actionEnd+1])
			self.predictedAction = le.inverse_transform([int(mode)])
			self.actions = []
			#self.actions = self.actions[self.actionEnd+1:len(self.actions)]
			self.actionStart = None
			self.actionEnd = None
			self.num = 0

	def ml(self, knn, le):
		#nextTime = time.time() + self.period
		#length = len(self.list)
		#data = self.list[self.currIndex:length]
		df = pd.read_csv('testdata2.csv', header=None)
		data = df.values

		
		x = self.data_processing(data, self.window_size)
		#self.currIndex = length
		feature = self.feature_extraction(x)
		pred = knn.predict(feature)
		#print(pred)
		self.actions = self.actions + list(pred)
		print(self.actions)
		print(len(self.actions))
		self.therealprediction(le)
		if self.predictedAction:
			print(self.predictedAction)
			#dheeraj does something
			self.predictedAction = None
		#threading.Timer(nextTime - time.time(), self.ml(knn, le)).start()


if __name__ == '__main__':
	ml = MachineLearning()
	ml.run()
