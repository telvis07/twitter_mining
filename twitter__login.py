#!/usr/bin/env python
"""Tweepy oauth dance"""
import tweepy

def login(config):
    """The config file should contain:

    [auth]
    CONSUMER_KEY = ...
    CONSUMER_SECRET = ...
    ACCESS_TOKEN = ...
    ACCESS_TOKEN_SECRET = ...
    """

    CONSUMER_KEY = config.get('auth','CONSUMER_KEY')
    CONSUMER_SECRET = config.get('auth','CONSUMER_SECRET')

    # Get these values from the "My Access Token" link located in the
    # margin of your application details, or perform the full OAuth
    # dance

    ACCESS_TOKEN = config.get('auth','ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = config.get('auth','ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Note: Had you wanted to perform the full OAuth dance instead of using
    # an access key and access secret, you could have uses the following 
    # four lines of code instead of the previous line that manually set the
    # access token via auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    # 
    # auth_url = auth.get_authorization_url(signin_with_twitter=True)
    # webbrowser.open(auth_url)
    # verifier = raw_input('PIN: ').strip()
    # auth.get_access_token(verifier)
    return auth
