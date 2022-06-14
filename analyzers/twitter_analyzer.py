import networkx as nx
import itertools
from pyvis.network import Network
import utils.aggregation_pipelines as ap
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd

class TwitterAnalyzer:
    """
    Analyzes collected tweets

    :param mongoclient: MongoDB connection client
    :type mongoclient: pymongo.MongoClient
    """
    static_trend_options = None

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