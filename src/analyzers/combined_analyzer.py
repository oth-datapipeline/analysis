import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import utils.aggregation_pipelines as ap

class CombinedAnalyzer:

    def __init__(self, mongoclient):
        self.rss_collection = mongoclient['data']['rss.articles']
        self.twitter_collection = mongoclient['data']['twitter.tweets']
        self.reddit_collection = mongoclient['data']['reddit.posts']
        self.combined_keyword_collection = mongoclient['analysis']['combined_keyword_analysis']

    def keyword_frequency_twitter(self):
        keywords = [k['keyword'] for k in list(ap.keywords_in_news_article(self.combined_keyword_collection, source='twitter'))]
        keyword = st.selectbox(label='Trend or hashtag', options=tuple(keywords))

        if st.button('Show'):
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            combined_analysis = list(ap.keyword_frequency_in_news_article(self.combined_keyword_collection, keyword, source='twitter'))
            list_twitter = []
            list_rss = []
            for entry in combined_analysis:
                if entry['source'] == 'twitter':
                    list_twitter.append({'date': str(entry['date']), 'count': entry['count']})
                else:
                    list_rss.append({'date': str(entry['date']), 'count': entry['count']})
            df_twitter = pd.DataFrame(list_twitter).sort_values('date')
            df_rss = pd.DataFrame(list_rss).sort_values('date')
            fig.add_trace(
                go.Scatter(x=list(df_twitter['date']), y=list(df_twitter['count']), name='Twitter tweets'), secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=list(df_rss['date']), y=list(df_rss['count']), name='News article'), secondary_y=True
            )
            fig.update_yaxes(title_text='Occurrences of keyword in Twitter tweets', secondary_y=False)
            fig.update_yaxes(title_text='Occurrences of keyword in News article', secondary_y=True)
            st.write(fig)

    def keyword_frequency_reddit(self):
        keywords = [k['keyword'] for k in list(ap.keywords_in_news_article(self.combined_keyword_collection, source='reddit'))]
        keyword = st.selectbox(label='Keyword', options=tuple(keywords))

        if st.button('Show'):
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            combined_analysis = list(ap.keyword_frequency_in_news_article(self.combined_keyword_collection, keyword, source='reddit'))
            list_reddit = []
            list_rss = []
            for entry in combined_analysis:
                if entry['source'] == 'reddit':
                    list_reddit.append({'date': str(entry['date']), 'count': entry['count']})
                else:
                    list_rss.append({'date': str(entry['date']), 'count': entry['count']})
            df_reddit = pd.DataFrame(list_reddit).sort_values('date')
            df_rss = pd.DataFrame(list_rss).sort_values('date')
            fig.add_trace(
                go.Scatter(x=list(df_reddit['date']), y=list(df_reddit['count']), name='Reddit posts'), secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=list(df_rss['date']), y=list(df_rss['count']), name='News article'), secondary_y=True
            )
            fig.update_yaxes(title_text='Occurrences of keyword in Reddit posts', secondary_y=False)
            fig.update_yaxes(title_text='Occurrences of keyword in News article', secondary_y=True)
            st.write(fig)

    def sentiment_analysis(self):
        if st.button('Show'):
            twitter_tweets = list(ap.sentiment_analysis(self.twitter_collection))
            reddit_posts = list(ap.sentiment_analysis(self.reddit_collection))
            reddit_comments = list(ap.sentiment_analysis_comments(self.reddit_collection))
            all_tweets = 0
            for bucket in twitter_tweets:
                all_tweets += bucket['count']
            all_posts = 0
            for bucket in reddit_posts:
                all_posts += bucket['count']
            all_comments = 0
            for bucket in reddit_comments:
                all_comments += bucket['count']
            result = {'negative': {}, 'neutral': {}, 'positive': {}}
            for bucket in twitter_tweets:
                result[bucket['bucket']]['Twitter tweets'] = bucket['count'] / all_tweets
            for bucket in reddit_posts:
                result[bucket['bucket']]['Reddit posts'] = bucket['count'] / all_posts
            for bucket in reddit_comments:
                result[bucket['bucket']]['Reddit comments'] = bucket['count'] / all_comments
            df_result = pd.DataFrame(result).reset_index().rename({'index': 'Sources'}, axis=1)
            print(df_result)
            fig = px.bar(df_result, x='Sources', y=['negative', 'neutral', 'positive'])
            st.write(fig)
