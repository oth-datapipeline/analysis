from pymongo import MongoClient
import networkx as nx
import itertools
from pyvis.network import Network

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

    def create_hashtag_network_from_trend(self, trend):
        result = self.collection.aggregate([
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

        G = nx.Graph()

        for i,res in enumerate(result):
            hashtags = res["hashtags"]
            for hashtag in hashtags:
                G.add_node(hashtag)
            for edge in itertools.combinations(hashtags, 2):
                G.add_edge(*edge)

        net = Network("800px", "1500px", heading=trend)
        net.from_nx(G)
        net.show("hashtags.html")