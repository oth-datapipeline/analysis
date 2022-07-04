"""
Module containing helper functions for the analyzers
"""
from profanity_check import predict_prob
import pandas as pd


def get_profanity_distribution(data):
    data['profanity'] = predict_prob(data['text'])
    data.drop('text', axis=1, inplace=True)
    data['category'] = pd.cut(data['profanity'] ,[0, 0.25, 0.5, 0.75, 1])
    return data['category'].value_counts(normalize=True)