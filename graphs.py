import unicodedata
import pandas as pd
import math 
import os
import collections
import random
import numpy as np
import sys
import math
import statistics
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
from collections import defaultdict
import pickle
import sys
import matplotlib.patches as mpatches
from matplotlib import style

plt.style.use('fivethirtyeight')
Training_Directory = r'C:\Users\skote\Desktop\Years'
keywords = r'βήχας,άρρωστος,γρίπη,Η1Ν1,πόνος,ιός,ίωση,γαστρεντερίτιδα,ωτίτιδα,αντιβίωση,ασπιρίνη,άσθμα,κρύωμα,διάρροια,ζαλάδα,φάρμακο,ημικρανία,ναυτία,παυσίπονο,panadol,παρακεταμόλη,χάπι,αναρρώνω,αναπνευστικό,φτάρνισμα,στομαχόπονος,σύμπτωμα,πονόλαιμος,εμβόλιο,πυρετός,άρρωστος,ντεπόν,πονοκέφαλος,ρίγος,αντιβίωση,εγώ'
translated_keywords = r'cough, sick, flu, H1N1, pain, virus, viral infection, gastroenteritis, otitis, antibiotic, aspirin, asthma, cold, diarrhea, dizziness, medication, migraine, nausea, painkiller, panadol, paracetamol, pill, recover, respiratory, sneezing, stomachache, symptom, sore throat, vaccine, fever, sick, painkiller, headache, chills, antibiotic, i'
trans_dict = {keywords.split(',')[i]:translated_keywords.split(',')[i] for i in range(len(keywords.split(',')))   }


def denorm(array):
    denorm  = lambda x: int(round(( (x+1)*(3214-2)/2) +2))
    vectorized_norm = np.vectorize(denorm)
    return vectorized_norm(array)


def keyword_freq():
    keyword_dict = {}
    for year in range(2010,2020):
        keyword_dict[year] = {}
        for word in keywords.split(','):
                keyword_dict[year][word]=52*[0]
        for week in range(1,53):
            raw = np.load(os.path.join(Training_Directory,str(year),str(week),'tokens.pkl'),allow_pickle=True)
            for tweet in raw:
                for word in raw[tweet]:
                    if word in keywords.split(','):
                        keyword_dict[year][word][week-1]+=1
                        break
    return keyword_dict


def tweet_freq():
    cont = []
    direct = r'C:\Users\skote\Desktop\Years' 
    for year in range(2010,2020):
        for week in range(1,53):
            path = os.path.join(direct,str(year),str(week),'number_of_tweets_by_county.npy')
            x = np.sum(np.load(path))
            cont.append(x)
    return cont


def weekly_avg(input):
    buf = []
    x = 0
    for i in range(520*7):
        x+=input[i]
        if i%7==0:
            buf.append(x/7)
            x = 0
    return buf 


def meteo_feats():
    dict = {'Αθήνα':{},'Ηράκλειο':{},'Θεσσαλία':{},'Θεσσαλονίκη':{}}
    feats = ['T2M_MAX','T2M_MIN','T2M','PRECTOTCORR','RH2M','PS']
    for feat in feats:
        for key in dict.keys():
            dict[key][feat]=[]
            input = pd.read_csv(os.path.join(r'C:\Users\skote\Desktop\Years',key+'.csv'))
            week =  weekly_avg(input[feat].values)
            dict[key][feat] = week 
    return dict        


def compare_keys_cases(Reference_Year):
    # Create some mock data
    
    year = Reference_Year
    t = np.arange(1, 53, 1)
    fig, ax2 = plt.subplots()
      # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Keyword Frequency', color=color)  # we already handled the x-label with ax1
    sorted_keys = [k for k,_ in sorted(Keyword_Freq[year].items(), key=lambda item: sum(item[1]))] [-5:] 
    bottom = 52*[0]
    pops = []
    colors = ['mediumblue','darkmagenta','darkgreen','crimson','gold']
    sorted_keys = list(zip(sorted_keys,colors))
    for key in sorted_keys:
        ax2.bar(t, Keyword_Freq[year][key[0]] ,bottom = bottom, alpha=1, color=key[1])
        bottom = np.add(Keyword_Freq[year][key[0]],bottom)
        pops.append(mpatches.Patch(color=key[1], label=trans_dict[key[0]]))
    pops.append(mpatches.Patch(color='red', label='ILI Cases'))
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(False)
    
    ax1 = ax2.twinx()
    color = 'tab:red'
    ax1.set_xlabel('Weeks')
    ax1.set_ylabel('Number of ILI Cases', color=color)
    ax1.plot(t, Cases[(year%2010)*52:((year+1)%2010)*52],linewidth=1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.legend(handles=pops, loc='upper right',fontsize='xx-small') 
    plt.savefig(os.path.join((r'C:\Users\skote\Desktop'),str(year)+'.png'))
    #plt.show()
    return


def plot_meteo_feats(County,Reference_Year):
    index = Reference_Year
    values = meteo_feats()
    
    feats = {'T2M_MAX':'Maximum Temperature - Celsius','T2M_MIN':'Minimum Temperature - Celsius',
    'T2M':'Mean Temperature - Celsius','PRECTOTCORR': 'Precipitation - Cm','RH2M':'Relative Humidity',
    'PS': 'Surface Pressure'}
    for key in values[County].keys():
        fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.plot(values[County][key][(index%2010)*52:((index+1)%2010)*52])
        ax1.set_xlabel('Weeks')
        ax1.set_ylabel(feats[key], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        plt.show()


def merge_images():
    from PIL import Image
    import os
    #Read the two images
    path = r'C:\Users\skote\Desktop\plots'
    for year in range(2010,2020):
        for week in range(1,4):
            new_image = Image.new('RGB',(4*500, 480), (250,250,250))
            count = 0
            for model in ['M','H','MH','MTH']:
                image = Image.open(os.path.join(path,model+'_'+str(week)+'_'+str(year)+'.png'))
                image = image.resize((500, 480))    
                new_image.paste(image,(count*image.size[0],0))
                count+=1
            result_dir = os.path.join(path,str(year))
            if os.path.exists(result_dir)==False:
                os.mkdir(result_dir)
            new_image.save(os.path.join(result_dir,'Advanced Models '+str(week)+' week ahead.png'),"JPEG")  


Health_Info = np.load(r'C:\Users\skote\Desktop\New Method\total.npy')
Cases = denorm(np.load(r'C:\Users\skote\Desktop\New Method\HEALTH_DATA.npy')).ravel()[1:-1]
Cases_per_Visit = Health_Info[:,0] 
Visits = Health_Info[:,1]
Tweet_Freq = tweet_freq()
Keyword_Freq = keyword_freq()
Meteo_Feats = meteo_feats()

print("Input the Reference_Year")
Reference_Year = int(input())
r = list(range(2011,Reference_Year))
#print("Input the County")
#County = input()

#plot_meteo_feats(County,Reference_Year)
for year in r:
    compare_keys_cases(year)

