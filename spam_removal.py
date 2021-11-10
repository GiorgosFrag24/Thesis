import pandas as pd
from collections import defaultdict
import botometer
from collections import defaultdict
from notify_run import Notify
notify = Notify()

Spam_Accounts = defaultdict(dict) # A dictionary containing all the spam accounts


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
with open("Spam Accounts.txt") as f:
	account = f.readline()
	while account:
		Spam_Accounts[account.rstrip(' \n')] = -1
		account = f.readline()
## If the account is not spam or the text doesnt contain a url ###
## which is common for bot accounts ##############################
## then keep it ##################################################
for df in pd.read_csv(r'path\Raw Tweets 2010-2019.csv', chunksize=5000):
	for account in df['username'].values:
		bot_score = bom.check_account(account)
		if account not in Spam_Accounts:
			if (bot_score['scores']['universal']>=0.43):
				Spam_Accounts[account]=1
				continue
			buffer =(df.loc[df['username'] == account,"text"].iloc[0] ).lower()
			if 'http' not in buffer :
				Real_Tweets = df[df['username'] == account]
				Real_Tweets.to_csv('Real_Tweets.csv', mode='a+', header=False)		

df = pd.read_csv(r'~path\Real Tweets.csv' )
df = df.drop_duplicates(subset='text')
df.to_csv('Real Tweets.csv', mode='w')		
