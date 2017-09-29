import pandas as pd
import os
import csv
import random

class storage(object):
		def __init__(self):
			self.filer = "storageData.csv"
			self.actions = ['busdriver', 'frontback', 'jumping', 'jumpingjack', 'sidestep',
				'squatturnclap', 'turnclap', 'wavehands', 'windowcleaner360',
				'windowcleaning']
			self.columns = ['action','goal', 'correct', 'voltage', 'current', 'power', 'cumpower']
			self.indexList = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]
			self.df = pd.DataFrame(index= self.indexList, columns = self.columns)
			

		def populateFile(self):
			#initialData = pd.DataFrame([[0,'frontback','frontback','true',4, 1.5,6,6]],columns = self.columns)
			##self.df = self.df.append(initialData)
			self.df.loc[0] = ['frontback','frontback','true',4, 1.5,6,6] #this list assignment cannot be done for iat
			if not os.path.isfile(self.filer):
				with open(self.filer, 'w+') as csvfile:
					self.df.to_csv(csvfile)
			for x in range(1, 50):
				with open(self.filer, 'w+') as f:
					actionEntry = random.choice(self.actions)
					goalEntry = random.choice(self.actions)
					correctMovement = (actionEntry==goalEntry)
					voltage = random.uniform(0.0,5.0) 
					current = random.uniform(0.0, 1.5)
					power = current*voltage
					cumpower = self.df.iat[(x-1),6]+power
					entryList = [actionEntry, goalEntry, correctMovement, voltage, current, power, cumpower]
					self.df.loc[x] = entryList
					self.df.to_csv(f)
			print(self.df)

store1 = storage()
store1.populateFile()


	