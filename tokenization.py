import spacy 
from spacy.lang.el import Greek
import csv
import unicodedata
import math 
from collections import Counter
from collections import defaultdict

error_file = open( "C:\\Users\\Administrator\\Desktop\\diplwmatikh giwrgos fragkozidhs\\Training\\Counties\\" +"\\log.txt",'a+') #Αρχείο για πιθανά errors

#C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training
County_directory = r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Counties'
Tweet_Directory = r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Counties'
Meteo_Directory = r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Counties 2'
Years_directory = r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Years'
Training_Directory = r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Years'

keyword_dict = {}
new_keyword_dict = {}
categories = ['TEMP','HIGH','LOW','RAIN','SPEED','HIGH.1']

counties = ['Αττικής','Κρήτης','Δυτικής Ελλάδας','Κεντρικής Μακεδονίας','Πελοποννήσου','Βόρειου Αιγαίου','Ηπείρου','Θεσσαλίας','Νοτίου Αιγαίου','Ανατολικής Μακεδονίας και Θράκης','Ιονίων Νήσων','Στερεάς Ελλάδας','Δυτικής Μακεδονίας']
geo_map = {'Αττικής':'Αττική',\
		   'Κρήτης':'Κρήτη',\
		   'Δυτικής Ελλάδας':'Δυτικής Ελλάδας',\
		   'Κεντρικής Μακεδονίας':'Κεντρικής Μακεδονίας',\
		   'Πελοποννήσου':'Πελοπόννησος',\
		   'Βόρειου Αιγαίου':'Βόρειο & Ανατολικό Αιγαίο',\
		   'Ηπείρου':'Ήπειρος',\
		   'Θεσσαλίας':'Θεσσαλίας',\
		   'Νοτίου Αιγαίου':'Νοτίου Αιγαίου',\
		   'Ανατολικής Μακεδονίας και Θράκης':'Θράκη',\
		   'Ιονίων Νήσων':'Νησιά_Ιονίου',\
		   'Στερεάς Ελλάδας':'Στερεάς Ελλάδας',\
		   'Δυτικής Μακεδονίας':'Δίκτυο_Κοζάνης'}
months = ['Ιανουάριο','Φεβρουάριο','Μάρτιο','Απρίλιο','Μάιο','Ιούνιο','Ιούλιο','Αύγουστο','Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο']

distribution = {'county':{},\
				'keyword':{}}
				
double_distribution = { 'Αττική':{},\
						'Κρήτη':{},\
						'Δυτικής Ελλάδας':{},\
						'Κεντρικής Μακεδονίας':{},\
						'Πελοποννήσου':{},\
						'Βόρειου Αιγαίου':{},\
						'Ηπείρου':{},\
						'Θεσσαλίας':{},\
						'Νοτίου Αιγαίου':{},\
						'Ανατολικής Μακεδονίας και Θράκης':{},\
						'Ιονίων Νήσων':{},\
						'Στερεάς Ελλάδας':{},\
						'Δυτικής Μακεδονίας':{}}   
 

sp = spacy.load('el_core_news_md')

#token dict contains weekly tweets, rule of thumb most frequent 1-2% 		
def generate_ngrams(token_dict, n): 
	weekly_ngrams = []
	weekly_num = len(token_dict)
	for id,tweet in token_dict.items():
		tokens = token_dict[id]
		ngrams = zip(*[tokens[i:] for i in range(n)])
		weekly_ngrams.extend([" ".join(ngram) for ngram in ngrams])
	c = Counter(weekly_ngrams) 
	
	ngrams = []
	for key in c :
		if c[key]>=5:
			ngrams.append((key,c[key]))
	if not ngrams:
		ngrams = c.most_common(5) 
	return ngrams 

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
				  if unicodedata.category(c) != 'Mn')
				  
