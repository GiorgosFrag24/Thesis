
# Important for generating replicable results across different machines
import unicodedata
import pandas as pd
import math 
import os
import os.path
from os import path
import csv
import collections
import numpy as np
import sys
import tensorflow as tf
import math
import tensorflow.keras
import scipy.stats as stats
import matplotlib.pyplot as plt
import pickle
import itertools
from datetime import datetime
from collections import Counter
from collections import defaultdict
from tensorflow.keras.layers import Flatten,Input,Dropout, Activation,concatenate,LSTM
from tensorflow.keras.models import Model,Sequential,load_model 
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import ModelCheckpoint,EarlyStopping
from tensorflow.keras import backend as K
from tensorflow.keras.models import model_from_json
from tensorflow.keras import backend
from numpy.random import seed
import random
Target_File = 'Sentinel.npy'
# Used for saving to or loading the model from disk
###################################################
###################################################
def load_model( load_path ) : 
    json_file = open( load_path + '_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights( load_path + '_model.h5')
    print('Loaded model from disk')
    return loaded_model
    
def save_model ( model, save_path ) :
    model_json = model.to_json()
    with open( save_path + '_model.json', 'w') as json_file:
        json_file.write( model_json )
    model.save_weights( save_path + '_model.h5' ) # serialize weights to HDF5
 
 
super_mode = '' 
###################################################
###################################################

# Used for saving history object#
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)   
def load_obj(name ):
    with open( name + '.pkl', 'rb') as f:
        return pickle.load(f)
def get_X (year, week, task, input,mode):
    #files = {'meteo':['norm_meteo.npy'],'tweet':['norm_2-specgrams.npy','Decomposed_per_county_users.npy','Decomposed_number_of_tweets_by_county.npy'
    files = {'meteo':['norm_meteo.npy'],'tweet':['norm_2-specgrams.npy','decomposed_per_county_users.pkl.npy','decomposed_SC_health_tokens.pkl.npy','decomposed_number_of_tweets_by_county.npy.npy'],'health':['Sentinel.npy']}#
    #sizes = {'meteo':13*8,'tweet':124+24+13*3+13*3,'health': 1}
    sizes = {'meteo':13*8,'tweet':124+24+13*3+13*3,'health': 1}
    #Training_Directory = r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years'
    Training_Directory = r'C:\Users\skote\Desktop\Years'
    if input == 'tweet':
        window_size = 3
    else:
        window_size = 2 
    x = [] #stores input arrays
    #print('gettingx')
    for i in range(1,window_size+1):    
        buf = []
        if(week-i<=0):
            temp_week = week-i + 52 
            temp_year = year-1 
        else:
            temp_week = week-i  
            temp_year = year
        # if mode == 'Evaluate':
            # print(temp_week)
            # print(temp_year)
            
        for file in files[input]:
            if input=='tweet':
                a = np.load(os.path.join(Training_Directory,str(temp_year),str(temp_week),file),allow_pickle=True).flatten()
                buf = np.append(buf,a) if np.size(buf) else a   
            else:
                buf = np.load(os.path.join(Training_Directory,str(temp_year),str(temp_week),file))
        
        buf = buf.reshape(1,sizes[input])   
        #print(np.shape(buf))
        x = np.vstack((buf,x)) if np.size(x) else buf
    #,np.amin(x),np.amax(x))
    x = x.reshape(1,window_size,sizes[input])   
    return x
    
def get_Y( year, week, week_ahead, task, architecture):
    Training_Directory = r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years'
    
    file2 = 'Sentinel.npy'
    
    if architecture == 'many-to-one':
        
        if (week + week_ahead)>52:
            y = np.load( Training_Directory + "\\" + str(year+1) + "\\" + str(week+week_ahead-52) + "\\" + file2 ).reshape(1,1)
        else :
            y = np.load(Training_Directory + "\\" + str(year)+ "\\" + str(week+week_ahead)+ "\\" + file2).reshape(1,1)
        return y        
    else:
        window_size = 2
        for i in range(0,window_size):
            if i == 0:
                if (week+week_ahead)>52:
                    y = np.load(Training_Directory+"\\"+str(year+1)+"\\"+str(week+week_ahead-52)+"\\"+file)
                elif(week+week_ahead)<=0:
                    y = np.load(Training_Directory+"\\"+str(year-1)+"\\"+str(week+week_ahead+52)+"\\"+file)
                else :
                    y = np.load(Training_Directory+"\\"+str(year)+"\\"+str(week+week_ahead)+"\\"+file)
            else:
                if (week-i+week_ahead)>52:
                    y = np.vstack((y,np.load(Training_Directory+"\\"+str(year+1)+"\\"+str(week-i+week_ahead-52)+"\\"+file)))
                elif(week-i+week_ahead)<=0:
                    y = np.vstack((y,np.load(Training_Directory+"\\"+str(year-1)+"\\"+str(week-i+week_ahead+52)+"\\"+file)))
                else :
                    y = np.vstack((y,np.load(Training_Directory+"\\"+str(year)+"\\"+str(week-i+week_ahead)+"\\"+file)))
        
    y = y.reshape(1,window_size,1)  
    return y    

