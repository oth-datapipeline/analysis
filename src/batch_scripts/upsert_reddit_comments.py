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

    reddit_collection = client['data']['reddit.posts']
    reddit_comments_collection = client['analysis']['reddit_comments']
    logging.info('Start upserting Reddit comments')
    result = list(ap.get_all_reddit_comments(reddit_collection))
    duplicates = 0
    success = 0
    for row in result:
        try:
            reddit_comments_collection.insert_one({'comment': row.get('text')})
            success = success + 1
        except Exception:
            duplicates = duplicates + 1

    logging.info('Upserting of Reddit comments finished')
    print(f'{success} entries inserted, {duplicates} Duplicates were found')

if __name__ == '__main__':
    main()