def get_tokens(tweets):
	token_dict = collections.defaultdict()
	count = 0
	for id in tweets['id']:	   
		try:
			count += 1
			buffer = (tweets.loc[tweets['id'] == id,"text"].iloc[0] ).lower()
			text =  buffer.split()
			if('http' in text[-1]) or ('https' in text[-1]):
				continue
			tokens = []
			for word in text:
				token = sp(word)[0]
				
				if ( (( "@" in token.text) or token.is_space or token.is_stop  or  token.is_punct or token.like_num or  token.like_url or  token.is_oov )):  
					continue
				else:
					if(keyword_dict.get( token.text )):
						tokens.append(keyword_dict[token.text])
					else:
						tokens.append( token.lemma_)
			token_dict[id] = tokens
		except Exception as inst:
			error_file.write("ID %s Error %s " % ( id ,inst))
			continue
	return token_dict		 
	
def get_count(tweet_tokens): #υπολογίζει τον αριθμό των tweets στα οποία εμφανίζεται η κάθε λέξη 
	token_count = {}
	count = 0
	for tweet in tweet_tokens: #iter einai o arithmos twn tweets	
		try:
			count = count+1
			#print (count)
			counts = Counter(tweet_tokens[tweet]) # ftoakse dict me ton arithmo emfanisewn sto sygkekrimeno tweet
			seen = {}
			for token in tweet_tokens[tweet]:
				if (token not in keyword_dict):
					if (token in seen):
						continue
					if (token in token_count):
						token_count[token]+= counts[token]
					else:
						token_count[token] = counts[token]
					seen[token] = "yes"
				else:
					if (token in seen):
						continue
					if (keyword_dict[token] in token_count):
						token_count[keyword_dict[token]]+= counts[token]
					else:
						token_count[keyword_dict[token]]= counts[token]
					seen[token] = "yes"
		except Exception as inst:
			error_file.write("ID %s Error %s " % ( tweet ,inst))
			continue
	return token_count

missing_tokens = [] 

def heavy_tokens(doc_count,tweet_tokens):
	heavy_tokens_dict = collections.defaultdict()# einai dict of lists

	for tweet in tweet_tokens:
		buf_list = []
		for token in tweet_tokens[tweet]:
			if token in doc_count:
				if doc_count[token] >= 5:
					buf_list.append(token)
			else:
				missing_tokens.append(token)
		heavy_tokens_dict[tweet] = buf_list		
	return heavy_tokens_dict
	
def make_vec(dict,num): 
	vectors = defaultdict(list)
	vectors2 = np.array([])
	count = 0
	if(type(dict)==list): 
		for ngram in dict:
			try:
				split_gram = ngram[0].split()
				if(keyword_dict.get(split_gram[0])):
					new = sp(keyword_dict.get(split_gram[0]))
				else:
					new = sp(split_gram[0])
				if(keyword_dict.get(split_gram[1])):
					new2 = sp(keyword_dict.get(split_gram[1]))
				else:
					new2 = sp(split_gram[1])
				if(num==3):
					if(keyword_dict.get(split_gram[2])):
						new3 = sp(keyword_dict.get(split_gram[2]))
					else:
						new3 = sp(split_gram[2])
					vectors = np.vstack((new.vector,new2.vector,new3.vector) )	
				else:
					vectors = np.vstack((new.vector,new2.vector))#,new2.vector)		
				vectors2=np.vstack((vectors2,vectors)) if np.size(vectors2) else vectors
				count+=1
			except Exception as inst:
				print("error when making vectors of tokens , count is" + str(count))
				error_file.write("ID %s Error %s " % ( tweet ,inst))
				continue
		return vectors2		   
	else:
		for tweet in dict:
			try:
				count=count+1
				#print(count)
				for token in dict[tweet]:
					if(keyword_dict.get(token)):
						doc = sp(keyword_dict.get(token))
						vectors[tweet] = np.concatenate((vectors[tweet],doc.vector),axis=0)		
					else:
						doc = sp(token)
						vectors[tweet] = np.concatenate((vectors[tweet],doc.vector),axis=0)
			except Exception as inst:
				print("error when making vectors of tokens , count is" + str(count))
				error_file.write("ID %s Error %s " % ( tweet ,inst))
				continue
		return vectors

