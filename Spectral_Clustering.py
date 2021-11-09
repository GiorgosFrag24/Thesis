import scipy.spatial.distance as f
import os
import matplotlib.pyplot as plt
import numpy as np
import spacy
from wordcloud import WordCloud
from sklearn.cluster import SpectralClustering


sp = spacy.load('el_core_news_md')

def Create_Label():
    embeddings = sp.vocab.vectors.data
    similarity = abs( 1 - f.squareform( f.pdist( embeddings, metric='cosine') ) )
    clustering = SpectralClustering(assign_labels = "discretize", affinity='precomputed').fit(similarity)
    utils.save_obj( clustering.labels_,os.path.join( dir,'SpectralClustering-Labels') )
    labels = clustering.labels_
    return labels


def cluster_tokens():   
    labels = Create_Label()
    for year in range(2010,2020):               
        print("Starting with year " + str(year))
        for  week in range(1,53):
            weekly = np.zeros(30) # padding 
            dir1 = os.path.join(Training_Directory,str(year),str(week))
            x = utils.load_obj(os.path.join(dir1,'tokens'))
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
    return 0  

