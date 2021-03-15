# Topics Modeling & Sentiment Analysis

These notebooks focus on topic modeling & sentiment analysis with the Twitter dataset. The whole process is below and the corresponding notebooks are labeled. View the notebooks to jump into deeper detail.

This is a beginning step. Now that the topics have been created, I believe the next step would be to conduct EDA with each topic. Some examples of quesitons that could be answered are:
- Further topic modeling could be explored. What topics are brought up within the 'Vaccine' or 'Opinion' topics? Or what topics are brought up in negative sentiment and/or highly subjective tweets?
- What are the most popular ngrams in each of the topics?
- What are the most popular hashtags in each topic?
- What is the most popular question in each topic?
- What are the links that are shared the most?
- What news outlet (link) is used for the the most positive/negative tweets? And what were the headlines of those articles?
- What is the mean sentiment when certain @mentions are used?
- What is the sentiment around the Vaccine geographically?



# Topic Modeling

There were 3 topics that were found overall. LDA models were also made with 4 and 5 topics. Further topics subdivided the topics that I labeled as 'Opinion' and 'Pandemic Updates'. 

- The topics that were further divided out may help benefit with further analysis. One of the topics labeled 'other' were tweets that seemed to be captured because the tweet had a keyword that was searched to scrape the data. Such as talking about  beer 'corona' or a tweet about a drink that can boost 'immunity'. Keeping this topic, then removing it, may prove useful if further EDA is used.

## Preprocessing
###### Notebook 1.0 exploration

Listed here are a few of the steps to preprocessing that were completed. 

