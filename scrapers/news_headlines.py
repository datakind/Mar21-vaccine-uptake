import time
import datetime
import requests
import re
import html5lib

import numpy as np
import pandas as pd

from bs4 import BeautifulSoup

"""
Web scraper tool for six U.S. media outlets spanning the political spectrum:
Breitbart, Fox News, the Washington Times, AP, Politico, and the Daily Kos.

Scrapes article titles and publication dates for articles related to the Covid-19
vaccine, and saves data to .csv. 

This script is designed to be run regularly (a cron job is a simple way to do this),
and will update the output .csv with new article data.
"""

# 00 constants -------------------------------------------------------------------------
KEYWORDS = ['vaccine', 'vaccination', 'immunization', 'doses', 'pfizer', 'moderna',
            'johnson & johnson', 'J&J', 'vaccinators', 'innoculation', 'jab', 'astrazeneca',
            'oxford', 'vaccines', 'vaccinated', 'vax']

# 01 scrapers --------------------------------------------------------------------------
def scrape_breitbart(keywords=KEYWORDS):
    """
    Scrapes news article titles from breitbart.com
    """
    breitbart_tags = []
    for section in ['entertainment/', 'health/', 'science/', 'sports/', 'faith/',
                    'politics/', 'europe/', 'asia/']:
        for keyword in keywords:
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

    # breitbart is picky about too many requests, limit to 30
    for n in np.arange(0, min(len(breitbart_tags), 30)):

        # get article link
        link = 'https://www.breitbart.com' + breitbart_tags[n].find('a')['href']
        breitbart_links.append(link)

        # get article title
        breitbart_titles.append(breitbart_tags[n].find('a').get_text())

        # get date
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        date = soup_article.time.attrs['datetime']
        date = date[:-10]
        breitbart_dates.append(date)

    breitbart_data = pd.DataFrame.from_dict({
        'publisher': 'breitbart',
        'date': breitbart_dates,
        'link': breitbart_links,
        'article_title': breitbart_titles
    })

    breitbart_data.drop_duplicates(inplace=True)

    return breitbart_data

def scrape_fox(keywords=KEYWORDS):
    """
    Scrapes news article titles from foxnews.com
    """
    fox_tags = []
    for section in ['health/', 'us/', 'politics/', 'entertainment/', 'world/']:
        for keyword in keywords:
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

    # fox is picky about too many requests, limit to 30
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
        'publisher': 'fox',
        'date': fox_dates,
        'link': fox_links,
        'article_title': fox_titles,
    })

    fox_data.drop_duplicates(inplace=True)

    return fox_data

def scrape_wt(keywords=KEYWORDS):
    """
    Scrapes new article titles from washingtontimes.com
    """
    wt_tags = []
    for section in ['news/', 'specials/coronavirus-covid-19-pandemic-updates/',
                    'news/politics/', 'news/white-house/', 'news/national/', 'news/world/']:
        for keyword in keywords:
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
    # wt is picky about too many requests, limit to 30
    for n in np.arange(0, min(len(wt_tags), 30)):

        # get article link
        link = 'https://www.washingtontimes.com' + wt_tags[n].find('a')['href']
        wt_links.append(link)

        # get article title
        wt_titles.append(wt_tags[n].find('a').get_text().strip())

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

    # format dates
    wt_dates = [datetime.datetime.strptime(date, '%A, %B %d, %Y').strftime('%Y-%m-%d') for date in wt_dates]

    wt_data = pd.DataFrame.from_dict({
        'publisher': 'washington_times',
        'date': wt_dates,
        'link': wt_links,
        'article_title': wt_titles,
    })

    wt_data.drop_duplicates(inplace=True)

    return wt_data

def scrape_ap():
    """
    Scrapes news article titles from apnews.com
    """
    # AP conveniently has all the vaccine news in one place - so no need for keywords or
    # to check multiple pages
    ap_requests = requests.get('https://apnews.com/hub/coronavirus-vaccine')
    ap_homepage = ap_requests.content
    ap_soup = BeautifulSoup(ap_homepage, 'html.parser')
    ap_tags = ap_soup.find_all('a', class_='Component-headline-0-2-111')
    ap_links = ['https://apnews.com' + link.get('href') for link in ap_tags]

    # get article titles and dates
    ap_titles = []
    ap_dates = []
    for link in ap_links:
        ap_article_request = requests.get(link)
        ap_article = ap_article_request.content
        ap_article_soup = BeautifulSoup(ap_article, 'html.parser')

        # article titles
        ap_titles.append(ap_article_soup.find_all('meta')[14]['content'])

        # article date
        date = ap_article_soup.find_all('meta')[24]['content']
        ap_dates.append(date[:-10])

    # join ap data
    ap_data = pd.DataFrame.from_dict({
        'publisher': 'ap',
        'date': ap_dates,
        'link': ap_links,
        'article_title': ap_titles
    })

    ap_data.drop_duplicates(inplace=True)

    return ap_data

