import time 
import GetOldTweets3 as got
import csv
import os
from retrying import retry
import os
import pickle
import matplotlib.pyplot as plt
import itertools

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def mineTweets(args):
    year, ms, ds, nds= args[0]
    city = args[1]
    try:
        row = []
        tweetCriteria = got.manager.TweetCriteria().setNear(city+",Ελλάδα").setWithin("30mi").setSince(str(year)+"-"+ms+"-"+ds).setUntil(str(year)+"-"+ms+"-"+nds)
        tweet = got.manager.TweetManager.getTweets(tweetCriteria)
        rows = [[tweet[i].date,tweet[i].username,tweet[i].id,tweet[i].text] for i in range(len(tweet))]
        with open(os.path.join(city+"Tweets.csv"), "a+",newline='') as myfile:
            T = csv.writer(myfile)
            T.writerows(row)
    except Exception as inst:
        print(inst)
            
time_parameters = [[str(year),str(month),str(day),str(day+1)] for year in range(2010,2020) for month in range(1,13) for day in range(1,31)] 
time_parameters = [item for item in time_parameters if not (item[1]==2 and item[2]>28)]
cities = ['Athens','Thessaloniki']
parameters = list(itertools.product(time_parameters,cities))
for args in parameters:
    mineTweets(args)
