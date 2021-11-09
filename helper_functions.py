from itertools import product
from pandas import DataFrame
from pandas import Series
from pandas import concat
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Input, concatenate
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Bidirectional as bi
from tensorflow.keras import activations
import numpy as np
from numpy import mean
import pickle
from numpy import std
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os

head_path = r'/content/drive/MyDrive/Final Thesis Fragkozidis Georgios/Training'

#Partitions the input time series in a sliding window format
#i.e. x = [a,b,c,d,...]-> [[a,b], [b,c], [c,d],...] if window size = 2
def sliding_window(data,size): 
    y = np.array([])
    for i in range(len(data) - (size-1)):
        buf_list = []
        buf = [data[i+j] for j in range(size)]
        x = np.array([buf_list])
        y = np.vstack((y, x)) if np.size(y) else x
    return y

# Partition the data so that we have an increasing time series
# without the fold set and validation set inside the training set
# Validation_start indicates where to start the validation set 
# because we need an increasing time subsequence but not including the test step
def get_val_partition(X, y, fold, val):
  
  if fold>val:
    X_train = np.split(X,(val*52,(fold+1)*52))
    y_train = np.split(y,(val*52,(fold+1)*52))
    validation_start = 0
  else:   
    X_train = np.split(X,(fold*52,(val+1)*52))
    y_train = np.split(y,(fold*52,(val+1)*52))
    validation_start = val*52 - (val-fold-1)*52
  
  X_train[1] = X_train[1][52:-52]
  y_train[1] = y_train[1][52:-52]
  X_val = X[validation_start:(val+1)*52]
  y_val = y[validation_start:(val+1)*52]
  
  return X_train, y_train, X_val, y_val


def get_test_partition(X, y, fold):
  
  X_test = X[fold*52:(fold+1)*52]
  y_test = y[fold*52:(fold+1)*52]
  
  X_train = np.split(X,(fold*52,(fold+2)*52))
  y_train = np.split(y,(fold*52,(fold+2)*52))
  X_train[1]=np.array([])
  y_train[1]=np.array([])
  
    
  return X_train, y_train, X_test, y_test


# Create a function for differencing a time series
# i.e. x = [a,b,c,d,...]->[b-a, c-b, d-c,...]
# dataset is a numpy array
def difference(dataset, interval=1):
  diff = np.array([])
  for i in range(interval, len(dataset)):
    value = dataset[i] - dataset[i - interval]
    diff = np.vstack((diff,value)) if np.size(diff) else value
  return diff
 

# invert differenced value
def inverse_difference(history, yhat, interval=1):
  
  return yhat + history[-interval]


def scale(train, test):
  # fit scaler
  scaler = MinMaxScaler(feature_range=(-1, 1))
  scaler = scaler.fit(train)
  # transform train
  train = train.reshape(train.shape[0], train.shape[1])
  train_scaled = scaler.transform(train)
  # transform test
  test = test.reshape(test.shape[0], test.shape[1])
  test_scaled = scaler.transform(test)
  return scaler, train_scaled, test_scaled
 

# inverse scaling for a forecasted value
def invert_scale(scaler, X, yhat):
  new_row = [x for x in X] + [yhat]
  array = numpy.array(new_row)
  array = array.reshape(1, len(array))
  inverted = scaler.inverse_transform(array)
  return inverted[0, -1]


def plot_learning(train,val):
  
  train = np.asarray(train)
  val = np.asarray(val)
  plt.figure(0)
  plt.plot(train)
  plt.plot(val)
  plt.show()
  
#This function plots the predicted cases for the given model and compares them with the true values
def plot_cases(predict,y_test,truth, forecast_horizon,window_size, test_set, directory, model_type):
  
  y_test = np.ravel(y_test[-51:,-1,-1])
  predict = np.ravel(predict[-51:,-1])
  plt.plot(predict)
  plt.plot(y_test)
  plt.title(model_type+' Model Prediction '+ str(forecast_horizon)+' ahead - '+str(2010+test_set))
  plt.ylabel('ILI Cases')
  plt.xlabel('Weeks')
  plt.legend(['Prediction','Truth'], loc='upper center')
  plt.savefig(os.path.join(directory,'Results','Plots', model_type+'_'+str(forecast_horizon)+'_'+str(2010+test_set)))
  plt.show()
  plt.clf()



