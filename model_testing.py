
def create_model(neurons=1, dropout=[0, 0 ], window_size=2,data_size=1,optimizer='nadam'):
  
  batch_size = 1
  Input_Layer = Input(shape=( window_size, data_size ))
  drop1 = Dropout(dropout[0])(Input_Layer)
  lstm = LSTM(neurons,kernel_initializer='glorot_normal')(drop1)
  drop2 = Dropout(dropout[1])(lstm)
  dense = Dense(1)((drop2))
  model = Model (inputs = Input_Layer, outputs = dense)                   
  model.compile(loss='mse', optimizer=optimizer, metrics=[tf.keras.metrics.RootMeanSquaredError()])
  
  return model


def test_models(mode = 'basic'):

  model_types = {'basic':['M','T','H'],
                 'advanced':['MH','MTH']}

  data_names = {'H':'total.npy', 'T':'TWEET_DATA.npy','M':'METEO_DATA.npy'}
  params = {'H':[8,[0,0],4,2], 'T':[90,[0.1,0],4,226],'M':[60,[0,0],4,104]}
  settings = params[model_type]
  window_size = settings[2]
  epochs = 50
  for forecast_horizon in range(1,4):
    for model_type in model_types:
      
      series_x = np.load(os.path.join(head_path, data_names[model_type]))
      series_y = np.load(os.path.join(head_path,'HEALTH_DATA.npy'))
      truth = np.load(os.path.join(head_path,'HEALTH_DATA.npy'))
      truth = truth[forecast_horizon:]
      series_x = series_x[:-forecast_horizon] 
      series_y =series_y[forecast_horizon:]
      
      directory = r'/content/drive/MyDrive/Final Thesis Fragkozidis Georgios/C:/Users/skote/Desktop/New Method/Final Method'
      
      for test_set in range(0,10):
        model = create_model(settings[0],settings[1],settings[2],settings[3])
        X, y = sliding_window(series_x,window_size), sliding_window(series_y,window_size)
        train = list()
        val = list()
        X_train, y_train, X_test, y_test = get_test_partition(X, y, test_set)
        
        for i in range(epochs):
          
          if np.size(X_train[0]):
            history = model.fit(X_train[0], y_train[0][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
          predict = model.predict(X_test)
          model.reset_states()
          if np.size(X_train[2]):
            history = model.fit(X_train[2], y_train[2][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
            model.reset_states()
          if i==49:
            np.save(os.path.join(directory,'Results', model_type +'_'+ str(forecast_horizon)+'_'+str(2010+test_set) ),predict[-52:])
            np.save(os.path.join(directory,'Results', 'Truth_'+ str(forecast_horizon)+'_'+str(2010+test_set) ),y_test[-52:,-1,-1])
            print(model_type+'_'+str(forecast_horizon)+'_'+str(2010+test_set))
            print(mean_squared_error(predict[-52:,-1],y_test[-52:,-1,-1]))
            #plot_cases(predict,y_test, truth,forecast_horizon,window_size, test_set, directory, model_type)
            #plot_learning(train,val)
          
          val.append(mean_squared_error(predict[-52:,-1],y_test[-52:,-1,-1]))
          train.append((history.history['loss'][0]))#,history.history['root_mean_squared_error'][0] ))
    
        model.reset_states()
        model.save(os.path.join(directory,'Models',model_type+str(forecast_horizon)+str(test_set)))

test_models()

from keras.layers import Dense, TimeDistributed


def create_model(neurons=1, dropout=[0, 0 ], window_size=2,data_size=1,optimizer='nadam'):
  batch_size = 1
  Input_Layer = Input(shape=( window_size, data_size ))
  lstm = LSTM(neurons,return_sequences=False,kernel_initializer='glorot_normal')(Input_Layer)
  drop2 = Dropout(dropout[1])(lstm)
  dense = Dense(1)((drop2))
  model = Model (inputs = Input_Layer, outputs = dense)                   
    
  model.compile(loss='mse', optimizer=optimizer, metrics=[tf.keras.metrics.RootMeanSquaredError()])
  return model


def merge_models(model1, model2):
  
  w1 = model1.get_weights()
  w2 = model2.get_weights()
  
  m1 =  create_model(60,[0,0],4,104)  #M model
  m2 =  create_model(8,[0,0],4,2)  #T model
  
  m1.set_weights(w1)
  m2.set_weights(w2)
  
  

  for layer in m1.layers[:]:
    layer.trainable = False

  for layer in model2.layers[:]:
    layer.trainable = True  
    #if hasattr(layer, 'rate'):
    #  layer.rate = 0  
  m1.compile(optimizer='nadam', loss = 'mse',metrics=['mse'])   
  m2.compile(optimizer='nadam', loss = 'mse',metrics=['mse'])
  input_data = [m1.input,model2.input]
  concat = concatenate([(m1.layers[-2].output), model2.layers[-2].output])
  drop = Dropout(0)(concat)
  dense = Dense(1)(drop)
  merged = Model(inputs=input_data, outputs=[dense])
  merged.compile(optimizer='nadam', loss = 'mse',metrics=['mse'])    

  return merged


def final_model(model1,model2):
  mh = model1
  
  w2 = model2.get_weights()
  t = create_model(90,[0.1,0],4,226)
  t.set_weights(w2)
  for layer in mh.layers[:]:
    layer.trainable=True
  for layer in t.layers[:]:
    layer.trainable=True  
  t.compile(optimizer='nadam', loss = 'mse',metrics=['mse'])
  input_data = [mh.input,t.input]
  concat = concatenate([ Dropout(0.1)(mh.layers[-2].output), Dropout(0.2)(t.layers[-2].output)])
  drop = Dropout(0)(concat)
  dense = Dense(1)(drop)
  merged = Model(inputs=input_data, outputs=[dense])
  merged.compile(optimizer='nadam', loss = 'mse',metrics=['mse'])   

  return merged
def test_models():
 
  window_size = 4 
  merged_models = ['MTH']
  model_types = ['M','H','T']
  data_names = {'H':'total.npy', 'T':'TWEET_DATA.npy','M':'METEO_DATA.npy'}

  epochs = 50
  for forecast_horizon in range(3,4):
    for model_type in  merged_models:
      truth = np.load(os.path.join(head_path,'HEALTH_DATA.npy'))
      truth = truth[forecast_horizon:]
      series_x1 = np.load(os.path.join(head_path, data_names['M']))
      series_x2 = np.load(os.path.join(head_path, data_names['H']))
      series_x3 = np.load(os.path.join(head_path, data_names['T']))
      series_x3[0:36] = series_x3[52:36+52]
      series_y = np.load(os.path.join(head_path,'HEALTH_DATA.npy'))
      scaler,series_x1,_ = scale(series_x1,series_x1)
      scaler,series_x2,_ = scale(series_x2,series_x2)
      scaler,series_x3,_ = scale(series_x3,series_x3)
      series_x1 = series_x1[:-forecast_horizon] 
      series_x2 = series_x2[:-forecast_horizon] 
      series_x3 = series_x3[:-forecast_horizon] 
      series_y = series_y[forecast_horizon:]
     
      directory = r'/content/drive/MyDrive/Final Thesis Fragkozidis Georgios/C:/Users/skote/Desktop/New Method/Final Method'
      for test_set in range(8,10):
        if model_type=='MH':
          model1 = tf.keras.models.load_model(os.path.join(directory,'Models','M'+str(forecast_horizon)+str(test_set)))
          model2 = tf.keras.models.load_model(os.path.join(directory,'Models','H'+str(forecast_horizon)+str(test_set)))
        y = sliding_window(series_y,window_size)
        X1 = sliding_window(series_x1,window_size)
        X2 = sliding_window(series_x2,window_size) 
        X_train1, y_train, X_test1, y_test = get_test_partition(X1, y, test_set)
        X_train2, y_train, X_test2, y_test = get_test_partition(X2, y, test_set)
        if model_type=='MTH':
          model1 = tf.keras.models.load_model(os.path.join(directory,'Models','MH'+str(forecast_horizon)+str(test_set)))
          model2 = tf.keras.models.load_model(os.path.join(directory,'Models','T'+str(forecast_horizon)+str(test_set)))
          X3 = sliding_window(series_x3,window_size) 
          X_train3, y_train, X_test3, y_test = get_test_partition(X3, y, test_set)
          model = final_model(model1, model2)
        else:
          model = merge_models(model1, model2)
        train = list()
        val = list()
        for i in range(epochs):
          if model_type=='MTH':
            if np.size(X_train1[0]):
              history = model.fit([[X_train1[0],X_train2[0]],X_train3[0]], y_train[0][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
            predict = model.predict([[X_test1,X_test2],X_test3])
            if np.size(X_train1[2]):
              history = model.fit([[X_train1[2],X_train2[2]],X_train3[2]], y_train[2][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
              model.reset_states()
            #model.reset_states()
            val.append(mean_squared_error(predict[-52:,-1],y_test[-52:,-1,-1]))
            train.append((history.history['loss'][0]))#,history.history['val_root_mean_squared_error'][0]))  
          else:
            if np.size(X_train1[0]):
              history = model.fit([X_train1[0],X_train2[0]], y_train[0][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
            predict = model.predict([X_test1,X_test2])
            if np.size(X_train1[2]):
              history = model.fit([X_train1[2],X_train2[2]], y_train[2][:,-1,-1],shuffle=True,batch_size=1, epochs=1, verbose=0)
              model.reset_states()
            
            #model.reset_states()
            val.append(mean_squared_error(predict[-52:,-1],y_test[-52:,-1,-1]))
            train.append((history.history['loss'][0]))#,history.history['val_root_mean_squared_error'][0]))  
          if i==(epochs-1):
            model.save(os.path.join(directory,'Models',model_type+str(forecast_horizon)+str(test_set)))
            np.save(os.path.join(directory,'Results', model_type +'_'+ str(forecast_horizon)+'_'+str(2010+test_set) ),predict)
            print(mean_squared_error(predict[-52:,-1],y_test[-52:,-1,-1]))
            plot_cases(predict,y_test, truth,forecast_horizon,window_size, test_set, directory, model_type)
            plot_learning(train,val)
test_models()