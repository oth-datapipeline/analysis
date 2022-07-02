import networkx as nx
import itertools
from pyvis.network import Network
import utils.aggregation_pipelines as ap
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
from profanity_check import predict_prob
import plotly.express as px
import plotly.graph_objects as pgo


class TwitterAnalyzer:
    """
    Analyzes collected tweets

    :param mongoclient: MongoDB connection client
    :type mongoclient: pymongo.MongoClient
    """
    static_trend_options = None
    static_geodata_trend_options = None

    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['twitter.tweets']
        if not TwitterAnalyzer.static_trend_options:
            trends = list(ap.twitter_recent_trends(self.collection))
            TwitterAnalyzer.static_trend_options = list(map(lambda trend_dict: trend_dict.get('trend'), trends))

    def hashtags_per_trend(self):
        """
        Analyzes how many tweets tagged a trend as a hashtag
        """
        result = pd.DataFrame(list(ap.twitter_hashtags_per_trend(self.collection)))
        if st.button('Show'):
            st.table(result)

    def create_hashtag_network_from_trend(self):
        """
        Analyzes
        """
        trend = st.selectbox(label='Trend', options=TwitterAnalyzer.static_trend_options)
        if st.button('Show'):
            result = ap.twitter_get_hashtags_for_specific_trend(self.collection, trend)
            G = nx.Graph()
            for i, res in enumerate(result):
                hashtags = res["hashtags"]
                for hashtag in hashtags:
                    G.add_node(hashtag)
                for edge in itertools.combinations(hashtags, 2):
                    G.add_edge(*edge)

            net = Network("800px", "1500px", heading=trend)
            net.from_nx(G)
        
            html_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'graph.html')
            net.save_graph(html_location)
            with open(html_location, 'r', encoding='utf-8') as html_file:
                components.html(html=html_file.read(), height=800)
            os.remove(html_location)

    def profanity_like_correlation(self):
        if st.button('Show'):

            tweets = list(ap.twitter_tweets_with_likes(self.collection))
            df = pd.DataFrame(tweets)

            profanity_scores = predict_prob(df["text"])
            df["profanity_scores"] = profanity_scores

            pd.cut(df["profanity_scores"], [0, 0.25, 0.5, 0.75, 1])

            bins = pd.cut(df["profanity_scores"], bins=[0, 0.25, 0.5, 0.75, 1])
            grouped_bins_avg_likes = df.groupby(bins)['likes'].mean()
            bin_index = grouped_bins_avg_likes.index.values.astype('str')

            fig=px.bar(grouped_bins_avg_likes, x=bin_index, y="likes")
            fig.update_layout(xaxis_title="Profanity Scores", yaxis_title="Average Likes")
            st.write(fig)

    def links_tweet_share(self):
        if st.button('Show'):
            result = list(ap.twitter_tweets_with_links(self.collection))
            tweet_total = self.collection.estimated_document_count()
            total_count = { "total_count": tweet_total }
            result.append(total_count)

            content = [
                {"count": result[0]["like_count"], "label": "Link Tweets"},
                {"count": tweet_total, "label": "Total Tweets"}
            ]

            df = pd.DataFrame(content)
            print(df)

            fig = px.pie(df, values="count", names="label")
            st.write(fig)

    def tweet_sentiment_analysis(self):
        if st.button('Show'):
            tweets = list(ap.sentiment_analysis(self.collection))

            all_tweets = 0
            for bucket in tweets:
                all_tweets += bucket['count']

            result = {'negative': {}, 'neutral': {}, 'positive': {}}

            for bucket in tweets:
                result[bucket['bucket']]['Twitter tweets'] = bucket['count'] / all_tweets

            df_result = pd.DataFrame(result).reset_index().rename({'index': 'Sources'}, axis=1)
            print(df_result)

            fig = px.bar(df_result, x='Sources', y=['negative', 'neutral', 'positive'])
            st.write(fig)

    def tweets_trends_on_map(self):
        trends_with_geodata = ap.twitter_trends_of_geodata_tweets(self.collection)
        TwitterAnalyzer.static_geodata_trend_options = list(map(lambda trend_dict: trend_dict.get('trend'), trends_with_geodata))
        trend = st.selectbox(label='Trend', options=TwitterAnalyzer.static_geodata_trend_options)
        
        if st.button('Show'):
            tweets = list(ap.twitter_geodata_createdat_by_trend(self.collection, trend))
            for tweet in tweets:
                tweet['long'] = tweet['geo']['long']
                tweet['lat'] = tweet['geo']['lat']
                tweet.pop('geo')
            print(tweets)
            df = pd.DataFrame(tweets)
            fig = pgo.Figure(data=pgo.Scattergeo(
                lon = df['long'],
                lat = df['lat'],
                text = df['user'],
                mode = 'markers'
            ))
            st.write(fig)

        