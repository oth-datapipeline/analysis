import utils.aggregation_pipelines as ap
import streamlit as st
import pandas as pd
import utils.constants as const
import plotly.express as px
from wordcloud import WordCloud

class RedditAnalyzer:
    """
    Analyzes collected reddit posts, comments and users

    :param mongoclient: MongoDB connection client
    :type mongoclient: pymongo.MongoClient
    """
    def __init__(self, mongoclient):
        self.collection = mongoclient['data']['reddit.posts']

    def top_posts(self):
        """
        Analyzes which are the top reddit posts in our database
        """
        limit = int(st.text_input("Limit", value="30"))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_top_posts(self.collection, limit)))
            st.table(result)

    def most_controversial_posts(self):
        """
        Analyzes the most controversial posts by searching for the lowest upvote_ratios
        """
        limit = int(st.text_input("Limit", value="30"))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_controversial_posts(self.collection, limit)))
            st.table(result)

    def subreddit_upvote_ratios(self):
        """
        Analyzes the average upvote ratios for each subreddit 
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_upvote_ratios(self.collection))).sort_values(by=["upvote_ratio"], ascending=False)
            result.rename(columns={'_id': "Subreddit", 'upvote_ratio': 'Average Upvote Ratio'}, inplace=True)
            fig=px.bar(result, x='Subreddit', y='Average Upvote Ratio', orientation='v')
            st.write(fig)

    def comment_length_per_subreddit(self):
        """
        Analyzes how long comments are on average for each collected subreddit
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_comment_length_per_subreddit(self.collection))).sort_values(by='average_comment_length', ascending=False)
            result.rename(columns={ 'subreddit': 'Subreddit', 'average_comment_length': 'Average comment length' }, inplace=True)
            fig = px.bar(result, x='Average comment length', y='Subreddit', orientation='h')
            fig.update_yaxes(autorange='reversed')
            st.write(fig)

    def keyword_per_subreddit(self):
        """
        Analyzes which keywords are commonly used on a specific subreddit
        """
        subreddit = st.selectbox(label='Subreddit', options=tuple(const.SUBREDDITS))
        limit = int(st.text_input("Limit", value="30"))
        output_wc = st.radio("Output as Wordcloud", options=tuple(["Yes", "No"]))
        if st.button('Show'):
            result = list(ap.reddit_keyword_per_subreddit(self.collection, subreddit))
            result = list(filter(lambda row: not row["keyword"].isspace(), result))
            result = pd.DataFrame(result[:limit]).sort_values(by='count', ascending=False)
            if output_wc == 'Yes':
                occurences = { keyword : count for keyword, count in zip(result["keyword"].tolist(), result["count"].tolist())}
                wc = WordCloud().fit_words(occurences)
                st.image(wc.to_array(), use_column_width=True, output_format='PNG')
            else:
                result.rename(columns={'keyword': 'Keyword', 'count': 'Number of occurrences'}, inplace=True)
                fig = px.bar(result[:limit], x='Number of occurrences', y='Keyword', orientation='h')
                fig.update_yaxes(autorange='reversed')
                st.write(fig)

    def score_dist_by_hour(self):
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_score_by_hour(self.collection)))
            result.rename(columns={"hour": "Hour", "score": "Score"}, inplace=True)
            fig=px.bar(result, x='Hour', y='Score', orientation='v')
            st.write(fig)

    def distribution_number_comments_per_user(self):
        """
        Analyzes the distribution of comments over users (top commentors vs. inactive commentors)
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_comments_per_user(self.collection)))
            result.rename(columns={'min_number_of_comments': 'Number of comments', 'number_of_users': 'Number of users'}, inplace=True)
            fig = px.bar(result, x='Number of comments', y='Number of users')
            fig.update_xaxes(type='category')
            st.write(fig)

    def distribution_number_posts_per_user(self):
        """
        Analyzes the distribution of posts over users (top posters vs. inactive posters)
        """
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_distribution_number_posts_per_user(self.collection)))
            result.rename(columns={'min_number_of_posts': 'Number of posts', 'number_of_users': 'Number of users'}, inplace=True)
            fig = px.bar(result, x='Number of posts', y='Number of users')
            fig.update_xaxes(type='category')
            st.write(fig)

    def frequently_used_news_sources(self):
        """
        Analyzes the news sources that are often used/cited on a specific subreddit
        """
        limit = int(st.text_input("Limit", value="30"))
        subreddit = st.selectbox(label='Subreddit', options=tuple(const.SUBREDDITS))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_frequently_used_news_sources(self.collection, subreddit))).sort_values(by='number_of_occurrences', ascending=False)
            result.rename(columns={'domain': 'Domain', 'number_of_occurrences': 'Number of occurrences'}, inplace=True)
            fig = px.bar(result[:limit], x='Number of occurrences', y='Domain', orientation='h')
            fig.update_yaxes(autorange='reversed')
            st.write(fig)

    def count_posts_per_user(self):
        """
        Analyzes the most active users / users with the most posts
        """
        limit = int(st.text_input(label='Limit', value='30'))
        if st.button('Show'):
            result = pd.DataFrame(list(ap.reddit_count_posts_per_user(self.collection, limit)))
            result.rename(columns={'_id': 'Username', 'num_posts': 'Number of posts'}, inplace=True)
            fig = px.bar(result, x='Number of posts', y='Username', orientation='h')
            fig.update_yaxes(autorange='reversed')
            st.write(fig)

    def reddit_posts_comment_sentiment_analysis(self):
        """
        Analyzes overall sentiment for all submissions and their respective comments across all scraped reddit data.
        """
        if st.button('Show'):
            reddit_posts = list(ap.sentiment_analysis(self.collection))
            reddit_comments = list(ap.reddit_sentiment_analysis_comments(self.collection))

            all_posts = 0
            for bucket in reddit_posts:
                all_posts += bucket['count']

            all_comments = 0
            for bucket in reddit_comments:
                all_comments += bucket['count']

            result = {'negative': {}, 'neutral': {}, 'positive': {}}

            for bucket in reddit_posts:
                result[bucket['bucket']]['Reddit posts'] = bucket['count'] / all_posts

            for bucket in reddit_comments:
                result[bucket['bucket']]['Reddit comments'] = bucket['count'] / all_comments

            df_result = pd.DataFrame(result).reset_index().rename({'index': 'Sources'}, axis=1)

            fig = px.bar(df_result, x='Sources', y=['negative', 'neutral', 'positive'])
            st.write(fig)