- Stopword were ***taken out*** from spaCy's initial stop_word list. This was, hopefully, to capture ngrams and phrases that might help model the topics. Words like 'Don't get the vaccine', 'Everyone shouldn't get the vaccine'. While in processing many of the words would have been stripped away.
- Adjusted different spellings of 'Coronavirus'
- Removed twitter text such as 'ht' or 'rt'
- Hashtags, except for the top 15 used in the dataset, were removed from the dataset. The hashtags were removed and placed in a separate column in the dataframe. This step might require some additional time to determine what the best course of action is. Some users use a very large amount of hashtags, and the model initially placed tweets with many hashtags (and @ mentions) together. I assume this was because of the '#' symbol, and the words are usually concatenated together (ie. #firefauci). Some users use hashtags while in the text in place of a word. (ie *'I received my #covid vaccine today!'*). I decided to leave in the most commonly used hashtags, as they may have meaning to them. The others I remoed for the LDA model, then I removed the actualy symbol '#' from the dataset before feeding into the model. 
- URL links were removed, and placed in a separate column in the dataset
- @mentions were removed, except for the top 30 used mentions. For similar reasons above. The mentions in some instances will give more context for the model to create topics, and on the other hand many of the @mentions were used very scarcely. The '@' symbol was also removed.
- n-grams: 2-6 ngrams were created

## Latent Topics
###### Notebook 02 - LDA-Modeling & Notebook 025-LDA Exploration
When plotting the coherent values, it was a bit tough to determine the amount of topics. The coherence values spike at 3 topic, but continue to rise at 4 and 5 topics. Generally, three topics which I labeled as Vaccine Information, Pandemic Information, Opinion works well. Definitions & example tweets below.
1. **Vaccine distribution**, studies, update on manufacturing, release etc. <br>
        <blockquote>#BJP #TNwithRahulGandhi <br>
                    #BBCnews #CNN #g20 #COP26 <br>
                    #imf #WHO #WTO #Chennai #INDvsENG #TomarModiKisanVirodhi #COVID19Vaccine #COVID19 #Corona #coronavirus #CoronaVaccine #CoronavirusVaccine #biden<br><br>
                    US #FDA which is Gold Standard for drug approvals has cleared #j&amp;j for emerg. use 
        </blockquote>
2. **Coronavirus**, pandemic, vaccine updates & reports (doses administered, deaths, cases etc.)
     <blockquote> COVID-19 vaccination doses administrated per 100 people:<br>
                🇮🇱 84.9<br>
                🇸🇨 67.2<br>
                🇦🇪 58.0<br>
                🇵🇼 39.3<br>
                🇬🇧 27.8<br>
                🇺🇸 19.6<br>
                🇧🇭 17.1<br>
                🇨🇱 16.3<br>
                🇲🇭 16.1<br>
                🇲🇻 16.0<br>
                🇷🇸 14.2<br>
                🇲🇹 13.2<br>
                🇫🇲 10.7<br>
                🇩🇰 8.8<br>
                🇹🇷 8.7<br>
                🇨🇭 7.9<br>
                🇮🇸 7.7<br>
                🇷🇴 7.4<br>
                🇳🇴 7.3<br>
                🇲🇦 7.3<br>
                🇱🇹 7.3<br>
                🇫🇷 5.7<br>
                🌍 2.75<br><br>
                #COVID19<br>
                #COVIDVaccine<br><br>
                24/02/2021<br>
                (OWID) <br>
 </blockquote>
 
3.  **Opinion** on Coronavirus, Vaccine, Politics
     <blockquote> OK : Bill advising DT in 2017 on Vax💉<br>
                         Safety .<br>
                First bio-weapon release Sars-02 in<br>
                2002 failed to catch on in Europe<br>
                trial run.<br>
                Genetically re-program for Global release 2019 .<br>
                16 years HiV Mers Ebola inbetween <br>
                Contaminate 💦H2O GModify food chain for 5.2b virus deaths https://t.co/p7SwLJEyta https://t.co/RGRsd9VVqx <br>
 </blockquote><br><br>
 Adding further topics subdivided the above three topics adding the below topics.
 
4. **"Other"** | Seems to capture a few different types of tweets
   - Words/tweets that may not directly relate to covid. (similar to topic 0.0 of 4 topics) Such as: <br>
   - It also captures repeated (or slightly altered) tweets. And reapeated Words within a tweet, tweets with mixed language <br> 
   - Some Coronavirus updates that have words and numbers vs full sentences:<br>
   - Lists where words don't necessarily follow a structured sentence. Seen in a list of hashtags, @mentions,  and link/retweet or a tweet with a list of symptoms, a list of city locations where vaccine is available.<br>
    <blockquote>Can some one book this Malome... 😁<br><br>
                @zodwalibram 😏 @moonchildsanelly<br><br>
                #mzanzimemes #mzanzi_beauty #mzanzihumor #zodwawabantu #moonchildsanelly #savanna #corona #sahiphopmusic #amapianoisalifestyle https://t.co/1HZpmkcxiu </blockquote>
  
 5.  **Wellness** | Immunity, health, recomendations. These tweets seem to include tweets about health and wellness, and ways to boost immunity. That do not directly pertain to covid. It could be because 'immunity' was a keyword that was used to capture these tweets.There are also tweets with repeated words/phrases, similar to what was found in topic 0.0 in the model with 4 topics.
     <blockquote>  Wellness Wednesday: Efficiency and Sustainability <br><br>
                    #WellnessWednesday #silage #density #microbasics #immunity #microbiome #natural #solutions #feedgooddogood #guthealth #converge #dairy #beef #poultry #aquaculture #chickens #calves #sheep #goats #pigs #health #gobacktobasics https://t.co/AkU4Cr0YZa <br>
 </blockquote><br><br>
 The last two topics, althought did not have many tweets in them, could be used to filter tweets that could have been collected but do not pertain to the pandemic. <br><br>
 Models for 3, 4, and 5 topics were used for expoloration andn sentiment analysis in the remaining notebooks.

## Sentiment Analysis
###### Notebook 03-Sentiment Analysis

- Data was imported and Vader & Texblob sentiment analysis was completed by tweet and by day.
- Different cutoffs were tried to label a tweet as positive or negative. There was difficulty in finding the best cutoff using either Textblob and/or Vader. 
	- ***DNN or some other ML sentiment may work better to capture sarcasm in the tweet data
- Subjectivity was included into the analysis***
- Sentiment for the whole dataset by day was graphed
- Sentiment by day per topic was graphed
- Distribution of sentiment among and within topics were graphed
- Different levels of subjectivity were graphed (High, Med, Low), with example tweets.
- Viewed texts with different levels of subjectivity, sentiment in different topics. For example a highly subjective, neutral sentiment in the Pandemic topic.
- Other questions were asked and answered in the dataset
	- Who was the most positive and negative twitter users with the most followers, and what were their tweets?
	- Which twitter users were the most positive or negative?
	- 

## Topics over time
###### Notebook 03-01-topics-over-time
Viewed the topic distribution over time. For this graph and many others that look at a variable over time, it would be interesting to see these distributions across a longer time span.


