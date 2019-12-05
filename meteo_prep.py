import unicodedata
import pandas as pd
import re 
import os
import numpy as np
import csv
months = ['Ιανουάριο','Φεβρουάριο','Μάρτιο','Απρίλιο','Μάιο','Ιούνιο','Ιούλιο','Αύγουστο','Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο']
years = [2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019]
counties = {'Αττική':'Αττική',\
            'Κρήτη':'Κρήτη',\
            'Κεντρικής Μακεδονίας':['Θεσσαλονίκη','Μακεδονία'],\
            'Πελοποννήσου':'Πελοπόννησος',\
            'Βόρειου Αιγαίου':'Βόρειο & Ανατολικό Αιγαίο',\
            'Ηπείρου':'Ήπειρος',\
            'Θεσσαλίας':['Θεσσαλία','Σποράδες'],\
                'Νοτίου Αιγαίου':'Δωδεκάνησα',\
            'Ανατολικής Μακεδονίας και Θράκης':'Θράκη',\
                'Ιονίων Νήσων':'Νησιά_Ιονίου',\
            'Στερεάς Ελλάδας':['Εύβοια','Στερεά_Ελλάδα'],\
                'Δυτικής Μακεδονίας':'Δίκτυο_Κοζάνης',\
            'Δυτικής Ελλάδας' : ['Αιτωλοακαρνανία','Αχαία','Ηλείας']}

categories = [0,1,2,4,8,9,10]

columns = 'Day,Mean_temp,Max_temp,Max_temp_time,Min_temp,Min_temp_time,Max_RH,Min_RH,Rain,AWS,Max_WS,Max_WS_time,DIR'

def get_data(file):
    lines = file.readlines()
    data = []
    for line in lines:
        if (len(line)>1):
            if (  (line[0].isnumeric() ) or ( line[1].isnumeric() )  ):
                data.append(re.sub("\s+", ",", line.strip()))
    return data
       
def write_to_csv(name,data):
    with open(name+".csv",  mode='w',newline='') as file:
        file_writer = csv.writer(file)
        file_writer.writerow( columns.split(',') )
        for iter in data:
            file_writer.writerow( iter.split(',') )
        print("Success for" + name)
        file.close()

average = {}

def get_average_month_county_year(county,month,year):
    count = 0
    number = 0
    month_data = pd.DataFrame({'A' : []})
    for filename in os.listdir():
        if (os.path.isfile(filename) and (county in filename) and ('.txt' in filename) and (str(year) in filename)and ( filename.endswith(".csv") ) and (month in filename) and (os.stat(filename).st_size != 0)):
            print(filename)
            if( (county == 'Πελοπόννησος') and ( ('Αχαίας' in filename) or ('Αιτωλοακαρνανίας' in filename) or ('Ηλείας' in filename) ) ):
                print("I skipped " + filename)
                continue
            try:
                if(count==0):
                    month_data = pd.read_csv(filename,usecols=categories)
                    if(month_data.select_dtypes(include=["float", 'int']).empty):
                        continue
                    count = 1
                    by_row_index = month_data
                else:
                    buffer = pd.read_csv(filename,usecols=categories)
                    if(buffer.select_dtypes(include=["float", 'int']).empty):
                        continue
                    month_data = pd.concat((month_data,buffer)) 
                    by_row_index = month_data.groupby(month_data.index)
                number+=1    
            except Exception as inst:
                print(inst)
                print( str(filename))
                return  pd.DataFrame({'A' : []})
        else:
            continue
    print("Νumber of sub_csvs  is " + str(number))
    if number>1:
        return by_row_index.mean()
    else: 
        return  month_data

for filename in os.listdir():
    if (os.path.isfile(filename) and filename.endswith(".txt") and ('' in filename) and (os.stat(filename).st_size != 0)):
        with open(filename, "r",encoding='utf-8') as file:
            try:
                numbers = get_data(file)
                write_to_csv(filename,numbers)    
            except Exception as inst:
                print(inst)
                print( str(filename) )               

def write_meteo_averages(counties):
    runs = 0
    for county in counties:
        print('This is the number of counties I ve visited ' + str(runs) + " \n")
        runs+=1
        print('Checking county '+ county )
        if type(counties[county])==list: # αν εχω 2 ενότητες για την περιφέρεια
            for year in years: # για κάθε χρονιά
                print('Checking year '+ str(year) )
                for month in months: # για κάθε μήνα
                    if((year == 2019) and (month in ['Αύγουστο','Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο'])):
                        print('skip')
                        continue
                    print('Checking month '+ str(month) )
                    average1 = get_average_month_county_year(counties[county][0],month,year) # βρες τον μέσο όρο για κάθε ενότητα
                    average2 = get_average_month_county_year(counties[county][1],month,year)
                    if((not average1.empty) and (not average2.empty)): # αν και οι 2 δεν ειναι άδειες , ενωσε τες
                        final = pd.concat((average1,average2)) 
                        med = final.groupby(final.index) 
                        final = med.mean()
                    elif((not average1.empty)): # αλλιώς βρες ποια δεν είναι άδεια
                        final = average1
                    elif((not average2.empty)):
                        final = average2
                    else:
                        continue # αλλιώς αν και οι 2 αδειες , συνέχισε με επόμενο μήνα
                    filename = county+" "+str(year)+" "+month 
                    try:
                        print("This is what is written " + "\n")
                        print(final)
                        final.to_csv(filename+'.csv')
                    except Exception as inst:
                            print(inst)
                            print( str(filename))
        else:
            for year in years:
                print('checking year '+ str(year) )
                for month in months:
                    if((year == 2019) and (month in ['Αύγουστο','Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο'])):
                        print('skip')
                        continue
                    print('checking month '+ month )
                    #if ( (counties[county]+" "+str(year)+" "+month+".csv") in os.listdir()):
                    #    continue
                    average = get_average_month_county_year(counties[county],month,year)
                    if(average.empty):  
                        continue
                    filename = counties[county]+" "+str(year)+" "+ month 
                    try:
                        print("This is what is written " + "\n")
                        print(average)
                        average.to_csv(filename+'.csv')  
                    except Exception as inst:
                        print(inst)
                        print( str(filename))
                   