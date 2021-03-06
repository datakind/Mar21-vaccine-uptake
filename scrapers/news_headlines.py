# Web Scraper Tool for US Media Outlets

import numpy as np
import pandas as pd

import json
import requests
import re
import html5lib

from bs4 import BeautifulSoup

# 00 constants -------------------------------------------------------------------------
keywords = ['vaccine', 'vaccination', 'immunization', 'doses', 'pfizer', 'moderna',
            'johnson & johnson', 'J&J', 'vaccinators', 'innoculation', 'jab', 'astrazeneca',
            'oxford', 'vaccines', 'vaccinated']

def scrape_breitbart():
    """
    Scrapes news article titles from breitbart.com
    return: pd.DataFrame
    """
    breitbart_tags = []
    for section in ['entertainment/', 'health/', 'science/', 'sports/', 'faith/',
                    'politics/', 'europe/', 'asia/']:
        for keyword in keywords:
            breitbart_request = requests.get('https://www.breitbart.com/{}'.format(section))
            breitbart_homepage = breitbart_request.content
            breitbart_soup = BeautifulSoup(breitbart_homepage, 'html.parser')

            # locate article tags
            new_tags = breitbart_soup.find_all(
                lambda tag: tag.name == 'h2' and re.findall(r'{}'.format(keyword), tag.text, flags=re.I))

            breitbart_tags+= new_tags

    # get article titles, dates, and links
    breitbart_links = []
    breitbart_titles = []
    breitbart_dates = []

    # limit to 30 tags, otherwise issues with beautiful soup
    for n in np.arange(0, min(len(breitbart_tags), 30)):

        # get article link
        link = breitbart_tags[n].find('a')['href']
        link = "https://www.breitbart.com" + link
        breitbart_links.append(link)

        # get article title
        title = breitbart_tags[n].find('a').get_text()
        breitbart_titles.append(title)

        # prep article content
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        # get publication datetime
        date = soup_article.time.attrs['datetime']
        date = date[:-10]
        breitbart_dates.append(date)

    # assembling data
    breitbart_data = pd.DataFrame.from_dict({
        'publisher': 'Breitbart',
        'date': breitbart_dates,
        'link': breitbart_links,
        'article_title': breitbart_titles
    })

    breitbart_data.drop_duplicates(inplace=True)

    return breitbart_data

def scrape_fox():
    """
    Scrapes news article titles from foxnews.com
    return: pd.DataFrame
    """
    fox_tags = []
    for section in ['health/', 'us/', 'politics/', 'entertainment/', 'world/']:
        for keyword in keywords:

            # load the HTML content using requests and save into a variable
            fox_requests = requests.get('https://www.foxnews.com/{}'.format(section))
            fox_homepage = fox_requests.content

            # create a soup to allow BeautifulSoup to work
            fox_soup = BeautifulSoup(fox_homepage, 'html.parser')

            # locate article tags
            new_tags = fox_soup.find_all(
                lambda tag: tag.name == 'article' and re.findall(r'{}'.format(keyword), tag.text, flags=re.I))

            fox_tags+= new_tags

    # get article titles, dates, and links
    fox_links = []
    fox_titles = []
    fox_dates = []

    for n in np.arange(0, min(len(fox_tags), 30)):
        link = fox_tags[n].find('a')['href']
        link = "https://foxnews.com" + link
        fox_links.append(link)
        fox_links = [x for x in fox_links if "/v/" not in x]
        fox_links = [x for x in fox_links if "https://foxnews.comhttps://www.foxnews.com" not in x]

    # prep for article content
    for link in fox_links:
        fox_article_request = requests.get(link)
        fox_article = fox_article_request.content
        fox_article_soup = BeautifulSoup(fox_article, 'html.parser')
        fox_metadata = fox_article_soup.find_all('script')[3]

        # get date
        date = re.search(r'\d{4}-\d{2}-\d{2}', str(fox_metadata)).group(0)
        fox_dates.append(date)

        # get title
        start = 'headline":'
        end = '/\n'
        s = str(fox_metadata)
        title = s[s.find(start) + len(start):s.rfind(end)]
        title = title.split('"')[1]
        fox_titles.append(title)

    # join fox data
    fox_data = pd.DataFrame.from_dict({
        'publisher': 'Fox',
        'date': fox_dates,
        'link': fox_links,
        'article_title': fox_titles,
    })

    fox_data.drop_duplicates(inplace=True)

    return fox_data
