from pymongo import MongoClient

class RssAnalyzer:

    def __init__(self, mongoclient):
        self._client = mongoclient
        self.collection = self._client['data']['rss.articles']

    def keyword_count_per_feedsource(self):
        return self.collection.aggregate([
            {
                '$project': {
                    'feed_source': '$feed_source', 
                    'tag': '$tags'
                }
            }, {
                '$unwind': {
                    'path': '$tag'
                }
            }, {
                '$group': {
                    '_id': {
                        'tag': '$tag', 
                        'feed_source': '$feed_source'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    'count': -1
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'feed_source': '$_id.feed_source', 
                    'tag': '$_id.tag', 
                    'count': '$count'
                }
            }
        ])
    
    def rss_avg_article_length(self):
        return self.collection.aggregate([
            {
                '$project': {
                    'text': '$content', 
                    'feed_source': '$feed_source'
                }
            }, {
                '$group': {
                    '_id': '$feed_source', 
                    'avg_article_length': {
                        '$avg': {
                            '$strLenCP': '$text'
                        }
                    }
                }
            }, {
                '$sort': {
                    'avg_article_length': -1
                }
            }
        ])