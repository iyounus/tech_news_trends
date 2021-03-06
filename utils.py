from nltk import WordNetLemmatizer, word_tokenize

def stop_words():
    '''
    INPUT None
    OUTPUT list
    '''
    with open('stop_words.txt', 'r') as f:
        stop = [line.strip() for line in f]
    return stop


def tokenize(article):
    '''
    INPUT string
    OUTPUT list

    This is a tokenizer to replace the default tokenizer in TfidfVectorizer
    '''
    stop = stop_words()
    tokens = [word.lower() for word in word_tokenize(article)]

    # lemmatize
    lmtzr = WordNetLemmatizer()
    tokens = [lmtzr.lemmatize(word) for word in tokens]

    # now remove stop words
    tokens = [word for word in tokens if word not in stop]

    # remove words less than three letters
    tokens = [word for word in tokens if len(word) >= 3]

    return tokens

