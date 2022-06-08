"""File for calling the analysis methods and starting streamlit"""

from analyzers.reddit_analyzer import RedditAnalyzer
from analyzers.twitter_analyzer import TwitterAnalyzer
from analyzers.rss_analyzer import RssAnalyzer
from analyzers.combined_analyzer import CombinedAnalyzer
import utils.constants as const

import logging
import os
import pandas as pd
from pymongo import MongoClient
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np


def main():
    try:
        user = os.environ["MONGO_INITDB_ROOT_USERNAME"] 
        pw = os.environ["MONGO_INITDB_ROOT_PASSWORD"] 
        mongo_host = os.environ["MONGO_HOST"]
        client = MongoClient(mongo_host, 27017, username=user, password=pw)
    except KeyError:
        logging.error('Environment variables for connecting to MongoDB not set')
        return


    data_source = st.sidebar.radio(label='Select the data source you want to analyze',
                                   options=(const.DATA_SOURCE_REDDIT, const.DATA_SOURCE_TWITTER, const.DATA_SOURCE_RSS, const.DATA_SOURCE_COMBINED))

    try:
        analysis = st.selectbox(label=f'Select the analysis you want to perform on the {data_source} dataset',
                                options=const.analyses_by_data_source.get(data_source),
                                format_func=lambda analysis: const.analyses_by_data_source.get(data_source).get(analysis))

    except TypeError:
        st.info(f'No analysis implemented for data source {data_source}')

    if data_source == const.DATA_SOURCE_REDDIT:
        analyzer = RedditAnalyzer(client)
        if analysis == 'comment_length_per_subreddit':
            if st.button('Show'):
                result = pd.DataFrame(list(analyzer.comment_length_per_subreddit()))
                st.table(result)
        elif analysis == 'distribution_number_comments_per_user':
            if st.button('Show'):
                result = pd.DataFrame(list(analyzer.distribution_number_comments_per_user()))
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
        else:
            st.info(f'The analysis you chose ({analysis}) is yet to be implemented')

    elif data_source == const.DATA_SOURCE_TWITTER:
        analyzer = TwitterAnalyzer(client)
        if analysis == 'create_hashtag_network_from_trend':
            # TODO: make as selectbox
            trend = st.text_input('Trend', value='')
            if st.button('Show'):
                graph = analyzer.create_hashtag_network_from_trend(trend)
                html_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'graph.html')
                graph.save_graph(html_location)
                with open(html_location, 'r', encoding='utf-8') as html_file:
                    components.html(html=html_file.read(), height=435)
                os.remove(html_location)
        else:
            st.info(f'The analysis you chose ({analysis}) is yet to be implemented')


if __name__ == '__main__':
    main()
