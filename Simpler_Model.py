import Data_Functions as utils
from pandas import DataFrame
from pandas import Series
from pandas import concat
from pandas import read_csv
from pandas import datetime
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.layers import LSTM
from math import sqrt
import matplotlib
import numpy as np
import os
from numpy import concatenate
#from numpy.lib.stride_tricks import sliding_window_view

head_path = r'C:\Users\skote\Desktop\New Method'
# date-time parsing function for loading the dataset
def sliding_window(data,size):
    y = np.array([])
    for i in range(len(data)-1):
        x = np.array([data[i],data[i+1]])
        y = np.vstack((y,x)) if np.size(y) else x
    return y    
    
def parser(x):
    return datetime.strptime('190'+x, '%Y-%m')
 
# frame a sequence as a supervised learning problem
def timeseries_to_supervised(x, y, lag, data_type):
    shape = {'HEALTH_DATA.npy':(2,1,1),'METEO_DATA.npy':(2,13,8),'TWEET_DATA.npy':(3,226)}    
    
    df1 = DataFrame(x)
    df = DataFrame(y.astype(dtype=np.float))
    columns = [df1.shift(lag) ]#for i in range(1, lag+1)]
    
    print("Shape of columns before windowing is "+str(np.shape(columns)))
    columns = np.array(columns).reshape(521) # 521 because lose one from differencing
    columns = sliding_window(columns[lag:],shape[data_type][0]) # shape is (520,2)
    print("Shape of columns after windowing is "+str(np.shape(columns)))
    
    #print(np.shape(columns))
    copy = np.array([])
    for k in range(0,519-lag):
        flattened = np.vstack((columns[k].ravel(),columns[k+1].ravel())).flatten()
        copy = np.vstack((copy,flattened)) if np.size(copy) else flattened 
    df1 = DataFrame(copy.astype(dtype = np.float))
    
    df = df.shift(-lag)
    
    df.drop(index=0,inplace=True)
    df.drop(df.tail(lag).index,inplace=True)
    
    df.rename(index = lambda s :s-1, inplace=True)
    
    df = concat((df1,df), axis=1)
    
    return df


# create a differenced series
def difference(dataset, interval):
    diff = list()
    print("Shape of samples before differencing is  "+str(np.shape(dataset[0])))
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    print("Shape of samples after differencing is  "+str(np.shape(value)))
    return Series(diff)
 
# invert differenced value
def inverse_difference(history, yhat, interval, year):
    return yhat + history[(year+1)*52-interval]
 
# scale train and test data to [-1, 1]
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
    array = np.array(new_row)
    array = array.reshape(1, len(array))
    inverted = scaler.inverse_transform(array)
    return inverted[0, -1]
 
# fit an LSTM network to training data
def fit_lstm(train, Parameters,forecast_horizon, year, data_type):
    batch_size = 1
    LSTM_Nodes = Parameters['LSTM_Nodes']                 # Number of hidden nodes of LSTM layer
    Weight_Init = Parameters['Weight_Init']               # Weight Initialization Scheme
    Drop_Param = Parameters['Drop_Param'] 
    X, y = train[:, 0:-1], train[:, -1]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    print("Shape of X is "+str(np.shape(X)))
    
    Input_Layer = Input ( batch_input_shape = (batch_size, X.shape[1], X.shape[2]))
    Dropout_Layer_1 = Dropout (Drop_Param[0]) (Input_Layer)
    LSTM_Layer = LSTM (LSTM_Nodes, activation = 'tanh', batch_input_shape=(batch_size, X.shape[1], X.shape[2]), kernel_initializer = Weight_Init) (Dropout_Layer_1)
    Dropout_Layer_2 = Dropout (Drop_Param[1]) (LSTM_Layer)
    Output_Layer = Dense (1, activation = "linear") (Dropout_Layer_2) # Linear activation function due to regression
    model = Model (inputs = Input_Layer, outputs = Output_Layer) 
    # model = Sequential()
    # model.add(Dropout(Drop_Param[0]))
    # model.add(LSTM(LSTM_Nodes, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), kernel_initializer = Weight_Init, stateful=True))
    # model.add(Dropout(Drop_Param[1]))
    # model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam',metrics = ['mse'])
    #model.summary()
    for i in range(50):
        model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0, shuffle=False)
        model.reset_states()
    yhat = model.predict(X,batch_size=1)
    np.save(os.path.join( head_path,'Results','Raw',str(forecast_horizon),str(year), data_type+'_train_predictions_'+'.npy' ), yhat[-52:])
    np.save(os.path.join( head_path,'Results','Raw',str(forecast_horizon),str(year), data_type+'_train_truth_'+'.npy' ), y[-52:])
    return model
 
# make a one-step forecast
def forecast_lstm(model, batch_size, X):
    X = X.reshape(1, 1, len(X) )
    yhat = model.predict(X, batch_size=batch_size)
    return yhat[0,0]
 
