from urllib.request import urlopen, HTTPError
import json
import pandas as pd 
import random 
import re 
import time 
from datetime import datetime
import logging
logging.basicConfig(filename='reddit_scraping.log', level=logging.INFO)

# collect posts from subreddits pertaining to the vaccine 
# collect comments from those posts 
# collect replies to those comments 

sub_reddits = ['Coronavirus', 'vaxxhappened', 'antivax', 'VaccineMyths', 
'science', 'news', 'COVID19', 'conspiracy', 'nyc', "Indiana", "Conservative", "illinois", "nashville", "LosAngeles"]

match_words =['covid-19 vaccine', 'vaccine', 'vaccination', 'coronavirus vaccine', 
               'covid vaccine', 'covid', 'coronavirus', 'virus', 'vax', 'doses', 'pfizer', 'moderna',
               'johnson & johnson', 'J&J', 'vaccinators']


def parse_sub_reddits(sub_reddit: str, 
                        match_words: list):
    """
    Check all the posts in the subreddit for 

    Args:
        sub_reddit (str): a subreddit to parse posts
        match_words (list): a list of match words 
    Returns:
        List of all posts in the subreddit mentioning vaccines 
    """

    url_to_open = f"https://www.reddit.com/r/{sub_reddit}.json"
    success_status = 0
    while success_status != 200:
        try:
            response = urlopen(url_to_open, timeout=10)
            success_status = response.status
        except HTTPError:
            logging.info(f"HTTP Error for exceeding requests. Sleeping for 2 minutes at {datetime.today()}.")
            time.sleep(120)
            success_status = 400
    
    entire_sub_reddit = json.loads(response.read())

    posts = [post["data"] for post in entire_sub_reddit['data']['children'] if post["kind"] == "t3"]
    _ids = []
    post_dataframes = []
    return_dict = {}
    if len(posts) > 0:
        for post in posts:
            try:
                title = post['title'].lower()
                if re.findall(r"(?=("+'|'.join(match_words)+r"))", title):
                    _id = post['id']
                    norm_df = pd.json_normalize(post)
                    norm_df = norm_df[['id', 'subreddit', 'title', 'ups', 'downs', 'upvote_ratio', 'num_comments', 'author_fullname', 'created_utc', 'subreddit_subscribers']]
                    norm_df = norm_df.rename(columns = {'id': 'post_id', 'author_fullname': 'author'})
                    post_dataframes.append(norm_df)
                    if post['num_comments'] > 0:
                        _ids.append(_id)
            except KeyError:
                pass 
        if len(post_dataframes) > 0:
            all_dfs = pd.concat(post_dataframes, ignore_index=True)
            return_dict['data'] = all_dfs
            return_dict['ids'] = _ids
        else:
           return_dict['data'] = None
           return_dict['ids'] = None 
    else:
        return_dict['data'] = None
        return_dict['ids'] = None 

    return return_dict
        

