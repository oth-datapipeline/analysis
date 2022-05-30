from pymongo import MongoClient

class CombinedAnalyzer:

    def __init__(self, mongoclient):
        self._client = mongoclient
        pass