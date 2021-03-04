# Vaccine Uptake
Volunteers will use open and scraped data to analyze trends in public sentiment regarding  the COVID-19 vaccine. This exploration will provide another resource for policymakers and implementers looking to increase vaccine distribution and craft messaging to combat vaccine hesitancy and misinformation. 

# Resources:

* [Project Brief](https://docs.google.com/document/d/1Qz94MIqwwAzXYqWzagZZfErU_NU9eMDvoYJ5SYccJvc/edit?usp=sharing): Includes background information, key questions to answer, expectations and ways of working. 

* [NLP Examples in Python](https://github.com/adashofdata/nlp-in-python-tutorial): Repo with example notebooks on using sentiment analysis, topic modeling and text generation. 

* [NLP in the Social Sector](https://ssir.org/articles/entry/how_the_social_sector_can_use_natural_language_processing): Article written by DataKind's own Ben Kinsella on how the social sector can gain insights from text data. 

* [Text Mining with R](https://www.tidytextmining.com/): A great introduction to NLP using R by Julia Silge and David Robinson. 

* [Supervised Machine Learning for Text Analysis](https://smltar.com/): Again, another great NLP book for those R users!

# Data:

Data can be found [here](https://drive.google.com/drive/folders/1FLxdBudO8_vfCk0VEylYRt0UouD7dPAq)

# Scraping Methodology 

Code can be viewed in `./scrapers/`

## Twitter

The twitter public API allows for a query based keyword search to return 100 random samples of tweets containing keywords from the previous 7 days. 

Data was scraped from February 23 - March 3 searching for either a combination of a Covid-19 related keyword and a vaccine related key word, or just containing a hashtag keyword. 

The queries were randomly generated with the above logic in order to obtain unique tweets per API request. 

## Data Available

**twitter_text.csv**: 51K tweets linked to users and metadata

**twitter_hashtag.csv**: Hashtags used per tweet 

**twitter_user.csv**: 37K users who tweeted with profile information 

### Twitter Keywords Used

`covid_keywords = ['covid', 'coronavirus', 'covid-19', 'pandemic', 'covid19', 'corona', 'virus', 'sarscov2']`

`vaccine_keywords = ['vax', 'vaccination', 'pfizer', 'moderna', 'vaccine', 'antivax', 'anti-vax', 'J&J', 'vaccinated', 'doses']`

`hashtags = ['#herdimmunity','#firefauci', '#vaccinated','#vaccineswork', '#bigpharma', '#vaxed', '#vaxxed', '#antivaccine', '#antivax','#immunity','#novaccine', '#vaccine', '#covid', '#coronavirus', '#covid19']`

## Reddit 

Reddit allows a subreddit post and comments to be accessed through their url in a json format. DataKind identified subreddits focused on Covid-19 or vaccines, or was an interest group that had posts about Covid-19 Vaccines and offered diversity of opinion. 

First, we scraped all the posts in pre-identified subreddits and saved posts within those subreddits pertaining to Covid-19 or the Vaccine. Then, we scraped all the comments and replies in those posts. 

Note: All user information is private through the reddit API. 

### Subreddits Scraped 

* r/CoronaVirus 
* r/vaxxhappened
* r/VaccineMyths 
* r/antivax
* r/science
* r/news
* r/conspiracy 
* r/COVID19
* r/nyc
* r/Indiana
* r/Illinois
* r/nashville 
* r/LosAngeles 

### Post Keyword Search

`match_words =['covid-19 vaccine', 'vaccine', 'vaccination', 'coronavirus vaccine', 
               'covid vaccine', 'covid', 'coronavirus', 'virus', 'vax', 'doses', 'pfizer', 'moderna',
               'johnson & johnson', 'J&J', 'vaccinators']`

### Data Available 

**reddit_posts.csv**: All the posts associated with a subreddit that contained a Covid-19 vaccine keyword 

**reddit_comments.csv**: All the comments and replies from the above posts 

