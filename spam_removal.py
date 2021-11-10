import pandas as pd
from collections import defaultdict

Spam_Accounts = defaultdict(dict) # A dictionary containing all the spam accounts

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
		if account not in Spam_Accounts :
			buffer =(df.loc[df['username'] == account,"text"].iloc[0] ).lower()
			if 'http' not in buffer :
				Real_Tweets = df[df['username'] == account]
				Real_Tweets.to_csv('Real_Tweets.csv', mode='a+', header=False)		
df = pd.read_csv(r'C:\Users\skote\Desktop\Twitter Files\Real Tweets.csv' )
df = df.drop_duplicates(subset='text')
df.to_csv('Real Tweets.csv', mode='w')		
