from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import pickle
from datetime import datetime
import numpy as np
 
with open('county_dict.pickle', 'rb') as handle:
    county_dict = pickle.load(handle)
with open('station_dict.pickle', 'rb') as handle:
    station_dict = pickle.load(handle)    

url = 'http://meteosearch.meteo.gr/'    
driver = webdriver.Chrome("C:\\Users\\User\\Desktop\\Διπλωματική\\chromedriver")


currentMonth = datetime.now().month
currentYear = datetime.now().year
driver.get(url)

ct = driver.find_element_by_id('select')
counties = ct.find_elements_by_tag_name('option')

for i in range(len(counties)):    
    counties = driver.find_element_by_id('select').find_elements_by_tag_name('option')
    #county_dict = np.load('C:\\Users\\User\\Desktop\\Διπλωματική\\meteo_files\\county_dict.npy').item()
    for county in counties:
        if(county.text in county_dict):
            if(county_dict[county.text] == "visited"): #το ιδιο και για τους δημους
                continue
        else: county_dict[county.text] = "visited"
        county_dict[county.text] = "visited"#####    
        county_name = county.text
        if (" " in county_name):
            county_name = county_name.replace(" ","_")
        if ("-" in county_name):
            county_name = county_name.replace("-","_")
        if ("/" in county_name):
            county_name = county_name.replace("/","_")
        if ("&" in county_name):
            county_name = county_name.replace("&","_")
        if ("&" in county_name):
            county_name = county_name.replace("&","_")
        county.click()
        st = driver.find_element_by_id('select1') #select a station
        stations = st.find_elements_by_tag_name('option')
        for j in range(len(stations)):
            print("irtha")
            stations = driver.find_element_by_id('select1').find_elements_by_tag_name('option')    
            #station_dict = np.load('C:\\Users\\User\\Desktop\\Διπλωματική\\meteo_files\\station_dict.npy')
            for station in stations:
                try:
                    print('now visiting' +" "+ station.text)
                except:
                    continue
                if(station.text in station_dict):
                    if(station_dict[station.text] =="visited"): #το ιδιο και για τους δημους
                        continue
                else :station_dict[station.text] ="visited"      
                station_dict[station.text] = "visited"#####    
                station_name = station.text
                time.sleep(0.5)
                station.click()
                search = driver.find_element_by_id('button')
                search.click()
                yr = driver.find_element_by_id('SelectYear') #select year
                year_range = driver.find_elements_by_class_name("Entono")[1].text
                month_range = driver.find_elements_by_class_name("Entono")[0].text
                for year in yr.find_elements_by_tag_name('option'): #kane ta panta
                    year_value = int(year.get_attribute("value"))
                    #print (int(year.get_attribute("value")))
                    time.sleep(1)
                    if year_value <= int(year_range):
                        continue
                    year.click()
                    mth = driver.find_element_by_id('SelectMonth') #select month
                    for month in mth.find_elements_by_tag_name('option'):
                        month_value = month.text
                        if(year_value == currentYear):
                            if(int(month.get_attribute("value"))>= currentMonth):
                                continue
                        time.sleep(1)
                        month.click()
                        done = 1
                        search = driver.find_element_by_name("Submit")
                        search.click()
                        handles = driver.window_handles
                        #print(handles)
                        driver.switch_to_window(handles[1])
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        text_soup = soup.find('pre')
                        text = text_soup.getText() if text_soup else ""
                        driver.close()
                        #print (text)
                        if (" " in station_name):
                            station_name = station_name.replace(" ","_")
                        if ("-" in station_name):
                            station_name = station_name.replace("-","_")
                        if ("/" in station_name):
                            station_name = station_name.replace("/","_")
                        if ("&" in station_name):
                            station_name = station_name.replace("&","_")
                        if ("&" in county_name):
                            station_name = station_name.replace("&","_")
                        f= open(county_name + "_"+ station_name +"_"+ str(year_value) + "_" + month_value + ".txt","w+",encoding="utf-8")
                        f.write(text)
                        f.close()
                        driver.switch_to_window(handles[0])
                driver.execute_script("window.history.go(-1)")
                with open('station_dict.pickle', 'wb') as handle:
                    pickle.dump(station_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
                break   
        with open('county_dict.pickle', 'wb') as handle:
            pickle.dump(county_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        break    
   
   
   
