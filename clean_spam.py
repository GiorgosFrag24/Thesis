import pandas as pd
from bs4 import BeautifulSoup
import botometer

df = pd.read_csv("C:\\Users\\User\\Desktop\\Διπλωματική\\twitter_files\\sample_clean.csv") # βάζω όποιο αρείο θέλω

rapidapi_key = "ebc81ab30fmsh3ff7cd41c4ee3f9p1d564cjsn1e6fb4d1ca51" # now it's called rapidapi key
twitter_app_auth = {
    'consumer_key': 'XLfRlXSVKIpH28wahBwVBbPCy',
    'consumer_secret': 'PFsLz8P4HppMKOglDginEFxWUxZH6Ghfem3qg6FSu2xxFUwnEK',
    'access_token': '1156146192448917504-M9Hss2TbG5YOR7FC9d2QtK1DPA5J5B',
    'access_token_secret': 'khVPFfyK0B4lJCDPW86Vup4dN5IiI2F2SpC0GbevQrEnB',
  }
bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)

#print(df)
text_file = open("Clean Spam Errors.txt",'w')
for account in df['username'].values:
    print("checking" +account +"\n")
    try:
        bot_score = bom.check_account(account)
        if (bot_score['scores']['universal']>=0.5):
            print("to profil " + account + "einai pseutiko \n")
            indexNames = df[ df['username'] == account ].index    
            df.drop(indexNames , inplace=True)
        else:
            continue
    except Exception as inst:
        text_file.write("%s  %s " % ( df.loc[df['username'] == account,"id"].iloc[0] ,inst))
        #print(inst)        
        continue
text_file.close()               
df.to_csv(r'C:\Users\User\Desktop\Διπλωματική\twitter_files\clean_tweets.csv')        
