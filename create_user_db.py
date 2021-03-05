import pandas as pd
import re

twitter_users = pd.read_csv('data/00_raw/twitter_user.csv')
twitter_text = pd.read_csv('data/00_raw/twitter_text.csv')
twitter_hashtag = pd.read_csv('data/00_raw/twitter_hashtag.csv')

twitter_text.drop(['geo', 'coordinates', 'place', 'possibly_sensitive'], axis=1, inplace=True)

twitter_text = twitter_text[twitter_text['user_id'].notna()]

twitter_text.drop_duplicates(inplace=True)

twitter_text['tweet_id']=twitter_text.tweet_id.astype('int64').astype('str')
twitter_text['retweet_count']=twitter_text.retweet_count.astype('int64')
twitter_text['favorite_count']=twitter_text.favorite_count.astype('int64')
twitter_text['user_id']=twitter_text.user_id.astype('int64').astype('str')

twitter_users['user_id']=twitter_users['user_id'].astype('int64').astype('str')
twitter_users['user_followers_count'] = twitter_users['user_followers_count'].astype('int64')

twitter_hashtag['tweet_id'] = twitter_hashtag['tweet_id'].astype('int64').astype('str')
twitter_hashtag['hashtags'] = twitter_hashtag.groupby('tweet_id')['hashtags'].apply(list)

twitter_text['full_text'].apply(lambda x: x.replace('/n', '. '))

user_text_df = pd.merge(twitter_text, twitter_users, on='user_id', how='left')

user_gb = user_text_df.groupby('user_id')

transform_cols = ['created_at', 'full_text', 'retweet_count', 'favorite_count', 'lang']

new_df = pd.DataFrame({col: user_gb[col].apply(list) for col in transform_cols})
new_df['user_id'] = [user_id for user_id, unused_df in user_gb]
new_df = new_df.reset_index(drop=True)
new_df = pd.merge(new_df, twitter_users, on='user_id', how='left')
new_df['number of tweets'] = new_df['full_text'].apply(lambda x: len(x))
new_df['total retweets'] = new_df['retweet_count'].apply(lambda x: sum(x))
new_df['total_favorites'] = new_df['favorite_count'].apply(lambda x: sum(x))

def grab_mentions(list_of_str):
    return [re.findall('@\S+\s', string) for string in list_of_str]

def grab_hashtags(list_of_str):
    return [re.findall('#\S+\s', string) for string in list_of_str]

new_df['mentions'] = new_df['full_text'].apply(grab_mentions)
new_df['hashtags'] = new_df['full_text'].apply(grab_hashtags)
print(user_text_df)

new_df.to_csv('data/01_cleaned/twitter_user_df', index=False)