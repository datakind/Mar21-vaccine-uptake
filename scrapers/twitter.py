import pandas as pd 
import tweepy 
import os 
from datetime import datetime, timedelta 
import time 
import random
import logging
logging.basicConfig(filename='twitter_scraping.log', level=logging.INFO)
####### constants 

# scraping
covid_keywords = ['covid', 'coronavirus', 'covid-19', 'pandemic', 'covid19', 'corona', 'virus', 'sarscov2']
vaccine_keywords = ['vax', 'vaccination', 'pfizer', 'moderna', 'vaccine', 'antivax', 'anti-vax', 'J&J', 'vaccinated', 'doses']
hashtags = ['#herdimmunity','#firefauci', '#vaccinated','#vaccineswork', '#bigpharma', '#vaxed', '#vaxxed', '#antivaccine', '#antivax','#immunity','#novaccine', '#vaccine', '#covid', '#coronavirus', '#covid19']

# twitter api 
api_key = os.getenv('TWITTER_API')
secret_key = os.getenv('TWITTER_SECRET_KEY')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_secret = os.getenv('TWITTER_ACCESS_SECRET')


# test or prd, 
env = 'prd'
#######

def build_query(covid_words: list, 
                vaccine_words: list, 
                hashtag_words: list) -> str:
    """Build query for twitter api per docs: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query

    Will generate a query that contains all possible combinations of covid + vaccine words, add hash tags to each

    The resulting logci will be: 
    - contains any covid + vaccine keyword pair OR contains any hashtag 
    - AND is not a retweet 
    Args:
        covid_words (list): List of covid related words
        vaccine_words (list): List of vaccination related qords 
        hashtag_words (list): List of specific hashtags 
    """

    def _or_parser(word_list: list):
        n_words = len(word_list) -1
        rand_ = [random.randint(0,n_words) for i in range(2)]
        word_list = [w_ for w_ in word_list if word_list.index(w_) in rand_]
        for w in word_list:
            if len(word_list) == 1:
                word_str = f"{w}"
            elif word_list.index(w) == 0:
                word_str = f"{w} OR"
            elif word_list.index(w) == (len(word_list) -1):
                word_str = f"{word_str} {w}"
            else:
                word_str = f"{word_str} {w} OR"

        word_str =f"({word_str})"

        return word_str 
    def _and_parser(word_list_1: list, 
                    word_list_2: list):
        n_1 = len(word_list_1) -1
        n_2 = len(word_list_2) -1
        rand_1 = random.randint(0,n_1)
        rand_2 = random.randint(0,n_2)
        
        word_1 = word_list_1[rand_1]
        word_2 = word_list_2[rand_2]

        return f"({word_1} AND {word_2})"

    rand_type = random.randint(0,3)

    if rand_type == 0:
        covid_str = _or_parser(word_list=covid_words)
        vax_str = _or_parser(word_list=vaccine_words)
        hashtag_str = _or_parser(word_list=hashtag_words)
        query = f"{covid_str} {vax_str} OR {hashtag_str} -filter:retweets"
    elif rand_type == 1:
        and_str = _and_parser(word_list_1=covid_words, word_list_2=vaccine_words)
        query = f"{and_str} -filter:retweets"
    elif rand_type == 2:
        and_str = _and_parser(word_list_1=vaccine_words, word_list_2=hashtag_words)
        query = f"{and_str} -filter:retweets" 
    else:
        random_ht = random.randint(0, len(hashtag_words)-1)
        _hash = hashtag_words[random_ht]
        query = f'{_hash} -filter:retweets'
    logging.info(f"Query Submitted: {query}")
    return query 


def scrape_tweets(twitter_api,
                   query_: str, 
                   language: str, 
                   result_type: str, 
                   tweet_mode: str, 
                   count: int, 
                   until: str):
    """
    This scrapes tweets and formats into a tabular format with necessary data. This will stream into a database 

    Args:
        twitter_api ([type]): App authenticated API 
        query_ (str): Query to search tweets 
        lanuage (str): en for english
        result_type (str): mixed, popular or recent. Default is mixed
        tweet_mode (str): extended to get non-truncated text. However, seems to only be truncated to 140 characters
        count (int): limit is 100
        until (str): YYYY-MM-DD to limit tweets 

    Returns:
        Dictionary of pd.DataFrames formatted DF for analysis 
    """

    tweets = twitter_api.search(q=query, 
                                lang = language, 
                                result_type = result_type, 
                                tweet_mode=tweet_mode, 
                                count=count, 
                                until = until)
    
    if len(tweets) == 0:
        return None 
    else: 
        ht_dataframes = []
        tweet_dataframes = []
        user_dataframes = []
        for tweet in tweets:
            _index = tweets.index(tweet)
            normalize_json = pd.json_normalize(tweets[_index]._json)
            columns_to_keep = ['id', 'full_text', 'geo', 'coordinates', 'place', 'retweet_count', 'favorite_count', 'possibly_sensitive', 
                                'created_at','lang', 'user.id', 'user.location', 'user.followers_count', 'user.verified']
            
            cols = [c for c in columns_to_keep if c in normalize_json.columns]
            missing_cols = [c for c in columns_to_keep if c not in cols]

            all_tweet_df = normalize_json[cols].rename(columns={'user.id': 'user_id', 
                                                                    'id': 'tweet_id', 
                                                                    'user.location': 'user_location', 
                                                                    'user.followers_count': 'user_followers_count', 
                                                                    'user.verified': 'user_verified'})
            if len(missing_cols) > 0:
                for mc in missing_cols:
                    all_tweet_df[mc] = 'NOT FOUND'
            column_order = ['tweet_id', 'created_at','full_text', 'geo', 'coordinates', 'place', 'retweet_count', 'favorite_count', 'possibly_sensitive',
            'lang', 'user_id', 'user_location', 'user_verified', 'user_followers_count']
            all_tweet_df = all_tweet_df[column_order]
            tweet_df = all_tweet_df[['tweet_id','created_at','full_text', 'geo', 'coordinates', 'place', 'retweet_count', 'favorite_count', 'possibly_sensitive','lang','user_id']] 
            user_df = all_tweet_df.filter(regex="^user*")
            
            # capture nested hashtags, expanded_urls 
            hashtags = tweets[_index]._json['entities']['hashtags']
            if len(hashtags) > 0: 
                ht_text = []
                for ht in hashtags:
                    i = hashtags.index(ht)
                    ht_text.append(hashtags[i].get('text'))
                ht_dict = {'hashtags': ht_text}

                tweet_id =tweets[_index]._json['id']
                ht_dict['tweet_id'] = tweet_id

                ht_df = pd.DataFrame(ht_dict) 
                ht_dataframes.append(ht_df)
            
            
            tweet_dataframes.append(tweet_df)
            user_dataframes.append(user_df)
        
        # concat dataframes and remove duplicate users 
        tweet_df_final = pd.concat(tweet_dataframes, ignore_index = True)
        user_df_final = pd.concat(user_dataframes, ignore_index = True)
        user_df_final.drop_duplicates(subset=['user_id'], keep='first', inplace=True)

        return_dict = {}
        return_dict['users'] = user_df_final
        return_dict['tweets'] = tweet_df_final

        if len(ht_dataframes) > 1:
            hashtag_df_final = pd.concat(ht_dataframes, ignore_index= True)
        elif len(ht_dataframes) == 1:
            hashtag_df_final = ht_dataframes[0]
        else:
            hashtag_df_final = None

        if hashtag_df_final is not None:
            return_dict['hashtags'] = hashtag_df_final  

        return return_dict