def f_tf_idf(token_dict,doc_count,doc_number):
	tf_idf = collections.defaultdict(dict)
	for tweet in token_dict:
		try:
			tweet_length = len(token_dict[tweet]) #posa tokens exei to kathe tweet
			buffer = [] #edw tha bazw to tfidf gia kathe token
			counts = Counter(token_dict[tweet])
			for token in counts:	
				if (token in keyword_dict):
					buffer.append( ( counts[token]/tweet_length )*math.log(doc_number/doc_count[keyword_dict[token]]) )
				else:
					if(token in doc_count):
						buffer.append( ( counts[token]/tweet_length )*math.log(doc_number/doc_count[token]) )
			tf_idf[tweet] = buffer
		except Exception as inst:
			#print(tweet)
			#error_file.write("ID %s Error %s " % ( tweet ,inst))
			continue
	return tf_idf
  
def find_county(tweet_id):# dexetai strings
	place = tweets.loc[tweets['id'] == tweet_id,"place"].iloc[0]
	split = place.split(',')
	try:
		if ('Περιφέρεια' in place ): # an den einai mono ellada
			my_index = 0
			for index in range(len(split)):
				if ("Περιφέρεια" in split[index]):
					my_index = index
					place  = split[my_index].replace("[","")
					place  = split[my_index].replace("]","")
					for item in counties:
						if item in place:
							place = item
					return place
	except Exception as inst:
		error_file.write("ID %s Error %s " % ( tweet_id ,inst))
		return ""
	return ""		
	
def get_dist(x):
	if (x == 'county'):
		for tweet_id in tweets['id']:
			county = find_county(tweet_id)
			if (county!=""):
				if not county in distribution['county']: #an de to exw ksanabalei bale to 
					distribution['county'][county] = 1
				else:	 #alliws auksise to
					distribution['county'][county] += 1
	if x == 'keyword':
		distribution['keyword'] = get_count(token_dict)
	if x == 'count_key':
		for id in token_dict:
			counts = Counter(token_dict[id])
			for token in counts:
				if(keyword_dict.get(strip_accents(token))):
					county = find_county(id)
					if (county!=""):
						if (keyword_dict.get(strip_accents(token)) in double_distribution[county]):
							double_distribution[county][keyword_dict[strip_accents(token)]]+=1
						else :
							double_distribution[county][keyword_dict[strip_accents(token)]] = 1
					   
def is_personal(token_dict):
	count = 0
	for key in token_dict:
		for token in token_dict[key]:
			if(keyword_dict.get(strip_accents(token))):
				if (keyword_dict.get(strip_accents(token))=='εγώ'):
					count +=  1
					break
	return count/len(token_dict)
			   

def write_to_csv(path,keys,place): # αυτες τις 2 φτιαχτες , περνα σαν παραμετρο τπτ αλλο γτ παιρνει μνημη
	number = 0
	myfile = open(path + "\\rest_data.csv", "w",encoding='utf8',newline='')	 
	w = csv.writer(myfile)
	w.writerow(['ID','Personal','County','Week','Temp','Max Temp','Min Temp','Rain','AWS','Max Wind'])
	meteo = get_weather_info(key,path) 
	w.writerow([key,is_personal(key),place,week,*meteo])	 
	print("wrote " + str(number))
	myfile.flush()	

