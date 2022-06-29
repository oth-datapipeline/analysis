"""Filling the collection 'combined_keyword_analysis'. Its purpose is the reduction of
computation time for combined analysis
"""
from pymongo import MongoClient
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.aggregation_pipelines as ap

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

    # Twitter
    logging.info('Start upserting from data source Twitter')
    collection = client['data']['twitter.tweets']
    result = ap.upserting_combined_analysis_for_twitter(collection)
    logging.info(result)
    logging.info('Upserting from data source Twitter finished')

    # Reddit
    logging.info('Start upserting from data source Reddit')
    collection = client['data']['reddit.posts']
    result = ap.upserting_combined_analysis_for_reddit(collection)
    logging.info(result)
    logging.info('Upserting from data source Twitter finished')

    # RSS
    logging.info('Start upserting from data source RSS')
    collection = client['data']['rss.articles']
    result = ap.upserting_combined_analysis_for_rss(collection)
    logging.info(result)
    logging.info('Upserting from data source RSS finished')

if __name__ == '__main__':
    main()
