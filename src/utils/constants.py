DATA_SOURCE_REDDIT = 'Reddit'
DATA_SOURCE_TWITTER = 'Twitter'
DATA_SOURCE_RSS = 'Rss'
DATA_SOURCE_COMBINED = 'Combined'

# Mapping from analysis labels in the selectbox to the methods of the analyzers
ANALYSES_BY_DATA_SOURCE = {
    DATA_SOURCE_REDDIT: {
        'comment_length_per_subreddit': 'Average comment length per subreddit',
        'keyword_per_subreddit': 'Most occurring keywords per subreddit',
        'distribution_number_comments_per_user': 'Distribution of number of comments per user',
        'distribution_number_posts_per_user': 'Distribution of number of posts per user',
        'frequently_used_news_sources': 'Frequently used news sources',
        'count_posts_per_user': 'Most active users',
    },
    DATA_SOURCE_TWITTER: {
        'hashtags_per_trend': 'Common hashtags per trend',
        'create_hashtag_network_from_trend': 'Show hashtag network from trend',
    }, 
    DATA_SOURCE_RSS: {
        'keyword_count_per_feedsource': 'Common keywords for different feed sources',
        'avg_article_length': 'Average article length',
        'tag_similarity': 'Most similar news sources based on their tags',
        'tag_dissimilarity': 'Most dissimilar news sources based on their tags',
        'content_similarity': 'Most similar news sources based on their content',
        'content_dissimilarity': 'Most dissimilar news sources based on their content',
        'published_dist_hour': 'Publication date distribution by hour',
        'published_dist_day': 'Publication date distribution by weekday',
        'headline_stats_per_feed_source': 'Headlines per news source',
        'headline_relative_occurences': 'Influential Topics in Headlines per source'
    }
}

SUBREDDITS = [ 'worldnews', 'news', 'europe', 'politics', 'liberal', 'Conservative',
               'upliftingnews', 'truereddit', 'inthenews', 'nottheonion' ]