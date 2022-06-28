import utils.aggregation_pipelines as ap

class CombinedAnalyzer:

    def __init__(self, mongoclient):
        self.rss_collection = mongoclient['data']['rss.articles']
        self.twitter_collection = mongoclient['data']['twitter.tweets']
        self.reddit_collection = mongoclient['data']['reddit.posts']        
