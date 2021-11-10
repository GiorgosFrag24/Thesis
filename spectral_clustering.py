import scipy.spatial.distance as f
import os
import matplotlib.pyplot as plt
import numpy as np
import spacy

from sklearn.cluster import SpectralClustering
import sys
import Data_Functions as utils
new_keywords = read_keywords

sp = spacy.load('el_core_news_md')

def Create_Label():
    embeddings = sp.vocab.vectors.data
    similarity = abs( 1 - f.squareform( f.pdist( embeddings, metric='cosine') ) )
    clustering = SpectralClustering(assign_labels = "discretize", affinity='precomputed').fit(similarity)
    utils.save_obj( clustering.labels_,os.path.join( dir,'SpectralClustering-Labels') )
    labels = clustering.labels_
    return labels
    

def cluster_tokens():   
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
    