def comment_data(post_id: str, 
            sub_reddit: str):
    

    """
    Generates a pandas dataframe with scraped comments and replies data. Will concatenate replies with comments 
    post_id (str): post_id from valid posts that contain covid vaccine keywords 
    """
    url_to_open = f"https://www.reddit.com/r/{sub_reddit}/comments/{post_id}.json"
    success_status = 0
    while success_status != 200:
        try:
            response = urlopen(url_to_open, timeout=10)
            success_status = response.status
        except HTTPError:
            logging.info(f"HTTP Error for exceeding requests. Sleeping for 2 minutes at {datetime.today()}.")
            time.sleep(120)
            success_status = 400
    
    sub_reddit_page = json.loads(response.read())
    comments_df = pd.json_normalize(sub_reddit_page[1]['data']['children'])
    comments_df['post_id'] = post_id
    comments_df = comments_df[['post_id', 'data.id', 'data.author_fullname', 'data.body', 'data.created', 
                                'data.downs', 'data.ups']]
    comments_df = comments_df.rename(columns = {'data.id': 'comment_id', 'data.author_fullname': 'author', 'data.body': 'comment', 
                                                'data.created': 'created_utc', 'data.downs': 'downs', 'data.ups': 'ups'})
    comments_df['reply'] = 'N'
    comments_df['comment_replied_id'] = ''
    # get all replies 
    replies_list = []
    for comment in sub_reddit_page[1]['data']['children']:
        replies = comment.get('data').get('replies')
        comment_id = comment.get('data').get('id') 
        if replies is None or replies == '':
            pass
        else:
            replies_df = pd.json_normalize(replies['data']['children'])
            try:
                replies_df = replies_df[['data.id', 'data.author_fullname', 'data.body', 'data.created', 
                                'data.downs', 'data.ups']]
            except KeyError:
                pass
            replies_df = replies_df.rename(columns = {'data.id': 'comment_id', 'data.author_fullname': 'author', 'data.body': 'comment', 
                                                'data.created': 'created_utc', 'data.downs': 'downs', 'data.ups': 'ups'})
            replies_df['reply'] = 'Y'
            replies_df['comment_replied_id'] = comment_id
            replies_df['post_id']  = post_id
            replies_list.append(replies_df)
    if len(replies_list) == 1:
        all_replies = replies_list[0]
    elif len(replies_list) > 1: 
        all_replies = pd.concat(replies_list, ignore_index = True)
    else:
        all_replies = None 

    column_order = [c for c in comments_df.columns]
    comments_df = comments_df[column_order]
    if all_replies is not None:
        all_replies = all_replies[column_order]
        all_comments_replies = pd.concat([comments_df, replies_df], ignore_index=True)
    else:
        all_comments_replies = comments_df

    return all_comments_replies

def utc_to_date(x): 
    try:
        new_value = datetime.strftime(datetime.fromtimestamp(x), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        new_value = None

    return new_value

def stream_to_db(subreddit: str, 
                df_dict: dict, 
                db_path: str) -> None:
    """
    Appends to CSVs and removes any duplicated tweets or users before saving

    Args:
        df_dict (dict): return from scraping tweets
        db_path (str): path to database files 
    """
    file_lkps = {'posts': f"reddit-{subreddit}-posts.csv", 
                'comments': f"reddit-{subreddit}-comments.csv"}
    
    for _key in df_dict:
        if df_dict.get(_key) is None:
            pass
        full_path = f"{db_path}/{file_lkps.get(_key)}"
        df = df_dict.get(_key)
        df.to_csv(full_path, index=False, encoding='utf-8')
        logging.info(f"Saved {_key} data for subreddit {subreddit} at {datetime.today()}")
    
    return None 

if __name__ == "__main__":
    for sr in sub_reddits:
        logging.info(f'Starting scraping for subreddit {sr} at {datetime.today()}')
        db_path = '/Users/philazar/Desktop/projects/covid-sentiment/data/reddit'
        valid_posts = parse_sub_reddits(sub_reddit = sr, match_words= match_words)
        posts_df = valid_posts.get('data')
        if posts_df is not None: 
            posts_df['post_date'] = posts_df['created_utc'].apply(lambda x: utc_to_date(x))
            stream_to_db(subreddit = sr, 
                            df_dict = {'posts': posts_df}, 
                            db_path=db_path)
            post_ids = valid_posts.get('ids')
            if post_ids is not None:
                comments_dataframes = []
                for i in post_ids:
                    comments_dataframe = comment_data(post_id=i, sub_reddit= sr)
                    comments_dataframes.append(comments_dataframe)
                all_comments = pd.concat(comments_dataframes, ignore_index =True)
                all_comments['comment_date'] = all_comments['created_utc'].apply(lambda x: utc_to_date(x))
                stream_to_db(subreddit = sr, 
                            df_dict = {'comments': all_comments}, 
                            db_path=db_path)
        logging.info(f'Finished scraping for subreddit {sr} at {datetime.today()}')
                