# run a repeated experiment
def experiment(repeats, series_x, series_y, updates, parameters, forecast_horizon, data_type):
    # transform data to be stationary
    raw_values_y = series_y
    diff_values_y = difference(raw_values_y, 1)
    raw_values_x = series_x
    print("Shape of whole dataset before differencing is "+str(np.shape(raw_values_x)))
    diff_values_x = difference(raw_values_x, 1)
    
    print("Shape of whole dataset after differencing is "+str(np.shape(diff_values_x)))
    # transform data to be supervised learning
    supervised = timeseries_to_supervised(diff_values_x,diff_values_y, forecast_horizon, data_type)
    supervised_values = supervised.values
    print("Shape of supervised dataset is "+str(np.shape(supervised_values)))
    # split data into train and test-sets
    for year in range(1,10):
        print('Year is '+ str(year))
        train, test = supervised_values[0:(year*52)], supervised_values[year*52:(year+1)*52]
        
        train_scaled, test_scaled = train, test
        # run experiment
        error_scores = list()
        for r in range(repeats):
            # fit the base model
            lstm_model = fit_lstm(train_scaled, parameters,forecast_horizon, year, data_type)
            utils.save_model (lstm_model, os.path.join( head_path,'Models',str(forecast_horizon),str(year), data_type))
            # forecast test dataset
            train_copy = np.copy(train_scaled)
            predictions = list()
            for i in range(len(test_scaled)):
                # update model
                # if i > 0:
                    # update_model(lstm_model, train_copy, 1, updates)
                # predict
                X, y = test_scaled[i, 0:-1], test_scaled[i, -1] 
                yhat = forecast_lstm(lstm_model, 1, X)
                yhat = inverse_difference(raw_values_y, yhat, len(test_scaled)-i-forecast_horizon, year)
                # store forecast
                predictions.append(yhat)
                # add to training set
                train_copy = concatenate((train_copy, test_scaled[i,:].reshape(1, -1)))
            # report performance
            np.save(os.path.join( head_path,'Results','Raw',str(forecast_horizon),str(year), data_type+'_predictions_'+'.npy' ), predictions)
            rmse = sqrt(mean_squared_error(raw_values_y[year*52+forecast_horizon:(year+1)*52+forecast_horizon], predictions))
            print('%d) Test RMSE: %.3f' % (r+1, rmse))
            error_scores.append(rmse)
    return error_scores
 
 
def update_model(model, train, batch_size, updates):
    X, y = train[:, 0:-1], train[:, -1]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    for i in range(updates):
        model.fit(X, y, epochs=1, batch_size=batch_size, verbose=1, shuffle=False)
        model.reset_states()
 
# execute the experiment
def run():
    # load dataset
    Model_Parameters = {'METEO_DATA.npy': { 'Window' : 2, 'Data_Dim' : 13*8 , 'LSTM_Nodes' : 40, 'Activation_Function' : 'tanh', 'Weight_Init' : 'glorot_normal', 'Drop_Param' : [0,0.3] },\
                    'TWEET_DATA.npy': { 'Window' : 3, 'Data_Dim' : 124+24+13*3+13*3 , 'LSTM_Nodes' : 16, 'Activation_Function' : 'tanh', 'Weight_Init' : 'glorot_normal', 'Drop_Param' : [0.2,0] },\
                    'HEALTH_DATA.npy' : {'Window' : 2, 'Data_Dim' : 1 , 'LSTM_Nodes' : 8, 'Activation_Function' :  'tanh', 'Weight_Init' :'glorot_normal', 'Drop_Param' : [0,0] }}
    series_y = np.load(r'C:\Users\skote\Desktop\Years\HEALTH_DATA.npy') #read_csv('shampoo-sales.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
    for data_type in ['METEO_DATA.npy']:
        print('Starting with data '+ data_type)
        series_x = np.load(os.path.join(r'C:\Users\skote\Desktop\Years',data_type))
        print("Shape of whole dataset is "+str(np.shape(series_x)))
        parameters = Model_Parameters[data_type]
        for forecast_horizon in range(3,4):
            print('Forecasting week '+ str(forecast_horizon))
            # experiment
            repeats = 1
            results = DataFrame()
            # run experiment\
            updates = 2
            results['results'] = experiment(repeats, series_x, series_y, updates, parameters, forecast_horizon, data_type)
            # summarize results
            print(results.describe())
            # save results
            results.to_csv('experiment_fixed.csv', index=False)

def f(x):
    # return math.sqrt(x)
    return ((x + 1)*3212)/2 + 2
def array_map(x):
    return np.array(list(map(f, x)))    
    
def plot_cases():
    for week in [1,2,3]:
        for year in range(1,9):
            for data_type in ['METEO_DATA.npy','HEALTH_DATA.npy']:#,'TWEET_DATA.npy']:
                result_path  = os.path.join(r'C:\Users\skote\Desktop\New Method',data_type+'_predictions_'+str(week)+'_'+str(year)+'.npy')
                y = np.load(r'C:\Users\skote\Desktop\Years\HEALTH_DATA.npy')
                x = np.load(result_path)
                
                x = x.astype('float')
                x = x.flatten() 
                
                ybuf = array_map(y)
                xbuf = array_map(x)
                
                plt.plot(ybuf[year*52:(year+1)*52])
                plt.plot(xbuf)
                if week==1:
                    plt.title(data_type+' Model Prediction-Nowcasting')
                else:
                    plt.title(data_type+' Model Prediction-Forecasting')
                plt.ylabel('ILI Cases')
                plt.xlabel('Weeks')
                plt.legend(['Truth','Prediction'], loc='upper left')
                save_folder = os.path.join(r'C:\Users\skote\Desktop\New Method\Plots',str(week),str(year))
                if(not os.path.exists( save_folder)):
                    os.makedirs( save_folder)
                plt.savefig(os.path.join(save_folder,data_type+'_'+str(week)+"_"+str(year)+'_Predictions'+'.png'))
                plt.clf()       

 # entry point

run()
