import utils.aggregation_pipelines as ap

class RssAnalyzer:

    def __init__(self, mongoclient):
        """
        Analyzes collected articles from rss feeds

        :param mongoclient: MongoDB connection client
        :type mongoclient: pymongo.MongoClient
        """
        self.collection = mongoclient['data']['rss.articles']

    def keyword_count_per_feedsource(self):
        result = ap.rss_keyword_count_per_feedsource(self.collection)
    
    def avg_article_length(self):
        result = ap.rss_avg_article_length(self.collection)