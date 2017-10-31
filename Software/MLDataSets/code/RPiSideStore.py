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
		self.idle = None
		self.predictedAction = None
		self.window_size = 150

	def run(self):

		le = self.labelling()
		train_features, train_output = self.setup(le, self.window_size)
		knn = KNeighborsClassifier(n_neighbors=5).fit(train_features, train_output)
		print("setup complete")
		itrans = le.inverse_transform([0,1,2,3,4,5])
		for i in range(len(itrans)):
			if (itrans[i] == "idle"):
				self.idle = i
		self.ml(knn, le)

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
		df = pd.read_csv('traindata.csv', header=None)
		array = df.values
		array_cols = array.shape[1]

		x_data = array[:,0:array_cols-1]
		normalized_X = preprocessing.normalize(x_data)

		y_data = array[:,array_cols-1:array_cols]
		y_rows = y_data.shape[0]
		y_cols = y_data.shape[1]
		y_data = y_data.ravel()
		y_data = le.fit_transform(y_data)

		y_data = y_data.reshape(y_rows, y_cols)
		x = self.overlap_segment(normalized_X, window_size)
		y = self.overlap_segment(y_data, window_size)

		layers = x.shape[0]
		rows = x.shape[1]
		cols = x.shape[2]
		features = []

		for i in range(layers):
			slice_layer = x[i,::]
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
		moves = []
		for i in range(layers):
			slice_layer = y[i,::]
			mode, count = md(slice_layer)
			moves = np.append(moves, [math.floor(mode)])

		df = pd.DataFrame(features)
		df.to_csv("features.csv")

		df = pd.DataFrame(moves)
		df.to_csv("moves.csv")


		return features, moves



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
		df = pd.read_csv('testdata.csv', header=None)
		data = df.values

		
		x = self.data_processing(data, self.window_size)
		#self.currIndex = length
		feature = self.feature_extraction(x)
		pred = knn.predict(feature)
		#print(pred)
		self.actions = self.actions + list(pred)
		self.therealprediction(le)
		if self.predictedAction:
			print(self.predictedAction)
			#dheeraj does something
			self.predictedAction = None
		#threading.Timer(nextTime - time.time(), self.ml(knn, le)).start()


if __name__ == '__main__':
	ml = MachineLearning()
	ml.run()
