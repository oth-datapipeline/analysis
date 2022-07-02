import utils.aggregation_pipelines as ap
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils.constants as const
import plotly.express as px

# There is a known issue with matplotlib and streamlit, see https://docs.streamlit.io/streamlit-cloud/troubleshooting#limitations-and-known-issues
# Using locks for every figure fixes this issue when running the streamlit app in a Docker environment; running locally there seems to be no issue
from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock

class RedditAnalyzer:
    """
    Analyzes collected reddit posts, comments and users

    :param mongoclient: MongoDB connection client
    :type mongoclient: pymongo.MongoClient
    """
    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['reddit.posts']

    def top_posts(self):
        """
        Analyzes which are the top reddit posts in our database
        """
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_top_posts(self.collection, limit)))
            st.table(result)

    def most_controversial_posts(self):
        """
        Analyzes the most controversial posts by searching for the lowest upvote_ratios
        """
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_controversial_posts(self.collection, limit)))
            st.table(result)

    def subreddit_upvote_ratios(self):
        """
        Analyzes the average upvote ratios for each subreddit 
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_upvote_ratios(self.collection))).sort_values(by=["upvote_ratio"], ascending=False)
            result.rename(columns={'_id': "Subreddit", 'upvote_ratio': 'Average Upvote Ratio'}, inplace=True)
            fig=px.bar(result, x='Subreddit', y='Average Upvote Ratio', orientation='v')
            st.write(fig)

    def comment_length_per_subreddit(self):
        """
        Analyzes how long comments are on average for each collected subreddit
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_comment_length_per_subreddit(self.collection)))
            st.table(result)

    def keyword_per_subreddit(self):
        """
        Analyzes which keywords are commonly used on a specific subreddit
        """
        subreddit = st.selectbox(label='Subreddit', options=tuple(const.SUBREDDITS))
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = list(ap.reddit_keyword_per_subreddit(self.collection, subreddit))
            result = list(filter(lambda row: not row["keyword"].isspace(), result))
            result = pd.DataFrame(result[:limit])
            st.table(result)

    def distribution_number_comments_per_user(self):
        """
        Analyzes the distribution of comments over users (top commentors vs. inactive commentors)
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_comments_per_user(self.collection)))
            labels = result['min_number_of_comments']
            bars = np.arange(len(labels))
            values = result['number_of_users']

            with _lock:
                fig = plt.figure(figsize=(20, 15))
                plt.bar(x=bars, height=values, align='center')
                plt.title('Distribution of number of comments over users')
                plt.xticks(bars, labels)
                plt.ylabel('Number of users')
                plt.xlabel('Number of comments')
                plt.grid(True, axis='y')
                st.pyplot(fig)

    def distribution_number_posts_per_user(self):
        """
        Analyzes the distribution of posts over users (top posters vs. inactive posters)
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_posts_per_user(self.collection)))
            labels = result['min_number_of_posts']
            bars = np.arange(len(labels))
            values = result['number_of_users']

            with _lock:
                fig = plt.figure(figsize=(20, 15))
                plt.bar(x=bars, height=values, align='center')
                plt.title('Distribution of number of posts over users')
                plt.xticks(bars, labels)
                plt.ylabel('Number of users')
                plt.xlabel('Number of posts')
                plt.grid(True, axis='y')
                st.pyplot(fig)

    def frequently_used_news_sources(self):
        """
        Analyzes the news sources that are often used/cited on a specific subreddit
        """
        subreddit = st.selectbox(label='Subreddit', options=tuple(const.SUBREDDITS))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_frequently_used_news_sources(self.collection, subreddit)))
            st.table(result)

    def count_posts_per_user(self):
        """
        Analyzes the most active users / users with the most posts
        """
        limit = int(st.text_input(label='Limit', value='100'))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_count_posts_per_user(self.collection, limit)))
            st.table(result)