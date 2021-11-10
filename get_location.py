import pandas as pd
import tweepy
import time as tm
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from collections import defaultdict
from datetime import datetime
from notify_run import Notify

notify = Notify()

text_file = open("Location Errors.txt",'w+')
geolocator = Nominatim(user_agent="my-application")
tweets_info = {"Greek_only_tweets" : 0,"empty_tweets" : 0 ,"accurate_tweets" :0,"error_tweets":0 }
user_loc = {}
tweet_loc = {}
count=0
keys = defaultdict(dict)
spam = defaultdict(dict)


def get_user_details(username):
        tm.sleep(2)
        userobj = api.get_user(username)
        return userobj
        

def get_loc_status(id):
    tm.sleep(2)
    status_obj  = api.get_status(id)
    if (status_obj.place is None):   
        return None
    else:
        return status_obj.place.name


# Checks to see if location is Greece 
def In_Greece(where):
    if( (where is not None) and (where != "")
                    and ( ( where.raw['display_name'].split(',')[-1] == ' Ελλάδα')\
                    or ( where.raw['display_name'].split(',')[-1] == 'Ελλάδα')) ):
        return True
    else:
        return False


def update_info(where,*args):   
    if(In_Greece(where)):
        tweet_loc[args[0]] = [where.raw['display_name'].split(','),args[1],args[2],args[3],args[4]]#time,text,hashtags,mentions)
        #print( tweet_loc[id] )
        if(len(where.raw['display_name'].split(','))==1):
            tweets_info["Greek_only_tweets"]+=1
        else:
            tweets_info["accurate_tweets"]+=1
    else:
        tweets_info["empty_tweets"]+=1


def check_user(username):
    username = tweets.loc[tweets['id'] == tweet_id,"username"].iloc[0]
    if(username in user_loc): ## αν εχω ξανατσεκαρει χρηστη
        if ((user_loc[username] == "") or ( user_loc[username] is None) ):
            return False
  

def write_dict_to_csv(name,dict,*columns):
    
    for key, val in dict.items():
        if key in keys: #checks to see if we have already written that key
            continue
        if(type(val)==list):
            week,year = get_week(val[1])
            county = find_county(val[0][3])
            path = "~county_path" + county + "\\" + str(year) + "\\" + str(week) + "\\" + "output.csv"
            print(path)
            myfile = open(path, "a+",encoding='utf8')  
            w = csv.writer(myfile)
            if(columns):
                w.writerow( *columns)
            keys[key]=True
            w.writerow([key, *val])
            myfile.flush()
        else:
            myfile = open(r'~county_path\output_info.csv', "a+",encoding='utf8')  
            w = csv.writer(myfile)
            if(columns):
                w.writerow( *columns)
            keys[key]=True
            w.writerow([key, val])
            myfile.flush()
     

def get_week(date):
    dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    week = datetime.date(dt).isocalendar()[1]
    return week,dt.year
    

def find_county(location):
    counties = ['Αττικής','Κρήτης','Δυτικής Ελλάδας','Κεντρικής Μακεδονίας','Πελοποννήσου','Βορείου Αιγαίου','Ηπείρου','Θεσσαλίας','Νοτίου Αιγαίου','Ανατολικής Μακεδονίας και Θράκης','Ιονίων Νήσων','Στερεάς Ελλάδας','Δυτικής Μακεδονίας']
    place = location
    for item in counties:
        if item in place:
            place = item
    return place
     
    
with open('SpamAccs.txt') as f: #remove spam accounts
        account = f.readline()
        while account:
            account = account.rstrip('\n')
            spam[account] = 1        
            account = f.readline() 
spam = {k.replace(' ', ''): v for k, v in spam.items()}
    
for tweets in pd.read_csv('path\\all.csv', chunksize=5000):   
    for tweet_id in tweets["id"]:
        if (tweets.loc[tweets['id'] == tweet_id,"username"].iloc[0] in spam):
            print(count)
            count+=1
            continue
        try:
            location = get_loc_status(tweet_id)     #get location of tweet
            time = tweets.loc[tweets['id'] == tweet_id,"date"].iloc[0] # and the other parameters
            text = tweets.loc[tweets['id'] == tweet_id,"text"].iloc[0]
            hashtags = tweets.loc[tweets['id'] == tweet_id,"hashtags"].iloc[0]
            mentions = tweets.loc[tweets['id'] == tweet_id,"mentions"].iloc[0]
            if( location is not None  ):            #αν υπαρχει τοποθεσια παιξε
                where = geolocator.geocode(location)
                print (where)
                update_info(where,tweet_id,time,text,hashtags,mentions) 
            else:   
                username = tweets.loc[tweets['id'] == tweet_id,"username"].iloc[0]
                if(not check_user(username)):    ##αν ο χρηστης δε λεει τιποτα
                    print("This User says None")
                    update_info(None) 
                    user_loc[username] = ""    
                else:    ## αν δεν εχω τσεκαρει χρηστη
                    print("Checking User: " + username)
                    userOBJ = get_user_details(username)
                    if ( (userOBJ.location == "") ):
                        update_info(None)
                        user_loc[username] = userOBJ.location
                    else: ## αλλιως αν λεει κατι για δες τι λεει
                        where = geolocator.geocode(userOBJ.location)
                        user_loc[username] = where.raw['display_name'].split(',')
                        update_info(where,tweet_id,time,text,hashtags,mentions)                            
        except Exception as inst:
            text_file.write("ID %s Error %s " % ( tweet_id ,inst))
            tweet_loc[tweet_id] = 'error:'
            tweets_info["error_tweets"]+=1
            continue
    text_file.close() 
    write_dict_to_csv("output_from_new_get_loc",tweet_loc)   
    write_dict_to_csv("output_from_new_get_loc_info",tweets_info)  
    notify.send('Get Loc Finished !!!!!!!!!!!! ' )    