def dict_to_numpy(dict,pad_length,heavy):
	#count = 0
	final = np.array([])
	if(pad_length == 96):# if not tfidf
		for key in dict:
			# if(heavy!=True):
				# if(len(dict[key])<20*pad_length): # 20 λεξεις Χ 96 
					# value = np.pad(dict[key],(0,20*pad_length-len(dict[key])),'mean')
					#count+=1
				# else: 
					# value = dict[key][0:20*pad_length]
					# value = np.pad(value,(0,2*pad_length))
			# else: # αν μιλαμε για το heavy tokens , κραταω 10 λεξεις
				# if(len(dict[key])<20*pad_length): # 20 λεξεις Χ 96 
					# value = np.pad(dict[key],(0,22*pad_length-len(dict[key])),'mean')
					#count+=1
				# else: 
					# value = dict[key][0:20*pad_length]
					# value = np.pad(value,(0,2*pad_length))
			value = dict[key]
			final = np.concatenate((final,value)) if np.size(final) else value
	else:	 
		for key in dict:
			# if(heavy!=True):
				# if(len(dict[key])<20):
					# value = np.pad(dict[key],(0,22-len(dict[key])),'mean')
					#count+=1
				# else: 
					# value = dict[key][0:20]
					# value = np.pad(value,(0,2))
			# else:
				# if(len(dict[key])<20):
					# value = np.pad(dict[key],(0,22-len(dict[key])),'mean')
					#count+=1
				# else: 
					# value = dict[key][0:20]
					# value = np.pad(value,(0,2))
			value = dict[key]
			final = np.concatenate((final,value)) if np.size(final) else value
	#print("Number padded is " , str(count))		
	return final

def weekly_norm_statistics(): #per week tfidf
	for year in range(2018,2020):				# Κάνουμε iteration στα directories 
		print("Starting with year " + str(year))
		for week in range(1,53):
			if(year==2010 and week<36):
				continue
			token_dict = collections.defaultdict()
			doc_count = collections.defaultdict()
			print("Starting with week " + str(week))
			
			dir = os.path.join(Years_directory,str(year),str(week))
			
			tweets = pd.read_csv(os.path.join(dir,"athens.csv"))	  # διαβασε τα συνολικα εβδομαδιαια της εκαστοτε περιφέρειας
			token_dict = get_tokens(tweets)
			#number of weekly document occurences of words 
			doc_number = len(token_dict)#number of weekly tweets
			for (key,tweet) in token_dict.items():
				seen = {}
				for token in tweet:
					if token not in keyword_dict:
						if token in seen:
							continue
						elif token in doc_count:
							doc_count[token] += 1
						else:
							doc_count[token] = 1
						seen[token] = 'yes'
					else:
						if token in seen:
							continue
						elif keyword_dict[token] in doc_count:
							doc_count[keyword_dict[token]] += 1
						else:
							doc_count[keyword_dict[token]] = 1
						seen[token] = 'yes'	

			save_obj(doc_count,os.path.join(Years_directory,str(year),str(week),'doc_count' ) )	
			save_obj(doc_number,os.path.join(Years_directory,str(year),str(week),'doc_number' ) )	
	
def weekly_norm_statistics2(): #all documents tfidf
	doc_count = collections.defaultdict()#number of weekly document occurences of words 
	doc_number = 0
	for year in range(2010,2020):				# Κάνουμε iteration στα directories 
		print("Starting with year " + str(year))
		for week in range(1,53):
			if(year==2010 and week<36):
				continue
			if(year==2019 and week==52):
				continue	
			dir = os.path.join(Years_directory,str(year),str(week))
			buf_count = load_obj(os.path.join(dir,'doc_count'))
			buf_number = load_obj(os.path.join(dir,'doc_number'))
			doc_number += buf_number
			for key in buf_count:
				if key in doc_count:
					doc_count[key] += buf_count[key]
				else:	
					doc_count[key] = buf_count[key]
			
	save_obj(doc_count,os.path.join(Years_directory,'doc_count' ) )	
	save_obj(doc_number,os.path.join(Years_directory,'doc_number' ) )	
		
def get_features(docs, max_length):
	Xs = np.zeros((len(docs), max_length),dtype='int32')
	for i, doc in enumerate(docs):
		for j, token in enumerate(doc[:max_length]):
			Xs[i, j] = clusters[sp(token)[0].rank-1] if sp(token)[0].has_vector else -1
	return Xs

