#!/usr/bin/env python
import tweepy
import ConfigParser
import os, sys

class Listener(tweepy.StreamListener):
    def on_status(self, status):
        print "screen_name='%s' tweet='%s'"%(status.author.screen_name, status.text)

def login(config):
    """Tweepy oauth dance
    The config file should contain:

    [auth]
    CONSUMER_KEY = ...
    CONSUMER_SECRET = ...
    ACCESS_TOKEN = ...
    ACCESS_TOKEN_SECRET = ...
    """
    CONSUMER_KEY = config.get('auth','CONSUMER_KEY')
    CONSUMER_SECRET = config.get('auth','CONSUMER_SECRET')
    ACCESS_TOKEN = config.get('auth','ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = config.get('auth','ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth


fn=sys.argv[1]
config = ConfigParser.RawConfigParser()
config.read(fn)
try:
    auth = login(config)
    streaming_api = tweepy.streaming.Stream(auth, Listener(), timeout=60)
    # San Francisco area.
    streaming_api.filter(follow=None, locations=[-122.75,36.8,-121.75,37.8]) 
except KeyboardInterrupt:
    print "got keyboardinterrupt"
