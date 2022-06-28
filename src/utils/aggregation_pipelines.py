"""
Module for MongoDB aggregation pipelines on different collections
"""
from datetime import datetime, timedelta


def reddit_comment_length_per_subreddit(collection):
    """
    Aggregation pipeline for comment_length_per_subreddit

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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
                'average_comment_length': {
                    '$avg': {
                        '$strLenCP': '$comment'
                    }
                }
            }
        }, {
            '$sort': {
                'avg': 1
            }
        }, {
            '$project': {
                '_id': 0,
                'subreddit': '$_id',
                'average_comment_length': '$average_comment_length'
            }
        }
    ])


def reddit_keyword_per_subreddit(collection, subreddit):
    """
    Aggregation pipeline for keyword_per_subreddit

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
        {
            '$project': {
                'subreddit': '$reddit.subreddit', 
                'keyword': '$keywords'
            }
        }, {
            '$match': {
                'subreddit': subreddit
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
                    'keyword': '$keyword'
                }, 
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'keyword': '$_id.keyword', 
                'count': '$count'
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ])


def reddit_distribution_number_posts_per_user(collection):
    """
    Aggregation pipeline for distribution_number_posts_per_user

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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

def reddit_distribution_number_comments_per_user(collection):
    """
    Aggregation pipeline for distribution_number_comments_per_user

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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
                    'boundaries': [ 1, 2, 5, 10, 20, 100, 200, 500, 1000, 2000  ], 
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


def reddit_frequently_used_news_sources(collection, subreddit):
    """
    Aggregation pipeline for frequently_used_news_sources

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
        {
            '$project': {
                '_id': 0, 
                'subreddit': '$reddit.subreddit', 
                'domain': '$domain'
            }
        }, {
            '$match': {
                'subreddit': subreddit
            }
        },{
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
        }, {
            '$project': {
                '_id': 0,
                'domain': '$_id',
                'number_of_occurrences': '$number_of_occurrences'
            }
        }
    ])


def reddit_count_posts_per_user(collection, limit):
    """
    Aggregation pipeline for count_posts_per_user

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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
        }, {
            '$limit': limit
        }
    ])


def twitter_hashtags_per_trend(collection):
    """
    Aggregation pipeline for hashtags_per_trend

    :param collection: MongoDB collection for tweets
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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


def twitter_get_hashtags_for_specific_trend(collection, trend):
    """
    Aggregation pipeline for get_hashtags_for_specific_trend(collection, trend):


    :param collection: MongoDB collection for tweets
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
        {
            '$match': {
                'trend': {
                    '$eq': trend
                }
            }
        }, {
            '$project': {
                '_id': 0, 
                'hashtags': '$hashtags'
            }
        }
    ])


def twitter_recent_trends(collection):
    """
    Aggregation pipeline for fetching current trends

    :param collection: MongoDB collection for tweets
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    today = datetime.now()
    delta = timedelta(days=3)
    start_date = today - delta
    return collection.aggregate([
        {
            '$match': {
                'created_at': { '$gte': start_date }
            }
        }, {
            '$group': {
                '_id': {
                    'trend': '$trend',
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
            '$limit': 100
        }, {
            '$project': {
                '_id': 0,
                'trend': '$_id.trend'
            }
        }
    ])

def rss_publication_stats(collection):
    return collection.aggregate([
        {
            '$project': {
                'feed_source': '$feed_source'
            }
        },
        {
            '$group': {
                '_id': '$feed_source', 
                'article_count': {
                    '$sum': 1
                }
            }
        },
        {
            '$project': {
                    '_id': 0, 
                    'feed_source': '$_id', 
                    'article_count': 1
            }
        }
    ]
    )

def rss_avg_article_length(collection):
    """
    Aggregation pipeline for avg_article_length

    :param collection: MongoDB collection for rss articles
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate([
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

def rss_tags(collection):
    return collection.aggregate([
            {
                '$project': {
                    'feed_source': 1, 
                    'tags': 1
                }
            }, {
                '$unwind': {
                    'path': '$tags'
                }
            }, {
                '$group': {
                    '_id': '$feed_source', 
                    'tags': {
                        '$push': '$tags'
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'feed_source': '$_id', 
                    'tags': 1
                }
            }
        ])

def rss_tag_count(collection, source):
    return collection.aggregate([
            {
                '$match': {
                    'feed_source': {'$eq' : source}
                }
            },
            {
                '$project': {
                    'feed_source': 1, 
                    'tags': 1
                }
            }, {
                '$unwind': {
                    'path': '$tags'
                }
            }, {
                '$group': {
                    '_id': {'feed_source': '$feed_source','tag': '$tags'}, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'feed_source': '$_id.feed_source',
                    'tag': '$_id.tag', 
                    'count': 1
                }
            }
        ])

def rss_content(collection):
    return collection.aggregate([
            {
                '$project': {
                    'feed_source': 1,
                    'content': 1
                }
            }
        ])

def rss_published_distribution_per_weekday(collection):
    return collection.aggregate([
            {
                '$match': {
                    'published': {
                        '$type': 9
                    }
                }
            }, {
                '$project': {
                    'day': {
                        '$isoDayOfWeek': '$published'
                    }
                }
            }, {
                '$group': {
                    '_id': '$day', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ])

def rss_published_distribution_per_hour(collection):
    return collection.aggregate([
            {
                '$match': {
                    'published': {
                        '$type': 9
                    }
                }
            }, {
                '$project': {
                    'day': {
                        '$hour': '$published'
                    }
                }
            }, {
                '$group': {
                    '_id': '$day', 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    '_id': 1
                }
            }
        ])

def rss_headlines(collection):
    return collection.aggregate([
            {
                '$project': {
                    'title': 1,
                    'feed_source': 1
                }
            }
        ])