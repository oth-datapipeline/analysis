from datetime import datetime 
import networkx as nx
import itertools
from pyvis.network import Network
import utils.aggregation_pipelines as ap
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
from profanity_check import predict_prob
import plotly.express as px
import plotly.graph_objects as pgo
from wordcloud import WordCloud

class TwitterAnalyzer:
    """
    Analyzes collected tweets

    :param mongoclient: MongoDB connection client
    :type mongoclient: pymongo.MongoClient
    """
    static_trend_options = None
    date_selected = None
    valid_dates = None
    user_types = {'longtime': 3650, 'recent': 30, 'bot': 1}

    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['twitter.tweets']
        if not TwitterAnalyzer.valid_dates:
            datestrings_dicts = list(ap.twitter_valid_dates(self.collection))
            datestrings = list(map(lambda _dict: _dict["_id"], datestrings_dicts))
            # get strings into list of (year,month,day) as ints
            year_month_day_list = [(int(datestring[:4]), int(datestring[4:6]), int(datestring[6:])) for datestring in datestrings]
            dates = list(map(lambda date_triple: datetime(*date_triple), year_month_day_list))
            TwitterAnalyzer.valid_dates = sorted(dates)
            # pick most recent valid date as default
            TwitterAnalyzer.date_selected = TwitterAnalyzer.valid_dates[-1]
        if not TwitterAnalyzer.static_trend_options:
            trends = list(ap.twitter_recent_trends(self.collection, TwitterAnalyzer.date_selected))
            TwitterAnalyzer.static_trend_options = list(map(lambda trend_dict: trend_dict.get('trend'), trends))

    def hashtags_per_trend(self):
        """
        Analyzes how many tweets tagged a trend as a hashtag
        """
        limit = int(st.text_input("Limit", value="30"))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.twitter_hashtags_per_trend(self.collection, limit=limit)))
            st.table(result)

    def most_common_hashtags(self):
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.twitter_common_hashtags(self.collection, limit=limit)))
            result.rename(columns={"_id": "Hashtag", 'count': 'Count'}, inplace=True)
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["Hashtag"].tolist(), result["Count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                fig=px.bar(result, x='Count', y='Hashtag', orientation='h')
                fig.update_yaxes(autorange="reversed")
                st.write(fig)

    def most_liked_hashtags(self):
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.twitter_most_liked_hashtags(self.collection, limit=limit)))
            result.rename(columns={"_id": "Hashtag", 'num_likes': 'Number of Likes'}, inplace=True)
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["Hashtag"].tolist(), result["Number of Likes"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                fig=px.bar(result, x='Number of Likes', y='Hashtag', orientation='h')
                fig.update_yaxes(autorange="reversed")
                st.write(fig)

    def high_interaction_hashtags(self):
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.twitter_high_interaction_hashtags(self.collection, limit=limit)))
            result.rename(columns={"_id": "Hashtag", 'num_replies': 'Number of Replies'}, inplace=True)
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["Hashtag"].tolist(), result["Number of Replies"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                fig=px.bar(result, x='Number of Replies', y='Hashtag', orientation='h')
                fig.update_yaxes(autorange="reversed")
                st.write(fig)

    def create_hashtag_network_from_trend(self):
        """
        Analyzes the networks created by common occurences of hashtags
        """
        with st.form("Trends"):
            TwitterAnalyzer.date_selected = st.date_input("Pick a day to see trends from", min_value=TwitterAnalyzer.valid_dates[0], max_value=TwitterAnalyzer.valid_dates[-1])
            if st.form_submit_button("Confirm Date"): 
                trends = list(ap.twitter_recent_trends(self.collection, TwitterAnalyzer.date_selected))
                TwitterAnalyzer.static_trend_options = list(map(lambda trend_dict: trend_dict.get('trend'), trends))
        st.info(f"Top Trends from {TwitterAnalyzer.date_selected}")
        if not TwitterAnalyzer.static_trend_options:
            st.warning(f"No Trends available for {TwitterAnalyzer.date_selected}. Please choose another date.")
        trend = st.selectbox(label='Trend', options=TwitterAnalyzer.static_trend_options)
        if st.button('Show'):
            result = ap.twitter_get_hashtags_for_specific_trend(
                self.collection, trend)
            G = nx.Graph()
            for i, res in enumerate(result):
                hashtags = res["hashtags"]
                for hashtag in hashtags:
                    G.add_node(hashtag)
                for edge in itertools.combinations(hashtags, 2):
                    G.add_edge(*edge)

            net = Network("800px", "1500px", heading=trend)
            net.from_nx(G)

            html_location = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), 'graph.html')
            net.save_graph(html_location)
            with open(html_location, 'r', encoding='utf-8') as html_file:
                components.html(html=html_file.read(), height=800)
            os.remove(html_location)

    def profanity_like_correlation(self):
        """
        Analyzes the (cor-)relation between tweet profanity, i.e. use of cursewords, and like count.
        """
        if st.button('Show'):
            tweets = list(ap.twitter_tweets_with_likes(self.collection))
            df = pd.DataFrame(tweets)
            
            profanity_scores = predict_prob(df["text"])
            df["profanity_scores"] = profanity_scores

            pd.cut(df["profanity_scores"], [0, 0.25, 0.5, 0.75, 1])

            bins = pd.cut(df["profanity_scores"], bins=[0, 0.25, 0.5, 0.75, 1])
            grouped_bins_avg_likes = df.groupby(bins)['likes'].mean()
            bin_index = grouped_bins_avg_likes.index.values.astype('str')

            fig = px.bar(grouped_bins_avg_likes, x=bin_index, y="likes")
            fig.update_layout(xaxis_title="Profanity Scores",
                              yaxis_title="Average Likes")
            st.write(fig)

    def links_tweet_share(self):
        """
        Analyzes the share of link tweets (videos, images, etc.) in comparison to total tweets.
        """
        if st.button('Show'):
            result = list(ap.twitter_tweets_with_links(self.collection))
            tweet_total = self.collection.estimated_document_count()
            total_count = {"total_count": tweet_total}
            result.append(total_count)

            content = [
                {"count": result[0]["like_count"], "label": "Link Tweets"},
                {"count": tweet_total, "label": "Total Tweets"}
            ]

            df = pd.DataFrame(content)
            fig = px.pie(df, values="count", names="label")
            st.write(fig)

    def tweet_sentiment_analysis(self):
        """
        Analyzes overall sentiment in tweet data.
        """
        if st.button('Show'):
            tweets = list(ap.sentiment_analysis(self.collection))

            all_tweets = 0
            for bucket in tweets:
                all_tweets += bucket['count']

            result = [{'count': bucket['count'], 'label': bucket['bucket']} for bucket in tweets]

            df_result = pd.DataFrame(result)
            fig = px.pie(df_result, values="count", names="label")
            st.write(fig)


    def tweets_overall_on_map(self):
        """
        Creates a map with markers for all geolocations of all tweet data.
        """
        if st.button('Show'):
            tweets = list(ap.twitter_all_tweets_with_geodata(self.collection))

            for tweet in tweets:
                tweet['long'] = tweet['geo']['long']
                tweet['lat'] = tweet['geo']['lat']
                tweet.pop('geo')
            
            df = pd.DataFrame(tweets)
            df['trend'] = df['trend'].apply(lambda trend: trend.lstrip('#'))
            fig = pgo.Figure(data=pgo.Scattergeo(
                lon=df['long'],
                lat=df['lat'],
                text=df['user'] + ": #" + df['trend'],
                mode='markers'
            ))
            st.write(fig)

    def longtime_user_trends(self):
        """
        Analyzes the trends within the group of users with a profile older than 10 years
        """
        st.info("Longtime user = User whose profile was older than 10 years upon creating the tweet")
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            longtime_user_predicate = {"$gte": TwitterAnalyzer.user_types["longtime"]}
            result = pd.DataFrame(ap.twitter_hashtag_count_per_usertype(self.collection, longtime_user_predicate))
            # result = data.sort_values(by=["count"], ascending=False)
            result = result[:limit]
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["hashtag"].tolist(), result["count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                #rearrange column order for better output
                cols = result.columns.tolist()
                cols = cols[-2:] + cols[:-2]
                result = result[cols]
                st.table(result)

    def recent_user_trends(self):
        """
        Analyzes the trends within the group of users with a profile younger than 30 days
        """
        st.info("Recently created user = User whose profile was younger than 30 days upon creating the tweet")
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            longtime_user_predicate = {"$lte": TwitterAnalyzer.user_types["recent"]}
            result = pd.DataFrame(ap.twitter_hashtag_count_per_usertype(self.collection, longtime_user_predicate))
            # result = data.sort_values(by=["count"], ascending=False)
            result = result[:limit]
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["hashtag"].tolist(), result["count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                #rearrange column order for better output
                cols = result.columns.tolist()
                cols = cols[-2:] + cols[:-2]
                result = result[cols]
                st.table(result)


    def bot_trends(self):
        """
        Analyzes the trends within the group of users with a profile younger than 1 day
        """
        st.info("Bot = User whose profile was younger than 1 day upon creating the tweet")
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            longtime_user_predicate = {"$lte": TwitterAnalyzer.user_types["bot"]}
            result = pd.DataFrame(ap.twitter_hashtag_count_per_usertype(self.collection, longtime_user_predicate))
            # result = data.sort_values(by=["count"], ascending=False)
            result = result[:limit]
            if output_wc == "Yes":
                occurences = {tag:count for tag,count in zip(result["hashtag"].tolist(), result["count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True,  output_format='PNG')
            else:
                #rearrange column order for better output
                cols = result.columns.tolist()
                cols = cols[-2:] + cols[:-2]
                result = result[cols]
                st.table(result)

    def likes_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["_id"] = result["_id"].astype(str)
            result.rename(columns={"avg_likes": "Average Likes"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Average Likes', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)

    def followers_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["_id"] = result["_id"].astype(str)
            result.rename(columns={"avg_follower": "Average Number of Followers"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Average Number of Followers', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)

    def quoted_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["_id"] = result["_id"].astype(str)
            result.rename(columns={"avg_quoted": "Average Number of Quotations"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Average Number of Quotations', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)

    def retweets_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["_id"] = result["_id"].astype(str)
            result.rename(columns={"avg_retweets": "Average Number of Retweets"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Average Number of Retweets', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)

    def replies_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["_id"] = result["_id"].astype(str)
            result.rename(columns={"avg_replies": "Average Number of Replies"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Average Number of Replies', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)

    def verified_by_membership_duration(self):
        if st.button('Show'):
            result = pd.DataFrame(ap.twitter_user_stats(self.collection))
            result["verified"] = result["num_verified"] / result["count"]
            result.rename(columns={"verified": "Percentage of verified users"}, inplace=True)
            fig=px.bar(result, x=['< 1 Day', '< 1 Month', '< 1 Year', '< 2 Years', '< 5 Years', '< 10 Years', '< 15 Years', 'More'], y='Percentage of verified users', orientation='v')
            fig.update_xaxes(title_text='Membership Duration')
            st.write(fig)
