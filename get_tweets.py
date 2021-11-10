import scipy.spatial.distance as f
import os
import matplotlib.pyplot as plt
import numpy as np
import spacy
from wordcloud import WordCloud
from sklearn.cluster import SpectralClustering

import sys
sys.path.insert(1, r'C:\Users\skote\Desktop\Twitter Files\CODE') # insert at 1, 0 is the script path (or '' in REPL)
import Data_Functions as utils
new_keywords = ['βήχας','βήχω','βήχεις','βήχει','βήχουμε','βήχετε','βήχουν','βήξω','βήξεις','βήξει','βηχω','βηχεις','βηχει','βηχουμε','βηχετε','βηχουν','βηξω','βηξεις','βηξει','βηξουμε','βηξετε','βηξουν','εβηξα','εβηξες','εβηξε','βηξαμε','βηξατε','εβηξαν'\
            ,'βηχας','βηχα','βήξουμε','βήξετε','βήξουν','έβηξα','έβηξες','έβηξε','βήξαμε','βήξατε','έβηξαν','βήχας','βήχα',\
            'γρίπη','γριπη','γριπης','γρίπη','γρίπης',\
            'Η1Ν1','h1n1','η1ν1',\
            'πόνος','πόνου','πόνοι','πονάω','πονάς','πονάει','πονάμε','πονάτε','πονάνε','πονούν',\
            'ιός','ιού','ιοί','ιος','ίωση','ιωση','ιωσης','ίωσης','ιώσεως','ιώσεων','ιωσεων','ιώσεις','ιωσεις',\
            'γαστρεντερίτιδα','γαστρεντερίτιδας','γαστρεντεριτιδα','γαστρεντερίτιδες','γαστρεντεριτιδες','γαστρεντεριτιδα',\
            'ωτίτιδα','ωτίτιδας',\
            'αντιβίωση','αντιβίωσης','αντιβιώσεων','αντιβιώσεις','αντιβιωση','αντιβιωσης','αντιβιωσεων','αντιβιωσεις',
            'ασπιρίνη','ασπιρίνες','ασπιρίνης','ασπιρινη','ασπιρινες','ασπιρινης',\
            'άσθμα','άσθματος','άσθματα','ασθμα','ασθματος','ασθματα',\
            'κρύωμα','κρυώματος','κρυολόγημα','κρυολογήματος','κρυωμα','κρυωματος','κρυολογημα','κρυολογηματος',\
            'διάρροια','διάρροιας','διαρροια','διαρροιας',\
            'ζαλάδα','ζαλάδας','ζαλαδα','ζαλαδας',\
            'φάρμακο','φάρμακα','φαρμάκων','φάρμακου','φαρμακο','φαρμακα','φαρμακων','φαρμακου',\
            'ημικρανία','ημικρανίας','ημικρανιών','ημικρανίες','ημικρανια','ημικρανιας','ημικρανιων','ημικρανιες',\
            'ναυτία','ναυτίες','ναυτιών','ναυτια','ναυτιες','ναυτιων',\
            'παυσίπονα','παυσίπονο','παυσίπονου','παυσίπονων','παυσίπονα','παυσιπονο','παυσιπονου','παυσιπονων',\
            'panadol','παναντόλ','παναντολ',\
            'παρακεταμόλη','παρακεταμόλης','παρακεταμολη','παρακεταμολης',\
            'χάπι','χάπια','χαπιού','χαπιών','χαπι','χαπια','χαπιου','χαπιων',\
            'αναρρώνω','ανάρρωση','ανάρρωσης','αναρρώνεις','αναρρώνει','αναρρώνουμε','αναρρώνετε','αναρρώνουν','αναρρωνω','αναρρωση','αναρρωσης','αναρρωνεις','αναρρωνει','αναρρωνουμε','αναρρωνετε','αναρρωνουν',\
            'αναπνευστικός','αναπνευστικό','αναπνευστικά','αναπνευστικών','αναπνευστικού','αναπνευστικος','αναπνευστικο','αναπνευστικα','αναπνευστικων','αναπνευστικου',\
            'φτάρνισμα','φταρνίζομαι','φταρνίζεσαι','φταρνίζεται','φτέρνισμα','φτερνίζομαι','φτερνίζεσαι','φτερνίζεται','φταρνισμα','φταρνιζομαι','φταρνιζεσαι','φταρνιζεται','φτερνισμα','φτερνιζομαι','φτερνιζεσαι','φτερνιζεται',\
            'στομαχόπονος','στομαχόπονοι','στομαχόπονου','στομαχόπονων','στομαχοπονος','στομαχοπονοι','στομαχοπονου','στομαχοπονων',\
            'συμπτώματα','συμπτωμάτων','σύμπτωμα','συμπτώματος','συμπτωματα','συμπτωματων','συμπτωμα','συμπτωματος',\
            'πονόλαιμος','πονόλαιμου','πονόλαιμοι','πονολαιμος','πονολαιμου','πονολαιμοι',\
            'εμβόλιο','εμβόλια','εμβολίων','εμβολίου','εμβολιο','εμβολια','εμβολιων','εμβολιου',\
            'πυρετός','πυρετος','πυρετο','πυρετου','πυρετών','πυρετοί','πυρετός','πυρετό','πυρετού','πυρετών','πυρετοί',\
            'άρρωστος','αρρωστος','αρρωστη','αρρωστο','αρρωστα','αρρωστοι','αρρωστια','αρρωστιες','αρρωστες','αρρωστησα','αρρωστησες','αρρωστησε','αρρωστησαμε','αρρωστησατε','αρρωστησαν','αρρωστου','αρρωστης','αρρωστου','αρρωστων', 'άρρωστος','άρρωστη','άρρωστο','άρρωστα','άρρωστοι','αρρώστια','αρρώστιες','άρρωστες','αρρώστησα','αρρώστησες','αρρώστησε','αρρωστήσαμε','αρρωστήσατε','αρρώστησαν','άρρωστου','άρρωστης','άρρωστου','άρρωστων',\
            'ντεπόν','ντεπον','ντεπόν',\
            'πονόλαιμος','πονολαιμος','πονολαιμοι','πονολαιμο','πονολαιμου','πονολαιμων','πονόλαιμος','πονόλαιμοι','πονόλαιμο','πονόλαιμου','πονόλαιμων',\
            'πονοκέφαλος','πονοκεφαλος','πονοκεφαλοι','πονοκεφαλο','πονοκεφαλου','πονοκεφαλων','πονοκέφαλος','πονοκέφαλοι','πονοκέφαλο','πονοκέφαλου','πονοκέφαλων',\
            'ρίγος','ριγος','ριγη','ριγους','ριγων','ρίγος','ρίγη','ρίγους','ριγών',\
            'αντιβίωση','αντιβιωση','αντιβιωσης','αντιβιωσεις','αντιβιωσεων','αντιβίωση','αντιβίωσης','αντιβιώσεις','αντιβιώσεων']
