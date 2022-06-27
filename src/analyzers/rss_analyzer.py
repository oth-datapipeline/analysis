import utils.aggregation_pipelines as ap
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud 
import numpy as np
import nltk
import re
from pymongo import MongoClient
import itertools

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')
from nltk.corpus import stopwords

from collections import Counter, defaultdict

class RssAnalyzer:

    static_source_options = None

    def __init__(self, mongoclient):
        """
        Analyzes collected articles from rss feeds

        :param mongoclient: MongoDB connection client
        :type mongoclient: pymongo.MongoClient
        """
        self.collection = mongoclient['data']['rss.articles']

        if not RssAnalyzer.static_source_options:
            RssAnalyzer.static_source_options = pd.DataFrame(ap.rss_headlines(self.collection))['feed_source'].unique().tolist()
        
        self.sources = RssAnalyzer.static_source_options

    def publication_stats(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.rss_publication_stats(self.collection)).sort_values(by=["article_count"], ascending=False)
            result.rename(columns={"article_count": "Number of articles", "feed_source": "News Source"}, inplace=True)
            fig=px.bar(result[:30], x='Number of articles', y='News Source', orientation='h')
            # reverse display order
            fig.update_yaxes(autorange="reversed")
            st.write(fig)
    
    def avg_article_length(self):
        if st.button('Show'):
            result =  pd.DataFrame(ap.rss_avg_article_length(self.collection)).sort_values(by=["avg_article_length"], ascending=False)
            result.rename(columns={"_id": "News Source", 'avg_article_length': 'Average Article Length'}, inplace=True)
            fig=px.bar(result, x='Average Article Length', y='News Source', orientation='h')
            fig.update_yaxes(autorange="reversed")
            st.write(fig)

    def tags_per_source(self):
        limit = int(st.text_input("Limit", value="100"))
        source = st.selectbox(label='News Source', options=tuple(self.sources))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            data = pd.DataFrame(ap.rss_tag_count(self.collection, source))
            result = data.sort_values(by=["count"], ascending=False)
            result = result[:limit]
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["tag"].tolist(), result["count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                #rearrange column order for better output
                cols = result.columns.tolist()
                cols = cols[-2:] + cols[:-2]
                result = result[cols]
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
            fig=px.bar(published_on, x='Weekday', y='Count', orientation='v')
            st.write(fig)

    def published_dist_hour(self):
        if st.button('Show'):
            data = ap.rss_published_distribution_per_hour(self.collection)
            rows = []
            for row in data:
                rows.append([row["_id"], row["count"]])

            published_on = pd.DataFrame(rows, columns=["Hour", "Count"])

            fig=px.bar(published_on, x='Hour', y='Count', orientation='v')
            st.write(fig)

    def headline_stats_per_feed_source(self):
        limit = int(st.text_input("Limit", value="100"))
        source = st.selectbox(label='News Source', options=tuple(self.sources))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
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
            if output_wc == "Yes":
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                occurences_per_source["Count"] = occurences

                result = pd.DataFrame.from_dict(occurences_per_source).fillna(0)
                # print(result)
                result = result.sort_values(by=["Count"], ascending=False)
                result["Word"] = result.index

                #rearrange column order for better output
                cols = result.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                result = result[cols]

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