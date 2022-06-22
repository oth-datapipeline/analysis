from unittest import result
import utils.aggregation_pipelines as ap
import streamlit as st
import pandas as pd
import numpy as np
import nltk
import re
from pymongo import MongoClient
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity

from nltk.corpus import stopwords

from collections import Counter, defaultdict

class RssAnalyzer:

    def __init__(self, mongoclient):
        """
        Analyzes collected articles from rss feeds

        :param mongoclient: MongoDB connection client
        :type mongoclient: pymongo.MongoClient
        """
        self.collection = mongoclient['data']['rss.articles']
        self.sources = pd.DataFrame(ap.rss_headlines(self.collection))['feed_source'].unique()

    def keyword_count_per_feedsource(self):
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = list(ap.rss_keyword_count_per_feedsource(self.collection, limit))
            st.table(result)

    
    def avg_article_length(self):
        if st.button('Show'):
            result = list(ap.rss_avg_article_length(self.collection))
            st.table(result)


    def tag_similarity(self):
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = self._tag_similarity_wrapper(ascending=False)
            st.table(result[:limit])


    def tag_dissimilarity(self):
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = self._tag_similarity_wrapper(ascending=True)
            st.table(result[:limit])

    def _tag_similarity_wrapper(self, ascending=True):
        data = list(ap.rss_tags(self.collection))
        df = pd.DataFrame(data)
        sources = df["feed_source"].unique()
        pairs = itertools.combinations(sources, 2)
        rows = []
        for pair in pairs:
            first_tags = set(df[df["feed_source"] == pair[0]]["tags"].values[0])
            second_tags = set(df[df["feed_source"] == pair[1]]["tags"].values[0])
            intersection = first_tags.intersection(second_tags)
            union = first_tags.union(second_tags)
            iou_similarity = len(intersection)/len(union)
            rows.append([*pair, iou_similarity])
        
        result = pd.DataFrame(rows, columns=["Source 1", "Source 2", "Similarity"])

        result = result.sort_values(by=["Similarity"], ascending=ascending)
        return result

    def content_similarity(self):
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = self._content_similarity_wrapper(ascending=False)
            st.table(result[:limit])

    def content_dissimilarity(self):
        limit = int(st.text_input("Limit", value="100"))
        if st.button('Show'):
            result = self._content_similarity_wrapper(ascending=True)
            st.table(result[:limit])

    def _content_similarity_wrapper(self, ascending=True):
        data = ap.rss_content(self.collection)
        df = pd.DataFrame(data)

        sws = stopwords.words("english")
        tokenized_articles = list(map(lambda text: nltk.tokenize.wordpunct_tokenize(text), df["content"]))
        cleaned_articles = [list(filter(lambda word: word.lower() not in sws, article)) for article in tokenized_articles]
        df["content"] = [" ".join(cleaned_article) for cleaned_article in cleaned_articles]

        # vectorizer = TfidfVectorizer()
        vectorizer = HashingVectorizer(n_features=100)
        X = vectorizer.fit_transform(df['content']).todense()

        average_embeddings = {}
        sources = df["feed_source"].unique()
        for source in sources:
            ids = df[df["feed_source"] == source].index
            average_embeddings[source] = np.ravel(np.mean(X[ids], axis=0))
                
        pairs = itertools.combinations(sources, 2)
        rows = []
        for pair in pairs:
            x,y = pair
            similaritiy = np.ravel(cosine_similarity(average_embeddings[x].reshape(1,-1),average_embeddings[y].reshape(1,-1)))[0]
            rows.append([*pair, similaritiy])

        result = pd.DataFrame(rows, columns=["Source 1", "Source 2", "Similarity"])

        result = result.sort_values(by=["Similarity"], ascending=ascending)
        return result

    def published_dist_day(self):
        if st.button('Show'):
            data = ap.rss_published_distribution_per_weekday(self.collection)
            
            daysOftheWeek = ("ISO Week days start from 1",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            )

            rows = []
            for row in data:
                rows.append([daysOftheWeek[row["_id"]], row["count"]])
            
            published_on = pd.DataFrame(rows, columns=["Weekday", "Count"])

            st.table(published_on)

    def published_dist_hour(self):
        if st.button('Show'):
            data = ap.rss_published_distribution_per_hour(self.collection)
            rows = []
            for row in data:
                rows.append([row["_id"], row["count"]])

            published_on = pd.DataFrame(rows, columns=["Hour", "Count"])

            st.table(published_on)

    def headline_stats_per_feed_source(self):
        limit = int(st.text_input("Limit", value="100"))
        
        source = st.selectbox(label='News Source', options=tuple(self.sources))
        if st.button('Show'):

            data = ap.rss_headlines(self.collection)
            df = pd.DataFrame(data)

            sws = stopwords.words("english")
            
            occurences_per_source = {}

            tokenized_titles = list(map(lambda text: nltk.tokenize.wordpunct_tokenize(text), df[df['feed_source']==source]["title"]))

            #remove stop words
            cleaned_titles_tokenized = [list(filter(lambda word: word.lower() not in sws, title)) for title in tokenized_titles]
            #remove numbers and special characters
            pattern = re.compile('\W+')
            cleaned_titles_tokenized = [list(filter(lambda word: not (pattern.match(word) or word.isdigit()), title)) for title in cleaned_titles_tokenized]

            #flatten list
            flat_words = []
            for tokens in cleaned_titles_tokenized:
                flat_words += tokens

            lowercase_words = list(map(lambda word: word.lower(), flat_words))
            occurences = Counter(lowercase_words)
            occurences_per_source["Count"] = occurences

            result = pd.DataFrame.from_dict(occurences_per_source).fillna(0)
            # print(result)
            result = result.sort_values(by=["Count"], ascending=False)
            result.index.rename('Word', inplace=True)
            st.info(f"Headline word count for {source}")

            st.table(result[:limit])

    def headline_relative_occurences(self):
        limit = int(st.text_input("Limit", value="100"))
        source_selection = st.selectbox(label='News Source', options=tuple(self.sources))
        if st.button('Show'):

            data = ap.rss_headlines(self.collection)
            df = pd.DataFrame(data)

            sws = stopwords.words("english")
            
            occurences_per_source = {}
            for source in self.sources:
                tokenized_titles = list(map(lambda text: nltk.tokenize.wordpunct_tokenize(text), df[df['feed_source']==source]["title"]))

                #remove stop words
                cleaned_titles_tokenized = [list(filter(lambda word: word.lower() not in sws, title)) for title in tokenized_titles]
                #remove numbers and special characters
                pattern = re.compile('\W+')
                cleaned_titles_tokenized = [list(filter(lambda word: not (pattern.match(word) or word.isdigit()), title)) for title in cleaned_titles_tokenized]

                #flatten list
                flat_words = []
                for tokens in cleaned_titles_tokenized:
                    flat_words += tokens

                lowercase_words = list(map(lambda word: word.lower(), flat_words))
                occurences = Counter(lowercase_words)
                occurences_per_source[source] = occurences


            super_dict = defaultdict(list)
            for d in occurences_per_source.values():
                for k, v in d.items():
                    if k in super_dict.keys():
                        super_dict[k] = super_dict[k] + v
                    else:
                        super_dict[k] = v

            count_threshold = 100

            relative_word_occurences = {k:{} for k in occurences_per_source.keys()}
            rows = []
            for source, d in occurences_per_source.items():
                    for k, v in d.items():
                        if super_dict[k] > count_threshold:
                            relative_probability = float(v/super_dict[k])
                            if relative_probability >= 0.05:
                                relative_word_occurences[source][k] = relative_probability
                                rows.append([source, k, relative_probability])

            result = pd.DataFrame(rows, columns=["Source", "Keyword", "Relative Importance"])
            result = result.sort_values(by=["Relative Importance"], ascending=False)
            # convert score to percentage with 2 decimal points
            result["Relative Importance"] = result["Relative Importance"].apply(lambda score: f"{score*100:.2f}%")

            st.table(result[result["Source"]==source_selection][:limit])