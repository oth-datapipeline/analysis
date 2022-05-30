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

    def distribution_amount_comments_per_user(self):
        return self.collection.aggregate([
            {
                '$project': {
                    '_id': 0, 
                    'comment': '$comments'
                }
            }, {
                '$unwind': {
                    'path': '$comment'
                }
            }, {
                '$group': {
                    '_id': '$comment.author.name', 
                    'number_of_comments': {
                        '$sum': 1
                    }
                }
            }, {
                '$bucket': {
                    'groupBy': '$number_of_comments', 
                    'boundaries': [
                        1, 2, 5, 10, 20, 100, 200, 500, 1000, 2000
                    ], 
                    'default': 'More', 
                    'output': {
                        'number_of_users': {
                            '$sum': 1
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'min_number_of_comments': '$_id', 
                    'number_of_users': 1
                }
            }
        ])

    def distribution_amount_posts_per_user(self):
        return self.collection.aggregate([
            {
                '$group': {
                    '_id': '$author.name', 
                    'number_of_posts': {
                        '$sum': 1
                    }
                }
            }, {
                '$bucket': {
                    'groupBy': '$number_of_posts', 
                    'boundaries': [ 1, 5, 10, 20, 40, 60, 80, 100, 200, 500, 1000 ], 
                    'default': 'More', 
                    'output': {
                        'number_of_users': {
                            '$sum': 1
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'min_number_of_posts': '$_id', 
                    'number_of_users': 1
                }
            }
        ])

    def frequently_used_news_sources(self):
        return self.collection.aggregate([
            {
                '$project': {
                    '_id': 0, 
                    'subreddit': '$reddit.subreddit', 
                    'domain': '$domain'
                }
            }, {
                '$group': {
                    '_id': '$domain', 
                    'number_of_occurrences': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    'number_of_occurrences': -1
                }
            }
        ])

    def count_posts_per_user(self):
        return self.collection.aggregate([
            {
                '$project': {
                    '_id': 0, 
                    'author_name': '$author.name', 
                    'subreddit': '$reddit.subreddit'
                }
            }, {
                '$group': {
                    '_id': '$author_name', 
                    'num_posts': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    'num_posts': -1
                }
            }
        ])
