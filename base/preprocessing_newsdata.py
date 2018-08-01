import spacy
import datetime

STOPLIST = ["'", '"', ',', "’", '-']
nlp = spacy.load('en')
processed_time = []
first_processed_words = []


def wash_word(word):
    sword = str(word)
    for c in STOPLIST:
        while c in sword:
            if sword.index(c) == 0: sword = sword[1:]
            else:
                if sword.index(c) == len(sword) - 1: sword = sword[0:-1]
                else:
                    sword = sword[0:sword.index(c)] + sword[sword.index(c)+1:]
    word = nlp(sword)
    for token in word:
        if str(token).isalpha() and len(token)>2:
            return token.lemma_
    return None


def preprocessing_newsdata(titles, update_time, mode):
    first_processed_words = []
    processed_time = []
    for title in titles:
        data = nlp(title)
        first_processed_words.append([wash_word(token) for token in data if not token.is_stop and not token.is_punct and wash_word(token)!=None])
        print(first_processed_words[-1])
    if mode == 0:
        for time_element in update_time:
            processed_time.append(datetime.datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S+00:00').timestamp())
    if mode == 1:
        for time_element in update_time:
            processed_time.append( datetime.datetime.strptime(time_element, '%B %d, %Y %H:%M').timestamp())
    if mode == 2:
        processed_time = update_time

    return first_processed_words, processed_time