def get_embeddings(vocab):
    max_rank = max(lex.rank for lex in vocab if lex.has_vector)
    vectors = np.ndarray((max_rank+1, vocab.vectors_length), dtype='float32')
    for lex in vocab:
        if lex.has_vector:
            vectors[lex.rank] = lex.vector
    return vectors

def old_token():
	#doc_count = load_obj(r'C:\Users\Administrator\Desktop\diplwmatikh giwrgos fragkozidhs\Training\Years\doc_count')	
	save_dir = Years_directory
	for year in range(2010,2020):
		print("Starting with year " + str(year))
		for week in range(1,53):
			if(year==2010 and week<36):	
				continue
			print("Starting with week " + str(week))
			token_dict = {}
			
			for county in counties:				# Κάνουμε iteration στα directories 
				print("Starting with county " + county)
				dir = os.path.join(County_directory,county,str(year),str(week))
				tweets = pd.read_csv(os.path.join(dir,"output.csv"))#,header=None)#,names=['date','username','id','text'])	  # διαβασε τα συνολικα εβδομαδιαια της εκαστοτε περιφέρειας
				
				token_dict.update(get_tokens(tweets))	 #tokenization
				#token_count = doc_count # counting
				#vector_dict = make_vec(token_dict,0) #make vectors
				
				#heavy_tokens_dict = heavy_tokens(doc_count,token_dict)
				save_obj(token_dict,os.path.join(save_dir,str(year),str(week),'tokens'))
				#heavy_vec = make_vec(heavy_tokens_dict,0)	
				#tf_idf = f_tf_idf(token_dict)	   #extract tf_idf
				#heavy_tf_idf = f_tf_idf(heavy_tokens_dict)
				#bigrams = generate_ngrams(heavy_tokens_dict,2)	 #generate_ngrams  
				#trigrams = generate_ngrams(heavy_tokens_dict,3)
				#bigrams_vec = make_vec(bigrams,2)
				#trigrams_vec = make_vec(trigrams,3)
				#df = pd.read_csv(meteo_dir+ "\\average.csv",index_col=0)	
				#info_row = get_weather_info(df,week) # βγαλε τοποθεσια και μετεωρολογικα,το path να ειναι το Counties 2 που εχει τα σωστα μετεο
				#myfile = open(dir + "\\rest_data.csv", "w",encoding='utf8',newline='')	
				#w = csv.writer(myfile)
				#w.writerow(['Week','Temp','Max Temp','Min Temp','Rain','AWS','Max Wind'])#Personal
				#w.writerow([*info_row])		#is_personal(token_dict),
				#myfile.flush()
				
				#############################################################
				#########all of these are to be used in normalization########
				#############################################################
				#df = pd.read_csv(dir+ "\\rest_data.csv")	
				#numpy_rest = df.drop(columns=['Week']).to_numpy().flatten()
				
				
				#vec = dict_to_numpy(vector_dict,96,False)
				#tf = dict_to_numpy(tf_idf,20,False)
				#heavy_vec = dict_to_numpy(heavy_vec,96,True)
				#heavy_tf_idf = dict_to_numpy(heavy_tf_idf,20,True)
				#np.save(dir+'\\Vectors.npy',vec)
				
				#np.save(dir+'\\Tf-Idf.npy',tf)
				
				#np.save(dir+'\\Heavy Vectors.npy',heavy_vec)
				#np.save(dir+'\\Heavy Tf-Idf.npy',heavy_tf_idf)
				
				#np.save(dir+'\\Bigrams.npy',bigrams_vec)
				#np.save(dir+'\\Trigrams.npy',trigrams_vec)
				#np.save(dir+'\\Rest.npy',numpy_rest)
			print("Saved ")
			#log.flush()	 
