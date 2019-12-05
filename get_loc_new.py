import pandas as pd
import tweepy
import time as tm
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
tweets = pd.read_csv("C:\\Users\\User\\Desktop\\Διπλωματική\\twitter_files\\sample_clean.csv")
consumer_key= 'XLfRlXSVKIpH28wahBwVBbPCy'
consumer_secret = 'PFsLz8P4HppMKOglDginEFxWUxZH6Ghfem3qg6FSu2xxFUwnEK'
access_token =  '1156146192448917504-M9Hss2TbG5YOR7FC9d2QtK1DPA5J5B'
access_token_secret =  'khVPFfyK0B4lJCDPW86Vup4dN5IiI2F2SpC0GbevQrEnB'
auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

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
def valid(where):
    if( (where is not None) and (where != "")
                    and ( ( where.raw['display_name'].split(',')[-1] == ' Ελλάδα')\
                    or ( where.raw['display_name'].split(',')[-1] == 'Ελλάδα')) ):# αν δεν εχει βαλει βλακειες στη τοποθεσια και η τοποθεσια ειναι η ελλαδα 
        return True
    else:
        return False

def update_info(where,*args):  
    if(valid(where)):
        tweet_loc[id] = (where.raw['display_name'].split(','),args[0],args[1],args[2],args[3])#time,text,hashtags,mentions)
        print( tweet_loc[id] )
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
    myfile = open(name+".csv", "w",encoding='utf8')  
    w = csv.writer(myfile)
    w.writerow([*columns])
    for key, val in dict.items():
        if(type(val)==list):
            w.writerow([key, *val])
        else:
            w.writerow([key, val])
    myfile.flush() 
    
tweets_info = {"Greek_only_tweets" : 0,"empty_tweets" : 0 ,"accurate_tweets" :0,"error_tweets":0 }
user_loc = {}
tweet_loc = {}
geolocator = Nominatim(user_agent="my-application")
text_file = open("Location Errors.txt",'w')

for tweet_id in tweets["id"]:
    try:
        location = get_loc_status(tweet_id)     #gt location of tweet
        time = tweets.loc[tweets['id'] == tweet_id,"date"].iloc[0] # and the other parameters
        text = tweets.loc[tweets['id'] == tweet_id,"text"].iloc[0]
        hashtags = tweets.loc[tweets['id'] == tweet_id,"hashtags"].iloc[0]
        mentions = tweets.loc[tweets['id'] == tweet_id,"mentions"].iloc[0]
        if( location is not None  ): #αν υπαρχει τοποθεσια παιξε
            where = geolocator.geocode(location,timeout=None)
            update_info(where,tweet_id,time,text,hashtags,mentions) 
        else:   
            username = tweets.loc[tweets['id'] == tweet_id,"username"].iloc[0]
            if(not check_user(username)):    ##αν ο χρηστης δε λεει τιποτα
                update_info(None)        
            else:    ## αν δεν εχω τσεκαρει χρηστη
                userOBJ = get_user_details(username)
                if ( (userOBJ.location =="") ):
                    update_info(None)
                    user_loc[username] = userOBJ.location
                else: ## αλλιως αν λεει κατι για δες τι λεει
                    where = geolocator.geocode(userOBJ.location,timeout=None)
                    user_loc[username] = where.raw['display_name'].split(',')
                    update_info(where,tweet_id,time,text,hashtags,mentions)                            
    except Exception as inst:
        text_file.write("ID %s Error %s " % ( tweet_id ,inst))
        tweet_loc[tweet_id] = 'error:'
        tweets_info["error_tweets"]+=1
        continue
text_file.close() 

write_dict_to_csv("output_from_new_get_loc",tweet_loc,['id','place','date','text','hashtags','mentions'])   
write_dict_to_csv("output_from_new_get_loc_info",tweet_info)   

