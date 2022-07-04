DATA_SOURCE_REDDIT = 'Reddit'
DATA_SOURCE_TWITTER = 'Twitter'
DATA_SOURCE_RSS = 'Rss'
DATA_SOURCE_COMBINED = 'Combined'

# Mapping from analysis labels in the selectbox to the methods of the analyzers
ANALYSES_BY_DATA_SOURCE = {
    DATA_SOURCE_REDDIT: {
        'frequently_used_news_sources': 'Frequently used news sources',
        'top_posts': 'Reddit posts with highest score',
        'most_controversial_posts': 'Most controversial Reddit posts',
        'reddit_posts_comment_sentiment_analysis': 'Sentiment analysis of all posts and comments',
        'subreddit_upvote_ratios': 'Average upvote ratios per subreddit',
        'keyword_per_subreddit': 'Most occurring keywords per subreddit',
        'distribution_number_comments_per_user': 'Distribution of number of comments per user',
        'distribution_number_posts_per_user': 'Distribution of number of posts per user',
        'count_posts_per_user': 'Most active users',
        'comment_length_per_subreddit': 'Average comment length per subreddit',
        'score_dist_by_hour': 'Average post score by hour'
    },
    DATA_SOURCE_TWITTER: {
        'create_hashtag_network_from_trend': 'Show hashtag network from trend',
        'tweets_overall_on_map': 'Show tweet geolocations on map',
        'bot_trends': 'Trends of (possible) bots',
        'recent_user_trends': 'Trends of recently created users',
        'longtime_user_trends': 'Trends of longtime users',
        'most_common_hashtags': 'Common hashtags overall',
        'most_liked_hashtags': 'Most liked hashtags',
        'high_interaction_hashtags': 'Hashtags with most replies',
        'hashtags_per_trend': 'Common hashtags per trend',
        'tweet_sentiment_analysis': 'Sentiment analysis of all tweets',
        'links_tweet_share': 'Share of link tweets in total tweets',
        'profanity_like_correlation': 'Correlation between profanity of tweets and their likes',
        'likes_by_membership_duration': 'Average likes aggregated by membership duration',
        'followers_by_membership_duration': 'Average number of followers aggregated by membership duration',
        'replies_by_membership_duration': 'Average number of replies aggregated by membership duration',
        'retweets_by_membership_duration': 'Average number of retweets aggregated by membership duration',
        'quoted_by_membership_duration': 'Average number of quotations aggregated by membership duration',
        'verified_by_membership_duration': 'Percentage of verified users aggregated by membership duration'
    }, 
    DATA_SOURCE_RSS: {
        'headline_relative_occurences': 'Influential topics in headlines per source',
        'headline_stats_per_feed_source': 'Headlines per news source',
        'tags_per_source': 'Most common keywords (tags) per news source',
        'publication_stats': 'Number of published articles for the most active sources',
        'tag_similarity': 'Most similar news sources based on their tags',
        'tag_dissimilarity': 'Most dissimilar news sources based on their tags',
        'content_similarity': 'Most similar news sources based on their content',
        'content_dissimilarity': 'Most dissimilar news sources based on their content',
        'avg_article_length': 'Average article length',
        'published_dist_hour': 'Publication date distribution by hour',
        'published_dist_day': 'Publication date distribution by weekday'
    }, 
    DATA_SOURCE_COMBINED: {
        'keyword_frequency_twitter': 'Occurrences of Twitter trends in news article',
        'keyword_frequency_reddit': 'Occurrences of Reddit keywords in news article',
        'sentiment_analysis': 'Comparison of sentiment in posts and tweets among Reddit and Twitter',
        'activity_by_hour': 'Activity of data sources by hour',
        'activity_by_weekday': 'Activity of data sources by weekday'
    }
}

SUBREDDITS = [ 'worldnews', 'news', 'europe', 'politics', 'Liberal', 'Conservative',
               'UpliftingNews', 'TrueReddit', 'inthenews', 'nottheonion' ]