def new_token():
	for year in range(2010,2020):				# Κάνουμε iteration στα directories 
		print("Starting with year " + str(year))
		for  week in range(1,53):# in range(2010,2020):
			if(year==2010 and week<36):
				continue
			print("Starting with week " + str(week))
			dist = []
			dir = os.path.join(Years_directory,str(year),str(week))
			token_dict = collections.defaultdict()
			tweets = pd.read_csv(os.path.join(dir,"athens.csv"))	  # διαβασε τα συνολικα εβδομαδιαια της εκαστοτε περιφέρειας
			buf  = get_tokens(tweets)
			token_dict.update(buf)
			save_dir = os.path.join(Years_directory,str(year),str(week))
			doc_count = load_obj(os.path.join(save_dir,'doc_count'))
			#heavy_tokens_dict = heavy_tokens(doc_count,token_dict)	
			#bigrams = generate_ngrams(heavy_tokens_dict,2)	 #generate_ngrams  
			#trigrams = generate_ngrams(heavy_tokens_dict,3)
			#cluster_list = []	
			token_list = []
			#final_list = []
			#final_token_list=[]
			
			for id in token_dict:
				#print(id)
				for token in token_dict[id]:
					#print(token)
					if (sp(token)[0].has_vector):
			#			cluster_list.append(clusters[sp(token)[0].rank]+1) 
						token_list.append(token) 
				#print(cluster_list)			
				final_list.append(cluster_list)
				final_token_list.append(token_list)
				cluster_list=[]
				token_list = []
				
			
			save_obj(final_list,os.path.join(save_dir,'cluster_list'))
			#save_obj(bigram_list,os.path.join(save_dir,'bigram_list'))
		
			print("Saved ")

def calc_tfidf(year):
	for year in range(year,year+1):				# Κάνουμε iteration στα directories 
		print("Starting with year " + str(year))
		for  week in range(1,53):# in range(2010,2020):
			#if (week>10):	
			#	continue
			print("Starting with week and year" + str(week)+str(year))
			dir1 = os.path.join(Training_Directory,str(year),str(week))
			dist = []
			token_dict = collections.defaultdict()
			doc_count = load_obj(os.path.join(dir1,'doc_count'))
			doc_number = load_obj(os.path.join(dir1,'doc_number'))
			token_dict = collections.defaultdict()
			#for county in counties:#week in range(1,53):
			#	print("Starting with county " + county)
			#	dir = os.path.join(Tweet_Directory,county,str(year),str(week))
			#	#meteo_dir = os.path.join(Meteo_Directory,geo_map[county],str(year),str(week)) # αυτό το path θα κοιταω για να βλεπω αν υπαρχουν μετεωρολογικα δεδομενα εκεινη τη βδομαδα)
			#	if(path.exists(os.path.join(dir,"output.csv"))!=True):# or path.exists(os.path.join(meteo_dir,"average.csv"))!=True): #αν δεν υπαρχει το αρχειο αυτο, πχ γτ μια περιφερεια δεν ειχε ολες τις βδομαδες
			#		continue
			tweets = pd.read_csv(os.path.join(dir1,"athens.csv"))	  # διαβασε τα συνολικα εβδομαδιαια της εκαστοτε περιφέρειας
			if(tweets.empty): # αν δεν εχει τπτ εκεινη τη βδομαδα συνεχισε
				continue
			buf  = get_tokens(tweets)
			token_dict.update(buf)
			
			tf_idf = f_tf_idf(token_dict,doc_count,doc_number)
			buf = np.array([])
			try:
				for tweet in tf_idf:
					if np.shape(tf_idf[tweet])[0]<15:
						tf_idf[tweet] =np.pad(tf_idf[tweet],(15-np.shape(tf_idf[tweet])[0],0))#is less words than weekly words , then pad
					else:
						tf_idf[tweet] = tf_idf[tweet][0:15]
					buf = np.vstack((buf,tf_idf[tweet])) if np.size(buf) else tf_idf[tweet]
				save_obj(buf,os.path.join(dir1,'tf_idf'))
			except Exception as inst:
				print(inst)



