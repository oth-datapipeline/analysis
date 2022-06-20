"""
Script which starts an interactive dashboard based on streamlit where different analyses on 
the collected data can be performed 
"""

from analyzers.reddit_analyzer import RedditAnalyzer
from analyzers.twitter_analyzer import TwitterAnalyzer
from analyzers.rss_analyzer import RssAnalyzer
from analyzers.combined_analyzer import CombinedAnalyzer
import utils.constants as const

import logging
import os
from pymongo import MongoClient
import streamlit as st


def main():
    """
    Main Method
    """
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
                                options=const.ANALYSES_BY_DATA_SOURCE.get(data_source),
                                format_func=lambda analysis: const.ANALYSES_BY_DATA_SOURCE.get(data_source).get(analysis))

    except TypeError:
        st.info(f'No analysis implemented for data source {data_source}')
        st.stop()

    analyzer = None
    if data_source == const.DATA_SOURCE_REDDIT:
        analyzer = RedditAnalyzer(client)
    elif data_source == const.DATA_SOURCE_TWITTER:
        analyzer = TwitterAnalyzer(client)
    elif data_source == const.DATA_SOURCE_RSS:
        analyzer = RssAnalyzer(client)
    elif data_source == const.DATA_SOURCE_COMBINED:
        analyzer = CombinedAnalyzer(client)
    else:
        st.warning(f'Data source {data_source} does not exist')
        st.stop()


    # dynamically calling the method corresponding to the analysis that is chosen in the selectbox
    try:
        analysis_method = getattr(analyzer, analysis)
        analysis_method()
    except AttributeError:
        st.info(f'The analysis you chose ({analysis}) is yet to be implemented')


if __name__ == '__main__':
    main()
