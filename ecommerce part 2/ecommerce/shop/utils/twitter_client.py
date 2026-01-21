import tweepy
from django.conf import settings


def get_twitter_client():
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)


def tweet_with_optional_image(message, image_path=None):
    api = get_twitter_client()
    api.update_status(status=message)
