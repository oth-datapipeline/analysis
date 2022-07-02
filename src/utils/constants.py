DATA_SOURCE_REDDIT = 'Reddit'
DATA_SOURCE_TWITTER = 'Twitter'
DATA_SOURCE_RSS = 'Rss'
DATA_SOURCE_COMBINED = 'Combined'

# Mapping from analysis labels in the selectbox to the methods of the analyzers
ANALYSES_BY_DATA_SOURCE = {
    DATA_SOURCE_REDDIT: {
        'top_posts': 'Reddit Posts with highest score',
        'most_controversial_posts': 'Most controversial Reddit Posts',
        'subreddit_upvote_ratios': 'Average Upvote ratios per Subreddit',
        'comment_length_per_subreddit': 'Average comment length per subreddit',
        'keyword_per_subreddit': 'Most occurring keywords per subreddit',
        'distribution_number_comments_per_user': 'Distribution of number of comments per user',
        'distribution_number_posts_per_user': 'Distribution of number of posts per user',
        'frequently_used_news_sources': 'Frequently used news sources',
        'count_posts_per_user': 'Most active users',
        'score_dist_by_hour': 'Average Post Score by hour'
    },
    DATA_SOURCE_TWITTER: {
        'most_common_hashtags': 'Common hashtags overall',
        'high_interaction_hashtags': 'Hashtags with most Replies',
        'most_liked_hashtags': 'Most liked Hashtags',
        'hashtags_per_trend': 'Common hashtags per trend',
        'create_hashtag_network_from_trend': 'Show hashtag network from trend',
        'recent_user_trends': 'Trends of recently created users',
        'bot_trends': 'Trends of (possible) bots',
        'longtime_user_trends': 'Trends of longtime users',
        'likes_by_membership_duration': 'Average likes aggregated by membership duration',
        'followers_by_membership_duration': 'Average number of Followers aggregated by membership duration',
        'replies_by_membership_duration': 'Average number of Replies aggregated by membership duration',
        'retweets_by_membership_duration': 'Average number of Retweets aggregated by membership duration',
        'quoted_by_membership_duration': 'Average number of Quotations aggregated by membership duration',
        'verified_by_membership_duration': 'Percentage of verified Users aggregated by membership duration'
    }, 
    DATA_SOURCE_RSS: {
        'publication_stats': 'Number of published articles for the most active sources',
        'avg_article_length': 'Average article length',
        'tag_similarity': 'Most similar news sources based on their tags',
        'tag_dissimilarity': 'Most dissimilar news sources based on their tags',
        'content_similarity': 'Most similar news sources based on their content',
        'content_dissimilarity': 'Most dissimilar news sources based on their content',
        'published_dist_hour': 'Publication date distribution by hour',
        'published_dist_day': 'Publication date distribution by weekday',
        'headline_stats_per_feed_source': 'Headlines per news source',
        'headline_relative_occurences': 'Influential Topics in Headlines per source',
        'tags_per_source': 'Most common Keywords (tags) per news source'
    }, 
    DATA_SOURCE_COMBINED: {
        'keyword_frequency_twitter': 'Occurrences of Twitter trends in news article',
        'keyword_frequency_reddit': 'Occurrences of Reddit keywords in news article',
        'sentiment_analysis': 'Comparison of sentiment in posts and tweets among Reddit and Twitter'
    }
}

SUBREDDITS = [ 'worldnews', 'news', 'europe', 'politics', 'Liberal', 'Conservative',
               'UpliftingNews', 'TrueReddit', 'inthenews', 'nottheonion' ]