def scrape_politico(keywords=KEYWORDS):
    """
    Scrapes news article titles from politico.com
    """
    politico_links = []
    for keyword in keywords:
        politico_request = requests.get('https://www.politico.com/search?q={}'.format(keyword))
        politico_homepage = politico_request.content
        politico_soup = BeautifulSoup(politico_homepage, 'html.parser')
        politico_tags = politico_soup.find_all('h3')
        new_links = [tag.find('a')['href'] for tag in politico_tags]
        new_links = [link for link in new_links if 'news' in link and 'magazine' not in link]
        # no duplicates
        [politico_links.append(link) for link in new_links if link not in politico_links]

    # get article titles and dates
    politico_titles = []
    politico_dates = []
    for link in politico_links:
        # prep article content
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        # get article title
        title = soup_article.find('title').get_text().replace(' - POLITICO', '')
        politico_titles.append(title)

        # get publication date
        # (some of their interactive articles have no date data in the html)
        try:
            politico_dates.append(soup_article.time.attrs['datetime'][:-9])
        except:
            politico_dates.append('continuously updated')

    # assembling data
    politico_data = pd.DataFrame.from_dict({
        'publisher': 'politico',
        'date': politico_dates,
        'link': politico_links,
        'article_title': politico_titles
    })

    politico_data.drop_duplicates(inplace=True)

    return politico_data

def scrape_dailykos(keywords=KEYWORDS):
    """
    Scrapes news article titles from dailykos.com
    """
    dk_request = requests.get('https://www.dailykos.com')
    dk_homepage = dk_request.content
    dk_soup = BeautifulSoup(dk_homepage, 'html.parser')
    dk_tags = dk_soup.find_all('div', class_='cell-wrapper')
    dk_links = ['https://www.dailykos.com' + tag.find('a')['href'] for tag in dk_tags]
    dk_links = [link for link in dk_links if any(keyword in link for keyword in keywords)]

    # get article titles and dates
    dk_titles = []
    dk_dates = []
    for link in dk_links:
        # prep article content
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        # get article title
        dk_titles.append(soup_article.find('title').get_text())

        # get publication date
        date = str(soup_article.find('span', class_='timestamp'))
        dk_dates.append(date[len(date) - 21:-7])

    # format dates
    dk_dates = [datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d') for date in dk_dates]

    # assembling data
    dailykos_data = pd.DataFrame.from_dict({
            'publisher': 'dailykos',
            'date': dk_dates,
            'link': dk_links,
            'article_title': dk_titles
    })

    dailykos_data.drop_duplicates(inplace=True)

    return dailykos_data

# 02 helper functions ---------------------------------------------------------------------
def save_data(new_data, existing_file=None):
    """
    Concatenates scraped data to old df (if exists) and saves new data set
    """
    # read in old data, if we're adding new data to a previously-saved .csv
    if existing_file is not None:
        existing_data = pd.read_csv(existing_file)
        num_prior_rows = len(existing_data)

        # append new data
        final_data = existing_data.append(new_data).drop_duplicates()
        num_current_rows = len(final_data)

        # save new csv
        final_data.to_csv('data/news_headlines/news_headline_data.csv', index=False)

    else:
        num_prior_rows = 0
        new_data.to_csv('data/news_headlines/news_headline_data.csv', index=False)
        num_current_rows = len(new_data)

    print('Number of entries in old data: {}'.format(num_prior_rows))
    print('Total number of entries in new data: {}'.format(num_current_rows))
    print('Rows added: {}'.format(num_current_rows - num_prior_rows))
    return

def run_safely(f, outlet, *args):
    """
    Web scraping functions frequently break when websites change.

    This function is to wrap the scraping functions in a try except clause
        so that other functions will continue even if one website
        is no longer scrapable.
    """
    print(f'Scraping {outlet}...')
    try:
        df = f(*args)
        print(f'Scraped {len(df)} {outlet} article titles')
        return df
    except:
        print(f'Error scraping {outlet}.')
        return pd.DataFrame()


if __name__ == '__main__':

    start_time = time.time()
    print('Beginning scraping pipeline.')

    breitbart_df = run_safely(scrape_breitbart, outlet='Breitbart')
    fox_df = run_safely(scrape_fox, outlet='Fox')
    washington_times_df = run_safely(scrape_wt, outlet='Washington Times')
    ap_df = run_safely(scrape_ap, outlet='AP')
    politico_df = run_safely(scrape_politico, outlet='Politico')
    dailkos_df = run_safely(scrape_dailykos, outlet='Daily Kos')

    duration = round((time.time() - start_time)/60, 4)
    print(f'Done scraping. Pipeline took {duration} minutes.')

    all_data = pd.concat([breitbart_df,
                          fox_df,
                          washington_times_df,
                          ap_df,
                          politico_df,
                          dailkos_df])

    save_data(all_data)
