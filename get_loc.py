import pandas as pd
import tweepy
import time
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
        time.sleep(2)
        userobj = api.get_user(username)
        return userobj

def get_loc_status(id):
    time.sleep(2)
    status_obj  = api.get_status(id)
    if (status_obj.place is None):   
        return None
    else:
        return status_obj.place.name

#   xdefdef update_info(place):
    #df = pd.read_csv("C:\\Users\\User\\Desktop\\Διπλωματική\\twitter_files\\output_got2.csv")
tweets_info = {"Greek_only_tweets" : 0,"empty_tweets" : 0 ,"accurate_tweets" :0,"error_tweets":0 }
user_loc = {}
tweet_loc = {}
geolocator = Nominatim(user_agent="my-application")

for tweet_id in tweets["id"]:
    try:
        #time.sleep(10)
       # print("1\n")
        location = get_loc_status(tweet_id)
        tweet_time = tweets.loc[tweets['id'] == tweet_id,"date"].iloc[0]
        tweet_text = tweets.loc[tweets['id'] == tweet_id,"text"].iloc[0]
        hashtags = tweets.loc[tweets['id'] == tweet_id,"hashtags"].iloc[0]
        mentions = tweets.loc[tweets['id'] == tweet_id,"mentions"].iloc[0]
        if( location is not None  ): #αν υπαρχει τοποθεσια παιξε
            #print("2\n")
            where = geolocator.geocode(location,timeout=None)
            if( (where is not None) and ( ( where.raw['display_name'].split(',')[-1] == ' Ελλάδα') or ( where.raw['display_name'].split(',')[-1] == 'Ελλάδα')) ):# αν δεν εχει βαλει βλακειες στη τοποθεσια και η τοποθεσια ειναι η ελλαδα 
                tweet_loc[tweet_id] = (where.raw['display_name'].split(','),tweet_time,tweet_text,hashtags,mentions)
                print( tweet_loc[tweet_id] )
                if(len(where.raw['display_name'].split(','))==1):
                    tweets_info["Greek_only_tweets"]+=1
                else:
                    tweets_info["accurate_tweets"]+=1  
            else:
                tweets_info["empty_tweets"]+=1
        else:   #αλλιως τσεκαρε χρηση
            username = tweets.loc[tweets['id'] == tweet_id,"username"].iloc[0]
            if(username in user_loc): ## αν εχω ξανατσεκαρει χρηστη
                #print("4\n")
                if ((user_loc[username] == "") or ( user_loc[username] is None) ): ##αν ο χρηστης δε λεει τιποτα
                    tweets_info["empty_tweets"]+=1
                    continue # 
                else: ## αλλιως βαλε οτι λεει
                        tweet_loc[tweet_id] = (user_loc[username],tweet_time,tweet_text,hashtags,mentions)
                        print( tweet_loc[tweet_id] )
                        if(len(tweet_loc[tweet_id][0])==1):
                            tweets_info["Greek_only_tweets"]+=1
                        else:
                            tweets_info["accurate_tweets"]+=1
            else:    ## αν δεν εχω τσεκαρει χρηστη
               # print("4\n")
                userOBJ = get_user_details(username)
                if ( (userOBJ.location =="") ):
                    #print("5\n")
                    tweets_info["empty_tweets"]+=1
                    user_loc[username] = userOBJ.location
                else: ## αλλιως αν λεει κατι για δες τι λεει
                    #print("6\n")
                    where = geolocator.geocode(userOBJ.location,timeout=None)
                    if( (where is not None) and ( ( where.raw['display_name'].split(',')[-1] == ' Ελλάδα') or ( where.raw['display_name'].split(',')[-1] == 'Ελλάδα')) ):
                        user_loc[username] = where.raw['display_name'].split(',')
                        tweet_loc[tweet_id] = (user_loc[username],tweet_time,tweet_text,hashtags,mentions)                       
                        print( tweet_loc[tweet_id] )
                        if(len(where.raw['display_name'].split(','))==1):
                            tweets_info["Greek_only_tweets"]+=1
                        else:
                            tweets_info["accurate_tweets"]+=1
                    else:
                        user_loc[username] = ""
                        tweets_info["empty_tweets"]+=1        
    except Exception as inst:
        print(type(inst))    # the exception instance
        print(inst.args)       # arguments stored in .args
        print(inst)        
        tweet_loc[tweet_id] = 'error:'+ str(tweet_id)
        tweets_info["error_tweets"]+=1
        continue


myfile = open("output.csv", "w",encoding='utf8')  
w = csv.writer(myfile)
for key, val in tweet_loc.items():
    w.writerow([key, val[0], val[1], val[2], val[3], val[4]]) # ftiakse kai auto edw gia to csv
myfile.flush()    
   
myfile2 = open("output_info.csv", "w",encoding='utf8') 
x = csv.writer(myfile2)
for key, val in tweets_info.items():
    w.writerow([key, val])
myfile2.flush()
