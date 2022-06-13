import networkx as nx
import itertools
from pyvis.network import Network
import utils.aggregation_pipelines as ap
import streamlit as st
import streamlit.components.v1 as components
import os
from utils.frontend_components import selectbox_twitter_trends

class TwitterAnalyzer:

    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['twitter.tweets']

    def hashtags_per_trend(self):
        result = ap.twitter_hashtags_per_trend(self.collection)

    def create_hashtag_network_from_trend(self):
        trend = selectbox_twitter_trends(self.collection)
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