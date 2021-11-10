import pandas as pd
import random
import numpy as np
import os
import matplotlib.pyplot as plt 
import itertools
import random
import unicodedata
import pandas as pd
import math 
import csv
import sys
import tensorflow as tf
import math
import tensorflow.keras
import scipy.stats as stats
import pickle
from datetime import datetime
from collections import Counter
from collections import defaultdict
from tensorflow.keras.layers import Flatten, Input, Dropout, Activation, concatenate, LSTM
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras import backend as K
from tensorflow.keras.models import model_from_json
from tensorflow.keras import backend
from numpy.random import seed
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time as tm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from notify_run import Notify
from statsmodels.tsa.seasonal import  seasonal_decompose 

dataset = r'C:\Users\skote\Desktop\Years'

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open( name + '.pkl', 'rb') as f:
        return pickle.load(f)


def norm(array,min,max):
  norm  = lambda x: 2*(x-min)/(max-min) -1
  vectorized_norm = np.vectorize(norm)
  return vectorized_norm(array) 