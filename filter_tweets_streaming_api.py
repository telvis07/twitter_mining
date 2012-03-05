# -*- coding: utf-8 -*-
"""
Uses tweepy to access the twitter filter streaming method. 
Store tweets in couch db.
USAGE: %prog [database] [filter param 1] [filter param 2] ...

$ python filter_tweets_streaming_api.py test twitter
opened test
Track parameters ['twitter']
Delay 0 seconds. created_at 2012-03-05 01:11:45. id_str '17647.....'. tweeter 'sometweeter'. tweet 'I love to tweet!'
Delay 0 seconds. created_at 2012-03-05 01:11:45. id_str '17647.....'. tweeter 'tweeter_guy'. tweet 'Twitter is fun!'
...
"""
import sys
import traceback
import tweepy
import jsonlib2 as json
import couchdb
import time
from datetime import datetime
from twitter__login import login

# global server
server = couchdb.Server('http://localhost:5984')
dbname = sys.argv[1]
try:
    db = server[dbname]
    print "opened",dbname
except couchdb.ResourceNotFound:
    print "creating db",dbname
    db = server.create(dbname)


def get_trace():
    return ''.join(traceback.format_exception(*sys.exc_info()))        

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self):
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        global db # couchdb (global)
        try:
            now = time.mktime(time.gmtime())

            results = {}
            # status info. See: https://dev.twitter.com/docs/api/1/get/statuses/show/%3Aid
            results['text']=status.text.lower()
            results['orig_text']=status.text
            results['id_str']=status.id_str
            results['created_at'] = time.mktime(status.created_at.timetuple())
            results['entities'] = status.entities # urls, hashtags, mentions,
            results['source'] = status.source
            results['geo'] = status.geo
            # user info
            results['user'] = {}
            results['user']['screen_name']=status.author.screen_name
            results['user']['name']=status.author.name
            results['user']['id']=status.author.id_str
            results['user']['url']=status.author.url
            results['user']['location']=status.author.location
            results['user']['friends_count']=status.author.friends_count
            results['user']['followers_count']=status.author.followers_count
            results['user']['statuses_count']=status.author.statuses_count
            results['user']['lang']=status.author.lang
            results['user']['description']=status.author.description
            results['user']['geo_enabled']=status.author.geo_enabled
            results['user']['verified']=status.author.verified

            d = int(now - results['created_at']) # bigger the number, worse the lag cuz the the tweet is older
            print "Delay %d seconds. created_at %s. id_str '%s'. tweeter '%s'. tweet '%s'"%(d,str(status.created_at),results['id_str'],status.author.screen_name,status.text)

            # store in db
            db[results['id_str']] = results
        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e, get_trace()
            pass

    def on_delete(self, status_id, user_id):
        print 'Got DELETE message:', status_id, user_id
        return True # Don't kill the stream
        
    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
        print 'Rate limit', str(track)
        return True # Don't kill the stream

    def on_error(self, status_code):
        print 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print 'Timeout...'
        return True # Don't kill the stream
    
    def on_stall_warning(self, status):
        print "Warning received",str(status)
        return True # Don't kill the stream
        
try:
    # Create a streaming API and set a timeout value of 1 minute
    auth = login()
    streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=60)
    Q = sys.argv[2:] 
    print "Track parameters",str(Q)
    streaming_api.filter(follow=None, track=Q)
except KeyboardInterrupt:
    print "got keyboardinterrupt"
