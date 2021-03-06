# Web Scraper Tool for US Media Outlets

import numpy as np
import pandas as pd

import json
import requests
import re
import html5lib

from bs4 import BeautifulSoup

# 00 constants -------------------------------------------------------------------------
KEYWORDS = ['vaccine', 'vaccination', 'immunization', 'doses', 'pfizer', 'moderna',
            'johnson & johnson', 'J&J', 'vaccinators', 'innoculation', 'jab', 'astrazeneca',
            'oxford', 'vaccines', 'vaccinated']

# 01 scrapers --------------------------------------------------------------------------
def scrape_breitbart(keywords=KEYWORDS):
    """
    Scrapes news article titles from breitbart.com
    return: pd.DataFrame
    """
    breitbart_tags = []
    for section in ['entertainment/', 'health/', 'science/', 'sports/', 'faith/',
                    'politics/', 'europe/', 'asia/']:
        for keyword in KEYWORDS:
            breitbart_request = requests.get('https://www.breitbart.com/{}'.format(section))
            breitbart_homepage = breitbart_request.content
            breitbart_soup = BeautifulSoup(breitbart_homepage, 'html.parser')
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

        # get date
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        date = soup_article.time.attrs['datetime']
        date = date[:-10]
        breitbart_dates.append(date)

    breitbart_data = pd.DataFrame.from_dict({
        'publisher': 'Breitbart',
        'date': breitbart_dates,
        'link': breitbart_links,
        'article_title': breitbart_titles
    })

    breitbart_data.drop_duplicates(inplace=True)

    return breitbart_data

def scrape_fox(keywords=KEYWORDS):
    """
    Scrapes news article titles from foxnews.com
    return: pd.DataFrame
    """
    fox_tags = []
    for section in ['health/', 'us/', 'politics/', 'entertainment/', 'world/']:
        for keyword in KEYWORDS:
            fox_requests = requests.get('https://www.foxnews.com/{}'.format(section))
            fox_homepage = fox_requests.content
            fox_soup = BeautifulSoup(fox_homepage, 'html.parser')
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

    fox_data = pd.DataFrame.from_dict({
        'publisher': 'Fox',
        'date': fox_dates,
        'link': fox_links,
        'article_title': fox_titles,
    })

    fox_data.drop_duplicates(inplace=True)

    return fox_data

def scrape_wt(keywords=KEYWORDS):
    """
    Scrapes new articles from washingtontimes.com
    return: pd.DataFrame
    """
    wt_tags = []
    for section in ['news/', 'specials/coronavirus-covid-19-pandemic-updates/',
                    'news/politics/', 'news/white-house/', 'news/national/', 'news/world/']:
        for keyword in KEYWORDS:
            wt_request = requests.get('https://www.washingtontimes.com/{}'.format(section))
            wt_homepage = wt_request.content
            wt_soup = BeautifulSoup(wt_homepage, 'html.parser')
            new_tags = wt_soup.find_all(
                lambda tag: tag.name == 'h2' and re.findall(r'{}'.format(keyword), tag.text, flags=re.I))
            wt_tags += new_tags

    # get article titles, dates, and links
    wt_links = []
    wt_titles = []
    wt_dates = []
    for n in np.arange(0, min(len(wt_tags), 30)):

        # get article link
        link = wt_tags[n].find('a')['href']
        link = 'https://www.washingtontimes.com' + link
        wt_links.append(link)

        # get article title
        title = wt_tags[n].find('a').get_text()
        title = title.strip()
        wt_titles.append(title)

        # get date
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        meta = soup_article.find('div', class_='meta').find('span', class_='source').text
        strip = meta.replace(
            ' -\n\t\t\t\n\t\t\t\tAssociated Press\n -\n                      \n                        \n                        ',
            '')
        strip = strip.replace(
            ' -\n\t\t\t\n\t\t\t\tThe Washington Times\n -\n                      \n                        \n                        ',
            '')
        date = strip.replace('\n                      \n                    ', '')
        wt_dates.append(date)

    wt_data = pd.DataFrame.from_dict({
        'publisher': 'washington_times',
        'date': wt_dates,
        'link': wt_links,
        'article_title': wt_titles,
    })

    wt_data.drop_duplicates(inplace=True)

    return wt_data


if name == '__main__'():

    breitbart_df = scrape_breitbart()
    fox_df = scrape_fox()

    all_data = pd.concat([breitbart_df, fox_df])

    all_data.to_csv('all_title_data.csv', index=False)
