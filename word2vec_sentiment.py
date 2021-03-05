import pandas as pd
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec
from sklearn.cluster import KMeans
import numpy as np
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os

def textblob_sim(text, name='twitter'):
    ps = PorterStemmer()
    wpt = nltk.tokenize.WordPunctTokenizer()
    tokenized_tweets = text.apply(lambda x: wpt.tokenize(x))
    tokenized_tweets = tokenized_tweets.apply(lambda x: [ps.stem(word) for word in x if word not in stopwords.words('english')])
    cleaned_tweets = tokenized_tweets.apply(lambda x: ' '.join(x))
    sentiment = cleaned_tweets.apply(lambda x: TextBlob(x).sentiment)
    polarity = sentiment.apply(lambda x: x[0])
    subjectivity = sentiment.apply(lambda x: x[1])
    return_df = pd.DataFrame({'tweet': text, 'polarity': polarity, 'subjectivity': subjectivity})
    if not os.path.exists('data/02_models'):
        os.mkdir('data/02_models')
    return_df.to_csv(f'data/02_models/textblob_sentiment_{name}.csv', index=False)

def create_embedding(text, name='twitter', pretrained=False):
    wpt = nltk.tokenize.WordPunctTokenizer()
    ps = PorterStemmer()
    tokenized_tweets = text.apply(lambda x: wpt.tokenize(x))
    tokenized_tweets = tokenized_tweets.apply(lambda x: [ps.stem(word) for word in x if word not in stopwords.words('english')])
    print(tokenized_tweets)
    if pretrained:
        vectors = KeyedVectors.load_word2vec_format('data/00_raw/w2v.twitter.27B.200d.txt', binary=False)
        w2v_model = Word2Vec(size=200, min_count=1, sg=1)
        w2v_model.build_vocab([list(vectors.vocab.keys())])
        w2v_model.train(tokenized_tweets, total_examples=tokenized_tweets.shape[0], epochs=10)
    else:
        w2v_model = Word2Vec(sentences=tokenized_tweets, size=200, min_count=2, sg=1)
    if not os.path.exists('data/02_models'):
        os.mkdir('data/02_models')
    w2v_model.save(f'data/02_models/w2v_{name}.model')

def create_clusters(vector_path, n=2, name='twitter'):
    word_vectors = Word2Vec.load(vector_path).wv
    print(word_vectors.vectors)
    model = KMeans(n_clusters=n, random_state=123).fit(word_vectors.vectors.astype('double'))
    for vector in model.cluster_centers_:
        print(vector)
        print(word_vectors.most_similar(positive=[vector], topn=10))
    words = pd.DataFrame(word_vectors.vocab.keys())
    words.columns = ['words']
    words['vectors'] = words.words.apply(lambda x: word_vectors[f"{x}"])

    def cast_vector(row):
        return np.array(list(map(lambda x: x.astype('double'), row)))

    words['vectors_typed'] = words.vectors.apply(cast_vector)
    print(words)
    words['cluster'] = words.vectors_typed.apply(lambda x: model.predict([np.array(x)]))
    words.cluster = words.cluster.apply(lambda x: x[0])
    words['cluster_value'] = [1 if i==0 else -1 for i in words.cluster]
    words['closeness_score'] = words.apply(lambda x: 1/(model.transform([x.vectors_typed]).min()), axis=1)
    words['sentiment'] = words.closeness_score * words.cluster_value
    words = words.sort_values('sentiment', ascending=False)
    if not os.path.exists('data/02_models'):
        os.mkdir('data/02_models')
    words.to_csv(f'data/02_models/w2v_sentiment_{name}.csv', index=False)

twitter_text = pd.read_csv('data/twitter/twitter_data_cleaned.csv')
twitter_text = twitter_text.loc[twitter_text['lang'] == 'en']
twitter_text['full_text'] = twitter_text['full_text'].str.lower().astype(str)

# Creates the textblob similarity for the given text.
textblob_sim(twitter_text['full_text'])

# Creates word2vec embeddings and clusters on these embeddings to create sentiment by word.
# If pretrained = True, requires the pretrained glove file located in data/00_raw
# I recommend filtering out all non - english data first. Results using pretrained data seem poor.
create_embedding(twitter_text['full_text'], pretrained=True)
create_clusters('data/02_models/w2v_twitter.model')

