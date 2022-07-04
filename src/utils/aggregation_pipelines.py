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


def reddit_get_all_comments(collection):
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
        }, 
        {
            '$project': {
                'text': '$comment.text'
            }
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

def upserting_combined_analysis_for_twitter(collection):
    """
    Aggregation pipeline for filling the collection 'combined_keyword_analysis' from Twitter

    :param collection: MongoDB collection for twitter tweets
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate(
        [
            {
                '$addFields': {
                    'trend_and_hashtags': {
                        '$concatArrays': [
                            [
                                {
                                    '$ltrim': {
                                        'input': '$trend', 
                                        'chars': '#'
                                    }
                                }
                            ], '$hashtags'
                        ]
                    }
                }
            }, {
                '$project': {
                    'created_at_trunc': {
                        '$dateFromParts': {
                            'year': {
                                '$year': '$created_at'
                            }, 
                            'month': {
                                '$month': '$created_at'
                            }, 
                            'day': {
                                '$dayOfMonth': '$created_at'
                            }
                        }
                    }, 
                    'trend_and_hashtags': 1
                }
            }, {
                '$unwind': {
                    'path': '$trend_and_hashtags'
                }
            }, {
                '$group': {
                    '_id': {
                        'keyword': {
                            '$toLower': '$trend_and_hashtags'
                        }, 
                        'date': '$created_at_trunc', 
                        'source': 'twitter'
                    }, 
                    'ids': {
                        '$addToSet': '$_id'
                    }
                }
            }, {
                '$project': {
                    'count': {
                        '$size': '$ids'
                    }
                }
            }, {
                '$match': {
                    'count': {
                        '$gte': 10
                    }
                }
            }, {
                '$merge': {
                    'into': {
                        'db': 'analysis',
                        'coll': 'combined_keyword_analysis'
                    },
                    'on': '_id', 
                    'whenMatched': 'replace', 
                    'whenNotMatched': 'insert'
                }
            }
        ]
    )

def upserting_combined_analysis_for_reddit(collection):
    """
    Aggregation pipeline for filling the collection 'combined_keyword_analysis' from Reddit

    :param collection: MongoDB collection for reddit posts
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate(
        [
            {
                '$project': {
                    'created_trunc': {
                        '$dateFromParts': {
                            'year': {
                                '$year': '$created'
                            }, 
                            'month': {
                                '$month': '$created'
                            }, 
                            'day': {
                                '$dayOfMonth': '$created'
                            }
                        }
                    }, 
                    'keywords': 1
                }
            }, {
                '$unwind': {
                    'path': '$keywords'
                }
            }, {
                '$match': {
                    'keywords': {
                        '$ne': ''
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'keyword': {
                            '$toLower': '$keywords'
                        }, 
                        'date': '$created_trunc', 
                        'source': 'reddit'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$match': {
                    'count': {
                        '$gte': 3
                    }
                }
            }, {
                '$merge': {
                    'into': {
                        'db': 'analysis',
                        'coll': 'combined_keyword_analysis'
                    }, 
                    'on': '_id', 
                    'whenMatched': 'replace', 
                    'whenNotMatched': 'insert'
                }
            }
        ]
    )

def upserting_combined_analysis_for_rss(collection):
    """
    Aggregation pipeline for filling the collection 'combined_keyword_analysis' from RSS

    :param collection: MongoDB collection for rss articles
    :type collection: pymongo.collection.Collection
    :return: result cursor
    :rtype: pymongo.command_cursor.CommandCursor
    """
    return collection.aggregate(
        [
            {
                '$project': {
                    'published': 1, 
                    'type': {
                        '$type': '$published'
                    }, 
                    'tags': 1
                }
            }, {
                '$match': {
                    'published': {
                        '$ne': None
                    }, 
                    'type': 'date'
                }
            }, {
                '$project': {
                    'published_trunc': {
                        '$dateFromParts': {
                            'year': {
                                '$year': '$published'
                            }, 
                            'month': {
                                '$month': '$published'
                            }, 
                            'day': {
                                '$dayOfMonth': '$published'
                            }
                        }
                    }, 
                    'tags': 1
                }
            }, {
                '$unwind': {
                    'path': '$tags'
                }
            }, {
                '$group': {
                    '_id': {
                        'keyword': {
                            '$toLower': '$tags'
                        }, 
                        'date': '$published_trunc', 
                        'source': 'rss'
                    }, 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$match': {
                    'count': {
                        '$gte': 3
                    }
                }
            }, {
                '$merge': {
                    'into': {
                        'db': 'analysis',
                        'coll': 'combined_keyword_analysis'
                    }, 
                    'on': '_id', 
                    'whenMatched': 'replace', 
                    'whenNotMatched': 'insert'
                }
            }
        ]
    )

def keywords_in_news_article(collection, source):
    assert source in ['twitter', 'reddit']
    return collection.aggregate(
        [
            {
                '$match': {
                    '_id.source': {
                        '$in': [
                            source, 'rss'
                        ]
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'keyword': '$_id.keyword', 
                        'date': '$_id.date'
                    }, 
                    'count_sources': {
                        '$sum': 1
                    }
                }
            }, {
                '$match': {
                    'count_sources': 2
                }
            }, {
                '$group': {
                    '_id': '$_id.keyword', 
                    'count_dates': {
                        '$sum': 1
                    }
                }
            }, {
                '$match': {
                    'count_dates': {
                        '$gte': 3
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'keyword': '$_id'
                }
            }, {
                '$sort': {
                    'keyword': 1
                }
            }
        ]
    )

def keyword_frequency_in_news_article(collection, keyword, source):
    assert source in ['twitter', 'reddit']
    return collection.aggregate(
        [
            {
                '$match': {
                    '_id.keyword': keyword,
                    '_id.source': {'$in': [source, 'rss']}
                }
            }, {
                '$project': {
                    '_id': 0,
                    'date': '$_id.date',
                    'source': '$_id.source',
                    'count': '$count'
                }
            }
        ]
    )

def sentiment_analysis(collection):
    return collection.aggregate(
        [
            {
                '$match': {
                    'sentiment.compound': {
                        '$exists': True
                    }
                }
            }, {
                '$project': {
                    'bucket': {
                        '$switch': {
                            'branches': [
                                {
                                    'case': {
                                        '$lt': [
                                            '$sentiment.compound', -0.05
                                        ]
                                    }, 
                                    'then': 'negative'
                                }, {
                                    'case': {
                                        '$gt': [
                                            '$sentiment.compound', 0.05
                                        ]
                                    }, 
                                    'then': 'positive'
                                }
                            ], 
                            'default': 'neutral'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$bucket', 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$project': {
                    '_id': 0,
                    'bucket': '$_id', 
                    'count': '$count'
                }
            }, {
                '$sort': {
                    'bucket': 1
                }
            }
        ]
    )

def sentiment_analysis_comments(collection):
    return collection.aggregate(
        [
            {
                '$unwind': {
                    'path': '$comments'
                }
            }, {
                '$match': {
                    'comments.sentiment.compound': {
                        '$exists': True
                    }
                }
            }, {
                '$project': {
                    'bucket': {
                        '$switch': {
                            'branches': [
                                {
                                    'case': {
                                        '$lt': [
                                            '$comments.sentiment.compound', -0.05
                                        ]
                                    }, 
                                    'then': 'negative'
                                }, {
                                    'case': {
                                        '$gt': [
                                            '$comments.sentiment.compound', 0.05
                                        ]
                                    }, 
                                    'then': 'positive'
                                }
                            ], 
                            'default': 'neutral'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$bucket', 
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$project': {
                    '_id': 0,
                    'bucket': '$_id', 
                    'count': '$count'
                }
            }, {
                '$sort': {
                    'bucket': 1
                }
            }
        ]
    )
