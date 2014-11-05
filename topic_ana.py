import numpy as np
import pandas as pd
import pickle as pkl

from pymongo import MongoClient
from pymongo import errors

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF

from nltk import WordNetLemmatizer, sent_tokenize, word_tokenize
from nltk.corpus import stopwords


pkl_file = "data/nyt_data.pkl"

def read_mongo():
    '''
    INPUT None
    OUPUT DataFrame

    This function reads mongodb for NYT articles, and creates dataframe
    for some columns
    '''

    # connect to db
    client = MongoClient()
    db = client.nyt_tech
    collection = db.articles

    columns = ['content','document_type','web_url','headline', \
               'abstract','section_name', 'subsection_name','pub_date']

    dict = {}
    for col in columns:
        dict[col] = []

    for article in collection.find({'content' : {'$exists' : True}}):
        # this is temporary
        if not '2014' in article['pub_date']:
            continue

        for col in columns:
            if col == 'headline': # headline is a dict
                dict[col].append(article[col]['main'])
            else:
                dict[col].append(article[col])

    return pd.DataFrame(dict)


def read_pickle():
    '''
    INPUT None
    OUTPUT DataFrame

    returns dataframe obtained from pickle file
    '''
    return pkl.load( open(pkl_file, "rb") )


def featurize(article):
    '''
    INPUT string
    OUTPUT list

    This is a tokenizer to replace the default tokenizer in TfidfVectorizer
    '''

    # tokenize into words
    tokens = [word for sent in sent_tokenize(article) \
              for word in word_tokenize(sent)]

    # remove stopwords
    stop = stopwords.words('english')
    stop.append('said') # some extra stop words not present in stopwords
    tokens = [token for token in tokens if token not in stop]

    # remove words less than three letters
    tokens = [word for word in tokens if len(word) >= 3]

    # lower capitalization
    tokens = [word.lower() for word in tokens]

    # lemmatize
    lmtzr = WordNetLemmatizer()
    tokens = [lmtzr.lemmatize(word) for word in tokens]

    return tokens



if __name__ == '__main__':
    
    # to save pickle of dataframe
    # df = read_mongo()
    # pkl.dump(df, open(pkl_file, "wb"))

    n_features = 5000
    n_topics = 10

    df = read_pickle()
    print "number of articles in dataframe: ", df.shape[0]

    vectorizer = TfidfVectorizer(tokenizer=featurize, max_features=n_features)
    vectors = vectorizer.fit_transform(df.content).toarray()

    nmf = NMF(n_components=n_topics, random_state=1).fit(vectors)

    # save the vertorizer and model to be analyzed later
    print "Writing: ", "data/vectorizer.pkl"
    print "Writing: ", "data/nmf.pkl"
    pkl.dump( vectorizer, open("data/vectorizer.pkl", "wb"))
    pkl.dump( nmf, open("data/nmf.pkl", "wb"))
