import utils.aggregation_pipelines as ap
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.frontend_components import selectbox_subreddit

class RedditAnalyzer:
    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['reddit.posts']

    def comment_length_per_subreddit(self):
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_comment_length_per_subreddit(self.collection)))
            st.table(result)

    def keyword_per_subreddit(self):
        subreddit = selectbox_subreddit()
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_keyword_per_subreddit(self.collection, subreddit)))
            st.table(result)

    def distribution_number_comments_per_user(self):
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_comments_per_user(self.collection)))
            labels = result['min_number_of_comments']
            bars = np.arange(len(labels))
            values = result['number_of_users']
            fig = plt.figure(figsize=(20, 15))
            plt.bar(x=bars, height=values, align='center')
            plt.title('Distribution of number of comments over users')
            plt.xticks(bars, labels)
            plt.ylabel('Number of users')
            plt.xlabel('Number of comments')
            plt.grid(True, axis='y')
            st.pyplot(fig)

    def distribution_number_posts_per_user(self):
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_posts_per_user(self.collection)))
            labels = result['min_number_of_posts']
            bars = np.arange(len(labels))
            values = result['number_of_users']
            fig = plt.figure(figsize=(20, 15))
            plt.bar(x=bars, height=values, align='center')
            plt.title('Distribution of number of posts over users')
            plt.xticks(bars, labels)
            plt.ylabel('Number of users')
            plt.xlabel('Number of posts')
            plt.grid(True, axis='y')
            st.pyplot(fig)

    def frequently_used_news_sources(self):
        subreddit = selectbox_subreddit()
        if st.button('Show'):
            result = ap.reddit_frequently_used_news_sources(self.collection, subreddit)
            st.table(result)

    def count_posts_per_user(self):
        limit = int(st.text_input(label='Limit', value='100'))
        if st.button('Show'):
            result = ap.reddit_count_posts_per_user(self.collection, limit)
            st.table(result)