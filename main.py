# File for calling the analysis methods and starting streamlit

from analyzers.reddit_analyzer import RedditAnalyzer
from analyzers.twitter_analyzer import TwitterAnalyzer
from analyzers.rss_analyzer import RssAnalyzer
from analyzers.combined_analyzer import CombinedAnalyzer

import os
from pymongo import MongoClient

if __name__ == '__main__':
    user = os.environ["MONGO_INITDB_ROOT_USERNAME"] 
    pw = os.environ["MONGO_INITDB_ROOT_PASSWORD"] 
    mongo_host = os.environ["MONGO_HOST"]
    client = MongoClient(     mongo_host,     27017,     username=user,     password=pw)
    
    
    reddit_analyzer = RedditAnalyzer(client)
    twitter_analyzer = TwitterAnalyzer(client)
    rss_analyzer = RssAnalyzer(client)

    # method call for demonstration
    avg_comment_length = reddit_analyzer.comment_length_per_subreddit()
    