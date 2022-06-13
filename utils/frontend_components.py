"""
Module containing reusable streamlit components
"""

import utils.constants as const
import streamlit as st
import utils.aggregation_pipelines as ap

def selectbox_subreddit():
    return st.selectbox(label='Subreddit', options=tuple(const.SUBREDDITS))

def selectbox_twitter_trends(twitter_collection):
    trend_filter = st.radio(label='Filter trends',
                            options=(const.TWITTER_TREND_FILTER_RECENT, 'Other'))
    if trend_filter == const.TWITTER_TREND_FILTER_RECENT:
        trends = tuple(ap.twitter_recent_trends(twitter_collection))
        print(trends)
        return st.selectbox(label='Trend',
                            options=trends)
    
    # TODO: implement filter for trends with the most tweets