# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 02:38:43 2017

@author: garygjy
"""

import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

def segment_signal(data, window_size):
    N = data.shape[0]
    dim = data.shape[1]
    K = int(N/window_size)
    segments = np.empty((K, window_size, dim))
    for i in range(K):
        segment = data[i*window_size:i*window_size+window_size,:]
        segments[i] = np.vstack(segment)
    return segments

def main():    
    
    le = preprocessing.LabelEncoder()
    le.fit(['busdriver','handwave','windowcleaner','sidestep','jumpingjack','jumping','frontback'])
    list(le.classes_)
    le.transform(['busdriver','handwave','windowcleaner','sidestep','jumpingjack','jumping','frontback'])

    df = pd.read_csv('testdata.csv', header=None)
    array = df.values
    x_data = array[:,0:12]
    normalized_X = preprocessing.normalize(x_data)
    
    y_data = array[:,12:13]
    y_num_rows = y_data.shape[0]
    y_num_columns = y_data.shape[1]
    y_data = le.fit_transform(y_data)
    y_data = y_data.reshape(y_num_rows, y_num_columns)
    x = segment_signal(normalized_X, 5)
    y = segment_signal(y_data, 5)
    
    x_num_layers = x.shape[0]
    x_num_rows = x.shape[1]
    x_num_columns = x.shape[2]
    features = []

    for i in range(x_num_layers):
        slice_layer = x[i,::]
        row = []
        for j in range(x_num_columns):
            temp_layer = slice_layer[:,j]
            std = np.std(temp_layer)
            row = np.append(row, [std])
            mean = np.mean(temp_layer)
            row = np.append(row, [mean])
            median = np.median(temp_layer)
            row = np.append(row, [median])
        features = np.append(features, row)
        
    features = features.reshape((x_num_layers,x_num_columns*3))
    
    y_array =[]
    for i in range(x_num_layers):
        slice_layer = y[i,::]
        row = []
        median = np.median(slice_layer)
        y_array = np.append(y_array, [median])
        
    
    kfold = KFold(n_splits=10, shuffle=True, random_state=8)
    
    fold_index = 0
    with open('metrics.txt', 'w') as outfile:
        for train, test in kfold.split(features):
            knn = KNeighborsClassifier(n_neighbors=5).fit(features[train], y_array[train])
            pred = knn.predict(features[test])
            accuracy = accuracy_score(pred, y_array[test])
            cm = confusion_matrix(y_array[test],pred)
           
            with open('metrics.txt', 'a') as outfile:
                outfile.write("In the %i fold, the classification accuracy is %f\n" %(fold_index, accuracy))
                print('In the %i fold, the classification accuracy is %f' %(fold_index, accuracy))
                outfile.write("And the confusion matrix is: \n")
                print('And the confusion matrix is: ')
                outfile.close()
            with open('metrics.txt', 'ab') as outfile:
                np.savetxt(outfile, cm, fmt='%d')
                print(cm)
                outfile.close()
            fold_index +=1
    outfile.close()
main()