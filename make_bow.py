"""Creates a bag of word representation, tfidf representation,
and a bigram bag of word representation. Saves to the data/02_models folder"""
import pandas as pd
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import pickle
import os

twitter = pd.read_csv('data/twitter/twitter_data_cleaned.csv')
reddit = pd.read_csv('data/reddit/reddit_comments_cleaned.csv')

def create_bow(text, name='twitter'):
    wpt = WordPunctTokenizer()
    ps = PorterStemmer()
    text = text.str.lower()
    tokens = text.apply(lambda x: wpt.tokenize(x))
    tokens = tokens.apply(lambda x: [ps.stem(word) for word in x if word not in stopwords.words('english')])

    def fake_tokenizer(x):
        return x

    cv = CountVectorizer(tokenizer=fake_tokenizer, lowercase=False)
    bow_model = cv.fit_transform(tokens)
    bow_vocab = cv.vocabulary_

    if not os.path.exists('data/02_models'):
        os.mkdir('data/02_models')

    with open(f'data/02_models/bow_matrix_{name}.pickle', 'wb') as f:
        pickle.dump(bow_model, f)
    with open(f'data/02_models/bow_vocab_dict_{name}.pickle', 'wb') as f:
        pickle.dump(bow_vocab, f)

    tfidf = TfidfVectorizer(tokenizer=fake_tokenizer, lowercase=False)
    tfidf_model = tfidf.fit_transform(tokens)
    tfidf_vocab = tfidf.vocabulary_

    with open(f'data/02_models/tfidf_matrix_{name}.pickle', 'wb') as f:
        pickle.dump(tfidf_model, f)
    with open(f'data/02_models/tfidf_vocab_dict_{name}.pickle', 'wb') as f:
        pickle.dump(tfidf_vocab, f)

    bigram = CountVectorizer(tokenizer=fake_tokenizer, ngram_range=(1,2), lowercase=False)
    bigram_model = bigram.fit_transform(tokens)
    bigram_vocab = bigram.vocabulary_

    with open(f'data/02_models/bigram_matrix_{name}.pickle', 'wb') as f:
        pickle.dump(bigram_model, f)
    with open(f'data/02_models/bigram_vocab_dict_{name}.pickle', 'wb') as f:
        pickle.dump(bigram_vocab, f)

create_bow(twitter['full_text'])




