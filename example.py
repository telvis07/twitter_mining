#!/usr/bin/env python
import tweepy
import ConfigParser
import os

class Listener(tweepy.StreamListener):
    def on_status(self, status):
        print "screen_name='%s' tweet='%s'"%(status.author.screen_name, status.text)

def login():
    config = ConfigParser.RawConfigParser()
    fn = 'twitter_mining.cfg'
    config.read(fn)

    CONSUMER_KEY = config.get('auth','CONSUMER_KEY')
    CONSUMER_SECRET = config.get('auth','CONSUMER_SECRET')
    ACCESS_TOKEN = config.get('auth','ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = config.get('auth','ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth


try:
    auth = login()
    streaming_api = tweepy.streaming.Stream(auth, Listener(), timeout=60)
    streaming_api.filter(follow=None, track=['technical','elvis'])
except KeyboardInterrupt:
    print "got keyboardinterrupt"
