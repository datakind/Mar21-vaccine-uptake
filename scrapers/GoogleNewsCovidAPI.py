#!/usr/bin/env python
# coding: utf-8

# ### Derived from:
# https://rapidapi.com/blog/google-news-api-python/
# 
# To avoid formatting issues, please open the output csv in a text editor, and select delimit by |.

# In[9]:


#! python
"""
Description:
  This script pulls a list of items from the Google News API, with the topic 'covid-19'
  
Output: Csv file with article date, publisher, title, link

"""

#import libraries used below
import requests
import json
from datetime import datetime
from pathlib import Path

# This is where the generated html will be saved (in the local directory)
#  More information about the Path function is described at https://realpython.com/python-pathlib/
data_folder = Path("~")
outputFile = "covid_google_news.csv"

# datetime object containing current date and time
now = datetime.now()

# Get the date and time in the format YYYY-mm-dd H:M:S
dt_string = now.strftime("%Y-%m-%d %H:%M:%S")


# Set to 1 to show details along the way for debugging purposes
debug=1


url = "https://google-news.p.rapidapi.com/v1/topic_headlines"

querystring = {"lang":"en","country":"US","topic":"CAAqIggKIhxDQkFTRHdvSkwyMHZNREZqY0hsNUVnSmxiaWdBUAE"}

headers = {
    'x-rapidapi-key': "5820bf39c3msh66e2e88970341ddp155860jsn1e7ee7cf25a0",
    'x-rapidapi-host': "google-news.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)


# In[68]:


json_dictionary = response.json()

with open(outputFile, "w", encoding="utf-8",) as f:
        f.write("Date" + "|" + "Publisher" + "|" + "Title" + "|" + "Link" + "\n")
        
NewsArticlesList = []

# Loop through dictionary keys to access each article
for item in json_dictionary['articles']:
    # Pull the title for this article into a variable.
    title = item['title']
    timestamp = item['published']
    date = item['published'].split(', ')[1][0:11]
    publisher = item['source']['title']
    link = item['link']
    
    if debug>0:
        print("Title: ", title, "Date: ", date)
        
    # append to list
    NewsArticlesList.append([date, publisher, title, link])
        
    # write to csv
    headline = str(date) + "|" + str(publisher) + "|" +  str(title) + "|" + str(link) + "\n"

    with open(outputFile, "a", encoding="utf-8") as f:
        f.write(headline)


# In[64]:


json_dictionary['articles']


# In[73]:


import pandas as pd
# convert news articles list into dataframe
NewsDf=pd.DataFrame(NewsArticlesList,columns=['date', 'publisher', 'title', 'link'])


# In[76]:


NewsDf['publisher'].value_counts()


# In[ ]:




