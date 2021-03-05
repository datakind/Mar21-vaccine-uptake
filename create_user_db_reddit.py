import pandas as pd
import re

comments = pd.read_csv('data/01_cleaned/reddit_comments_cleaned.csv')
posts = pd.read_csv('data/00_raw/reddit_posts.csv')

print(comments)

group_cols = ['comment', 'downs', 'ups', 'comment_date']

user_gb = comments.groupby('author')

new_df = pd.DataFrame({col: user_gb[col].apply(list) for col in group_cols})
new_df['author'] = [author_id for author_id, unused_df in user_gb]
new_df = new_df.reset_index(drop=True)
new_df['vote_delta'] = new_df.apply(lambda x: sum(x['ups']) - sum(x['downs']), axis=1)

print(new_df)

post_cols = ['subreddit', 'title', 'ups', 'downs', 'num_comments', 'subreddit_subscribers', 'post_date']

post_gb = posts.groupby('author')

post_df = pd.DataFrame({col: post_gb[col].apply(list) for col in post_cols})
post_df['author'] = [author_id for author_id, unused_df in post_gb]
post_df = post_df.reset_index(drop=True)
post_df = post_df.rename(columns={'ups': 'post_ups', 'downs': 'post_downs'})
post_df['post_vote_delta'] = post_df.apply(lambda x: sum(x['post_ups']) - sum(x['post_downs']), axis=1)

merge_df = pd.merge(new_df, post_df, on='author', how='outer')

merge_df.to_csv('data/01_cleaned/reddit_user_df.csv', index=False)