def load_data(year, week, model, week_ahead, task,mode):
    y = get_Y (year, week, week_ahead, task, 'many-to-one')
    buf = []
    if model == 'MTH':
        for input in ['meteo','tweet','health']:
            x = get_X(year,week,task,input,mode)
            buf.append(x)
        return [buf,y]
    elif model == 'MH':
        for input in ['meteo','health']:
            x = get_X(year,week,task,input)
            buf.append(x)
        return [buf,y]
    elif model == 'TH':
        for input in ['tweet','health']:
            x = get_X(year,week,task,input)
            buf.append(x)
        return [buf,y]
    elif model == 'MT':
        for input in ['meteo','tweet']:
            x = get_X(year,week,task,input,mode)
            buf.append(x)
            #print(len(buf))
        return [buf,y]
    elif model == 'M':
        for input in ['meteo']:
            x = get_X(year,week,task,input,mode)
            buf.append(x)
        return [buf,y]
    elif model == 'T':
        for input in ['tweet']:
            x = get_X(year,week,task,input,mode)
            buf.append(x)
        return [buf,y]
    elif model == 'H':
        for input in ['health']:
            x = get_X(year,week,task,input,mode)
            buf.append(x)       
        return [x,y]

def test_generator(test, mode, model, week_ahead, task):    
    super_mode = mode
    count = 0
    x = np.array([])
    x1 = np.array([])
    x2 = np.array([])
    y = np.array([])
    buf_x1 = np.array([])
    buf_y = np.array([])
    r = list(range(2010,2020))
    w = list(range(1,53))
    random.shuffle(r)
    random.shuffle(w)
    while True:     
        if(mode == 'Evaluate'):
            for year in range(2010,2020):
                if year == test:
                    #print(year)
                    for week in range(1,53):                    
                        x = load_data(year, week, model, week_ahead, task,mode)
                        buf_X = x[0]
                        buf_Y = x[1]
                        x = np.array([])
                        yield buf_X, buf_Y
                else:
                    continue
        else:
            for year in r:
                if( year != test ):
                    for week in w:
                        x = load_data(year, week, model, week_ahead, task,mode)
                        buf_X = x[0]
                        buf_Y =  x[1]
                        # print(f'the x is {buf_X}')
                        # print(f'the y is {buf_Y}')
                        x = np.array([])
                        yield buf_X, buf_Y
 
def train_generator(test, holdout, mode, model, week_ahead, task):
    count = 0
    r = list(range(2010,2020))
    w = list(range(1,53))
    batch_size=1
    # random.shuffle(r)
    # random.shuffle(w)
    while True:
        for year in range(2010,2020):
            if year == holdout:
                continue
            if (mode == 'Evaluate'):
                if year == test:
                    buf_year = year
                else:   
                    continue
            else:
                buf_year = year
            for week in range(1,53):
                x = load_data(buf_year, week, model, week_ahead, task,mode, Window)               
                if count == 0: #Supports batch size
                    buf_X =  x[0]
                    buf_Y =  x[1]
                    count += 1
                else:
                    buf_X = np.vstack((buf_X,x[0]))
                    buf_Y = np.vstack((buf_Y,x[1]))
                    #print('X shape after loading  is %d',np.shape(x[0]))
                    #print('Buf shape after stacking  is %d',np.shape(buf_X))
                    
                    count += 1
                if count == batch_size:
                    count = 0
                    #print(np.shape(buf_X))
                    #buf_X = buf_X.reshape(batch_size, Window, sizes[input])  
                    yield buf_X, buf_Y          
def norm(array,min,max):
    norm  = lambda x: 2*(x-min)/(max-min) -1
    vectorized_norm = np.vectorize(norm)
    return vectorized_norm(array)  


def norm_inplace(array,min,max):
    norm  = lambda x: 2*(x-min)/(max-min) -1
    array = np.vectorize(norm)
    
def wind_norm(array):
    norm  = lambda x: (x/array[0]) - 1
    vectorized_norm = np.vectorize(norm)
    return vectorized_norm(array)          
def normalize_meteo():
    min = 8*[1000]
    max = 8*[0]
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years_3',str(year),str(week))
            try:
                x = np.load(os.path.join(dir1,'final_meteo.npy'))
                for i in range(0,8):                    
                    if np.amax(x[:,i]) > max[i]:
                        max[i] = np.amax(x[:,i])
                    if np.amin(x[:,i]) < min[i]:
                        min[i] = np.amin(x[:,i])    
            except:
                continue
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years_3',str(year),str(week))
            dir3 = os.path.join(r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years',str(year),str(week))
            try:
                x = np.load(os.path.join(dir1,'final_meteo.npy'))
                for i in range(0,8):
                    x[:,i] = norm(x[:,i],min[i],max[i])
                np.save(os.path.join(dir3,'norm_meteo.npy'),x)                       
            except:
                continue            



def normalize_tweet():
    max = 0
    min = 1000
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years',str(year),str(week))
            try:
                x = np.load(os.path.join(dir1,'SC_health_tokens.pkl'),allow_pickle = True)                
                if np.amax(x)>max:
                    max = np.amax(x)
                if x[i]<min[i]:
                    min[i] = x[i]
            except:
                continue
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years',str(year),str(week))
            try:
                x = np.load(os.path.join(dir1,'SC_health_tokens.pkl'),allow_pickle = True)
                for i in range(0,30):
                    if max[i]==min[i]:
                        x[i] = 0
                    else:    
                        x[i] = 2*(x[i]-min[i])/(max[i]-min[i]) -1
                np.save(os.path.join(dir1,'Norm_SC_health_tokens.npy'),x)                       
            except: 
                continue
