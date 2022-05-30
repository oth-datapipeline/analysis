from pymongo import MongoClient

class RedditAnalyzer:

    def __init__(self, mongoclient):
        self._client = mongoclient
        self.collection = self._client['data']['reddit.posts'] 

    def comment_length_per_subreddit(self):
        return self.collection.aggregate([
            {
                '$project': {
                    'comment': '$comments.text', 
                    'sub': '$reddit.subreddit'
                }
            }, {
                '$unwind': {
                    'path': '$comment'
                }
            }, {
                '$group': {
                    '_id': '$sub', 
                    'avg': {
                        '$avg': {
                            '$strLenCP': '$comment'
                        }
                    }
                }
            }, {
                '$sort': {
                    'avg': 1
                }
            }
        ])

    def reddit_keyword_per_sub(self):
        return self.collection.aggregate([
            {
                '$project': {
                    'subreddit': '$reddit.subreddit', 
                    'keyword': '$keywords'
                }
            }, {
                '$unwind': {
                    'path': '$keyword'
                }
            }, {
                '$match': {
                    'keyword': {
                        '$ne': ''
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'subreddit': '$subreddit', 
                        'keyword': '$keyword'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'subreddit': '$_id.subreddit', 
                    'keyword': '$_id.keyword', 
                    'count': '$count'
                }
            }, {
                '$sort': {
                    'count': -1
                }
            }
        ])