dir = r'C:\Users\skote\Desktop\Twitter Files\DATA'
Training_Directory = r'C:\Users\skote\Desktop\OLD\twitter_files\Training\Years'
sp = spacy.load('el_core_news_md')

def Create_Label():
    embeddings = sp.vocab.vectors.data
    similarity = abs( 1 - f.squareform( f.pdist( embeddings, metric='cosine') ) )
    clustering = SpectralClustering(assign_labels = "discretize", affinity='precomputed').fit(similarity)
    utils.save_obj( clustering.labels_,os.path.join( dir,'SpectralClustering-Labels') )
    labels = clustering.labels_
    return labels
    
def get_wordcloud(year,week,cluster):
    raw = load_obj(os.path.join(Training_Directory,str(year),str(week),'tokens'))
    text = " ".join(word for tweet in raw for word in raw[tweet] if ( not sp(word)[0].is_oov) and (labels[sp(word)[0].rank] == cluster))
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()    
def normalize():
    max = 0
    min = 0
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(Training_Directory,str(year),str(week))
            x = np.load(os.path.join(dir1,'number_of_tweets_by_county.npy'))
            if np.amax(x)>=max:
                max = np.amax(x)
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020): 
            dir1 = os.path.join(Training_Directory,str(year),str(week))
            x = np.load(os.path.join(dir1,'number_of_tweets_by_county.npy'))
            norm = 2*(x-min)/(max) -1
            np.save(os.path.join(dir1,'number_of_tweets_by_county.npy'),x)
def new_cluster_tokens():   
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020):
            weekly = np.zeros(30)
            dir1 = os.path.join(Training_Directory,str(year),str(week))
            try:
                x = utils.load_obj(os.path.join(dir1,'tokens'))
            except:
                continue
            for tweet in x :
                personal = 0
                for i in range(0,len(x[tweet])):
                    token = x[tweet][i]
                    try:
                        if token in new_keywords:   
                            weekly[labels[sp(token)[0].rank]]+=1
                    except:
                        #print(token)
                        continue
            utils.save_obj(weekly,os.path.join(dir1,'SC_health_tokens'))
            print(weekly)
    return 0  

def keyword_tokens():   
    for year in range(2010,2020):               # Κάνουμε iteration στα directories 
        print("Starting with year " + str(year))
        for  week in range(1,53):# in range(2010,2020):
            weekly = np.zeros(324)
            dir1 = os.path.join(Training_Directory,str(year),str(week))
            try:
                x = utils.load_obj(os.path.join(dir1,'tokens'))
            except:
                continue
            for tweet in x :
                personal = 0
                for i in range(0,len(x[tweet])):
                    token = x[tweet][i]
                    try:
                        if token in new_keywords:   
                            weekly[new_keywords.index(token)]+=1
                    except:
                        #print(token)
                        continue
            utils.save_obj(weekly,os.path.join(dir1,'keywords'))
            print(weekly)
    return 0        
    




