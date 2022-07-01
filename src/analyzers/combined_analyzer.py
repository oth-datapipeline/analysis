import utils.aggregation_pipelines as ap
from profanity_check import predict_prob
import streamlit as st
import pandas as pd

class CombinedAnalyzer:

    def __init__(self, mongoclient):
        self.rss_collection = mongoclient['data']['rss.articles']
        self.twitter_collection = mongoclient['data']['twitter.tweets']
        self.reddit_collection = mongoclient['data']['reddit.posts']    

    def compare_profanity_score_reddit_twitter(self):
        if st.button('Show'):
            # tweets = pd.DataFrame(self.twitter_collection.find({}, {'_id': 0, 'text': 1}))
            # tweets['profanity'] = predict_prob(tweets['text'])
            # tweets.drop('text', axis=1, inplace=True)
            # tweets['category'] = pd.cut(tweets['profanity'], [0, 0.25, 0.5, 0.75, 1])
            # num_tweets_by_profanity_category = tweets.groupby(by='category').count()
            # tweet_fractions = tweets['category'].value_counts(normalize=True)

            reddit_comments = pd.DataFrame(ap.reddit_get_all_comments(self.reddit_collection))
            reddit_comments['profanity'] = predict_prob(reddit_comments['text'])
            reddit_comments.dropna(inplace=True)
            reddit_comments['category'] = pd.cut(reddit_comments['profanity'], [0, 0.25, 0.5, 0.75, 1])
            print(reddit_comments['category'])
            # reddit_fractions = reddit_comments['category'].value_counts(normalize=True)
