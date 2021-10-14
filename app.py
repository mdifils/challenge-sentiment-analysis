# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 04:33:29 2021

@author: michel
"""

import re
import twint
import pandas as pd
import streamlit as st
import neattext.functions as nfx
from transformers import pipeline

# Instantiating the pretrained model
sentiment_classifier = pipeline('sentiment-analysis')

# App Title
st.title('Twitter Sentiment Analysis')
# Grabbing hashtag from user
text = st.text_input("Enter some data", "")
nb_tweet = st.slider("Number of Tweets: ", min_value=10, max_value=100)

# Useful functions
def get_tweets(search):
    c = twint.Config()
    c.Search = search
    c.Limit = 1000
    c.Pandas = True
    # c.Output = 'output.csv'
    c.Lang = 'en'
    c.Hide_output = True
    c.Count = True
    
    # Run
    twint.run.Search(c)
    df = twint.output.panda.Tweets_df
    return df

def preprocess(s):
    s = nfx.remove_emojis(s)
    s = nfx.remove_emails(s)
    s = nfx.remove_urls(s)
    s = re.sub('[\W]+', ' ', s)
    s = re.sub('\s+', ' ', s)
    return s

def main(text, nb_tweet):
        
    df = get_tweets(text)
    df = df[df.language == 'en'][['username','tweet']]
    data_list = []
    
    for n in range(nb_tweet):
        s = df.iloc[n,1]
        data = {}
        s = preprocess(s)
        data['tweet'] = s
        result = sentiment_classifier(s)
        data['label'] = result[0]['label']
        data['score'] = result[0]['score']
        data_list.append(data)
    
    tweet_df = pd.DataFrame(data_list)
    return tweet_df

submit = st.button("Analyse")

if submit:
    st.dataframe(main(text, nb_tweet))