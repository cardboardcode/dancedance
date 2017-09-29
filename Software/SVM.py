# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 22:16:05 2017

@author: garygjy
"""

import numpy as np
import pandas as pd
import matplotlib as mpl
import tensorflow as tf

from sklearn.svm import SVC

from sklearn import preprocessing
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix

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
    le.fit(['walking', 'sitting', 'jumping'])
    list(le.classes_)
    le.transform(['walking', 'sitting', 'jumping'])

    df = pd.read_csv('acceldata.csv', header=None)
    array = df.values
    x_data = array[:,0:3]
    normalized_X = preprocessing.normalize(x_data)
    y_data = array[:,3:4]
    x = segment_signal(normalized_X, 125)
    y = segment_signal(y_data, 125)
    
    num_layers = x.shape[0]
    num_rows = x.shape[1]
    num_columns = x.shape[2]
    features = []

    for i in range(num_layers):
        slice_layer = x[i,::]
        row = []
        for j in range(num_columns):
            temp_layer = slice_layer[:,j]
            std = np.std(temp_layer)
            row = np.append(row, [std])
            #mean = np.mean(temp_layer)
            #row = np.append(row, [mean])
            #median = np.median(temp_layer)
            #row = np.append(row, [median])
        features = np.append(features, row)
        
    features = features.reshape((num_layers,num_columns))
    
    y_array =[]
    for i in range(num_layers):
        slice_layer = y[i,::]
        row = []
        mean = np.mean(slice_layer)
        y_array = np.append(y_array, [mean])
        
    kfold = KFold(n_splits=10, shuffle=True, random_state=7)
    
    fold_index = 0
    
    for train, test in kfold.split(features):
        svm_model_linear = SVC(kernel = 'linear', C = 1).fit(features[train], y_array[train])
        svm_predictions = svm_model_linear.predict(features[test])
        accuracy = svm_model_linear.score(features[test], y_array[test])
        cm = confusion_matrix(y_array[test],svm_predictions)
        
        print('In the %i fold, the classification accuracy is %f' %(fold_index, accuracy))
        print('And the confusion matrix is: ')
        print(cm)
        fold_index +=1
 
main()