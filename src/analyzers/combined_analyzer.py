import utils.aggregation_pipelines as ap

class CombinedAnalyzer:

    def __init__(self, mongoclient):
        self.rss_collection = mongoclient['data']['rss.articles']
        self.twitter_collection = mongoclient['data']['twitter.tweets']
        self.reddit_collection = mongoclient['data']['reddit.posts']
        self.combined_keyword_collection = mongoclient['data']['combined_keyword_analysis']

    def frequency_twitter_trends_in_news_article(self):
        keywords_for_selection = self.combined_keyword_collection.aggregate(
            [
                {
                    '$match': {
                        '_id.source': {'$eq': ['twitter', 'rss']}
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
                        'count_dates': {'$gte': 5}
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'keyword': '$_id.keyword'
                    }
                }
            ]
        )

        keyword = ... # Selected per droplist from keywords list

        combined_analysis = self.combined_keyword_collection.aggregate(
            [
                {
                    '$match': {
                        '_id.keyword': keyword,
                        '_id.source': {'$eq': ['twitter', 'rss']}
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'source': '$_id.source',
                        'count': '$count'
                    }
                }
            ]
        )
