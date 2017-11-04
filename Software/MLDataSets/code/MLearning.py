# -*- coding: utf-8 -*-
#"""
#Created on Thu Sep 21 02:38:43 2017
#@author: garygjy
#"""

import numpy as np
import pandas as pd
import math

from scipy.stats import mode as md
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

def fixed_segment(data, window_size):
    N = data.shape[0]
    dim = data.shape[1]
    K = int(N/window_size)
    segments = np.empty((K, window_size, dim))
    for i in range(K):
        segment = data[i*window_size:i*window_size+window_size,:]
        segments[i] = np.vstack(segment)
    return segments

def overlap_segment(data, window_size):
    N = data.shape[0]
    dim = data.shape[1]
    K = int(N/window_size)
    halfwindow = math.ceil(window_size/2.0)
    segments = np.empty((K*2, window_size, dim))
    for i in range(K-1):
        segment = data[i*window_size:i*window_size+window_size,:]
        segments[i*2] = np.vstack(segment)
        segment = data[i*window_size+halfwindow:i*window_size+window_size+halfwindow,:]
        segments[i*2+1] = np.vstack(segment)
    return segments

def labelling():
    le = preprocessing.LabelEncoder()
    le.fit(['busdriver','handwave','windowcleaner','sidestep','jumpingjack','jumping','frontback'])
    le.transform(['busdriver','handwave','windowcleaner','sidestep','jumpingjack','jumping','frontback'])
    return le

def data_processing(le, window_size):
    df = pd.read_csv('testdata.csv', header=None)
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
    #x = fixed_segment(normalized_X, window_size)
    x = overlap_segment(normalized_X, window_size)
    #y = fixed_segment(y_data, window_size)
    y = overlap_segment(y_data, window_size)

    return x,y

def feature_extraction(x_data, y_data, numfeatures):
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
    features = features.reshape(layers, cols*numfeatures)

    moves = []
    for i in range(layers):
        slice_layer = y_data[i,::]
        mode, count = md(slice_layer)
        moves = np.append(moves, [math.floor(mode)])

    df = pd.DataFrame(features)
    df.to_csv("features.csv")
    return features, moves

def cross_validate(features, moves):
    kfold = KFold(n_splits=10, shuffle=True)

    fold_index = 0
    with open('metrics.txt', 'w') as outfile:
        for train, test in kfold.split(features):
            knn = KNeighborsClassifier(n_neighbors=5).fit(features[train], moves[train])
            pred = knn.predict(features[test])
            accuracy = accuracy_score(pred, moves[test])
            cm = confusion_matrix(moves[test],pred)

            with open('metrics.txt', 'a') as outfile:
                outfile.write("In the %i fold, the classification accuracy is %f\n" %(fold_index, accuracy))
                #print('In the %i fold, the classification accuracy is %f' %(fold_index, accuracy))
                outfile.write("And the confusion matrix is: \n")
                #print('And the confusion matrix is: ')
                outfile.close()
            with open('metrics.txt', 'ab') as outfile:
                np.savetxt(outfile, cm, fmt='%d')
                #print(cm)
                outfile.close()
            fold_index +=1
    outfile.close()

def main():
    le = labelling()
    x, y = data_processing(le, 3)
    features, moves = feature_extraction(x, y, 3)
    cross_validate(features, moves)

main()