def stream_to_db(df_dict: dict, 
                db_path: str) -> None:
    """
    Appends to CSVs and removes any duplicated tweets or users before saving

    Args:
        df_dict (dict): return from scraping tweets
        db_path (str): path to database files 
    """
    file_lkps = {'users': 'twitter_user.csv', 
                  'hashtags': 'twitter_hashtag.csv', 
                  'tweets': 'twitter_text.csv'}
    unique_ids = {'users': 'user_id', 
                  'hashtags': 'tweet_id', 
                  'tweets': 'tweet_id'}
    
    for _key in df_dict:
        if df_dict.get(_key) is None:
            pass
        # check if file exists
        full_path = f"{db_path}/{file_lkps.get(_key)}"
        if os.path.isfile(full_path): 
            current_df = pd.read_csv(full_path)
            unique_id = unique_ids.get(_key)
            # some counts 
            n_current = current_df[unique_id].count()
            cc_df = df_dict.get(_key)
            scraped_count = cc_df[unique_id].count()
            full_df = pd.concat([current_df, cc_df], ignore_index=True)
            full_df.drop_duplicates(subset=[unique_id], keep='first', inplace=True)
            new_count = full_df[unique_id].count()
            logging.info(f"Adding {new_count-n_current} records to {file_lkps.get(_key)}. Total {scraped_count} were scraped.")
            full_df.to_csv(full_path, index=False, encoding='utf-8')
        else:
            new_df = df_dict.get(_key)
            new_df.to_csv(full_path, index =False, encoding='utf-8')
    
    return None 

# limits 450 requests x 100 tweets per request every 15 minutes 

if env == 'test': 
    requests_static = 100
    n_tweets = 10
    timeout = 15
    path = '/Users/philazar/Desktop/projects/covid-sentiment/data'
else:
    requests_static = 450
    n_tweets = 100
    timeout = 15*60 + 1
    path = '/Users/philazar/Desktop/projects/covid-sentiment/data'

twitter_auth = tweepy.AppAuthHandler(consumer_key=api_key, consumer_secret=secret_key)
twitter_api = tweepy.API(twitter_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# one iteration == 45000 tweets 
max_iters = 12
requests = int(requests_static*1)
total_requests = 0

while max_iters > 0:
    today_ = datetime.today()
    rand_ = random.randint(0,6)
    until_ = today_ - timedelta(days=rand_)
    until_fmt = datetime.strftime(until_, '%Y-%m-%d')
    logging.info(f'Scraping data for day {until_fmt}')
    logging.info(f'Scraping twitter at {datetime.strftime(today_, "%Y-%m-%d %H:%M:%S")} request number: {requests}')
    rand_i = random.randint(0,2)
    if rand_i == 0:
        _type = 'mixed'
    elif rand_i == 1:
        _type = 'recent'
    else:
        _type = 'popular'
    query =build_query(covid_words = covid_keywords, 
                vaccine_words = vaccine_keywords, 
                hashtag_words = hashtags) 
    data_dict = scrape_tweets(twitter_api = twitter_api,
                   query_ = query, 
                   language = 'en', 
                   result_type = _type, 
                   tweet_mode = 'extended', 
                   count = n_tweets, 
                   until = until_fmt) 
    if data_dict is not None:
        stream_to_db(df_dict = data_dict, db_path = path)

    total_requests += 1 
    requests -= 1
    logging.info(f'{datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")}\n Total requests: {total_requests}')
    if requests == 0:
        logging.info(f'Sleeping at {datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")}')
        time.sleep(timeout)
        # reset requests 
        requests = int(requests_static*1) 
        max_iters -= 1
    
logging.info(f'Complete at {datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")}')
    