labels = load_obj(os.path.join(Training_Directory,'spectral_labels_words'))
for word_string in keywords:
	word_list = word_string.split(",")
	for word in word_list:
		keyword_dict[word] = word_list[0]

for word_string in new_keywords:
	word_list = word_string.split(",")
	for word in word_list:
		new_keyword_dict[word] = word_list[0]		

for w in stop_words:
	sp.vocab[w].is_stop = True	
count = 0

		

#def average_tokens(year):
def label_tweets(year,week):
	weekly_count=0
	id_list = []
	if(week>52):
		week=1
		year+=1
	if(year==2019 and week==52):
		return 0		
	print(year)
	print(week)	
	dir = os.path.join(Training_Directory,str(year),str(week))
	tweets = load_obj(os.path.join(dir,'tokens'))
	
	for id,tweet in tweets.items():
		for token in tweet:
			if token in keyword_dict.keys():
				weekly_count+=1
				print(token)
				id_list.append(id)
				break
	print(weekly_count)			
	save_obj(weekly_count,os.path.join(dir,'health_related_tweets_percentage'))			
	save_obj(id_list,os.path.join(dir,'health_ids'))			
	return label_tweets(year,week+1)

def plot_percent():
	x = []
	for year in range(2010,2020):
		for week in range(1,53):
			if(year==2010 and week<36):
				continue
			if(year==2019 and week==52):
				continue	
			dir = os.path.join(Training_Directory,str(year),str(week))	
			tweets = load_obj(os.path.join(dir,'tokens'))
			y = load_obj(os.path.join(dir,'health_related_tweets_percentage'))			
			z = load_obj(os.path.join(dir,'health_ids'))			
			for id in z:
				print(tweets[id])
			x.append(y)
	
	f = open(r'health_tweets_total.txt','w+')
	f.write("Health Tweets,Gritot"+"\n")
	sent = pd.read_csv(r'Sentinel.csv')
	count = 0
	for el in x :
		f.write(str(el)+"," +str(sent["gritot"].iloc[count])+'\n')
		count+=1
	plt.plot(x)
	plt.show(x)


def split_sentinel():
	vec = np.load("C:\\Users\\Administrator\\Desktop\\diplwmatikh giwrgos fragkozidhs\\Training\\Sentinel.npy")
	count = 0
	min = 0
	max = 0
	for year in range(2010,2020):
		for week in range(1,53):
			print("this week"+str(week))
			try:
				weekly = vec[count] # thn tetarth sthlh, mporw na to allaksw)
				print("saving week number " + str(vec[count]))
				np.save("C:\\Users\\Administrator\\Desktop\\diplwmatikh giwrgos fragkozidhs\\Training\\Years\\"+str(year)+"\\" + str(week)+"\\Sentinel1.npy",weekly)			  
				count+=1
			except Exception as inst:
				count+=1
				print(inst)
				continue

def split_ILI():

	vec = np.load("C:\\Users\\Administrator\\Desktop\\diplwmatikh giwrgos fragkozidhs\\Training\\ILI.npy")
	count = 0
	min = 0
	max = 0
	for year in range(2010,2020):
		for week in range(1,53):
			print("this week"+str(week))
			try:
				weekly = vec[count] # thn tetarth sthlh, mporw na to allaksw)
				print("saving week number " + str(vec[count]))
				np.save("C:\\Users\\Administrator\\Desktop\\diplwmatikh giwrgos fragkozidhs\\Training\\Years\\"+str(year)+"\\" + str(week)+"\\ILI.npy",weekly)			  
				count+=1
			except Exception as inst:
				count+=1
				print(inst)

    
    

path= r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years'

x = []
for year in range(2010,2020):
    for week in range(1,53):
        buf = np.load(os.path.join(path,str(year),str(week),'Sentinel.npy'))
        x = np.vstack((x,buf)) if np.size(x) else buf