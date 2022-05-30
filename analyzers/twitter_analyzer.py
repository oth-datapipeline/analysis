from pymongo import MongoClient

class TwitterAnalyzer:

    def __init__(self, mongoclient):
        self._client = mongoclient
        self.collection = self._client['data']['twitter.tweets']

    def hashtags_per_trend(self):
        return self.collection.aggregate([
            {
                '$project': {
                    'hashtags': '$hashtags', 
                    'trend': '$trend'
                }
            }, {
                '$unwind': {
                    'path': '$hashtags'
                }
            }, {
                '$group': {
                    '_id': {
                        'trend': '$trend', 
                        'hashtag': '$hashtags'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$addFields': {
                    '_id.trend': {
                        '$ltrim': {
                            'input': '$_id.trend', 
                            'chars': '#'
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'trend': '$_id.trend', 
                    'hastag': '$_id.hashtag', 
                    'count': '$count', 
                    'is_neq': {
                        '$ne': [
                            {
                                '$strcasecmp': [
                                    '$_id.hashtag', '$_id.trend'
                                ]
                            }, 0
                        ]
                    }
                }
            }, {
                '$match': {
                    'is_neq': True
                }
            }, {
                '$unset': 'is_neq'
            }, {
                '$sort': {
                    'count': -1
                }
            }
        ])