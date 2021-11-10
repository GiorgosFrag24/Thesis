from wordcloud import WordCloud

def get_wordcloud(year,week,cluster):
    raw = load_obj(os.path.join(Training_Directory,str(year),str(week),'tokens'))
    text = " ".join(word for tweet in raw for word in raw[tweet] if ( not sp(word)[0].is_oov) and (labels[sp(word)[0].rank] == cluster))
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()    