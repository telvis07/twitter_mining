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
import sys, os, re
import ConfigParser
import traceback
import tweepy
import jsonlib2 as json
import couchdb
import time
from datetime import datetime
from twitter__login import login
import logging

FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger('tweepy')
log.setLevel(logging.INFO)

# global server
server = couchdb.Server('http://localhost:5984')
def getdb(dbname):
    try:
        db = server[dbname]
        log.info("opened "+dbname)
    except couchdb.ResourceNotFound:
        log.error("creating db "+dbname)
        db = server.create(dbname)
    return db


def get_trace():
    return ''.join(traceback.format_exception(*sys.exc_info()))        

def filtergroupdict(ma):
    """Remove all entries with values == None"""
    di = filter(lambda x: x[1]!=None, ma.groupdict().items())

    if len(di) != 1:
        return None

    return di[0][0]

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, dbdict, regex):
        tweepy.StreamListener.__init__(self)
        self.i = 0
        self.dbdict = dbdict
        self.match_filter = re.compile(regex,re.VERBOSE|re.MULTILINE).search

    def on_status(self, status):
        try:
            # skip retweets
            if status.retweet_count:
                return True

            txt = status.text.lower()
            for url in status.entities['urls']:
                txt += url['expanded_url']

            ma = self.match_filter(txt)
            if ma:
                ret = filtergroupdict(ma)
                db = self.dbdict[ret] 
                log.debug("Found match for '%s'"%ret)

            # skip if already in couch
            if status.id_str in db:
                return True

            now = time.mktime(time.gmtime())

            results = {}
            # status info. See: https://dev.twitter.com/docs/api/1/get/statuses/show/%3Aid
            results['text']=status.text.lower()
            results['orig_text']=status.text
            results['id_str']=status.id_str
            results['created_at'] = time.mktime(status.created_at.utctimetuple())
            results['created_at_msecs'] = results['created_at']*1000
            results['entities'] = status.entities # urls, hashtags, mentions,
            results['source'] = status.source
            results['geo'] = status.geo
            results['retweet_count'] = status.retweet_count
            results['retweeted'] = status.retweeted
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
#            print json.dumps(results)


            d = int(now - results['created_at']) # bigger the number, worse the lag cuz the the tweet is older

            # store in db
            db[results['id_str']] = results
            self.i+=1

            if self.i%100==0:
                self.i=0
                log.info("Delay %d seconds. created_at %s. id_str '%s'. tweeter '%s'. tweet '%s'"%(d,str(status.created_at),results['id_str'],status.author.screen_name,status.text))

            if d > 60:
                log.error("Too slow... aborting")
                return False
        except Exception, e:
            log.error('Encountered Exception: %s %s'%(e, get_trace()))
            pass

        return True

    def on_delete(self, status_id, user_id):
        log.error("Got DELETE message: '%s' %s"%(status_id, user_id))
        return True # Don't kill the stream
        
    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
        log.error('Got Rate limit Message %s'%str(track))
        return True # Don't kill the stream

    def on_error(self, status_code):
        log.error('Encountered error with status code: %s'%status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        log.error('Timeout...')
        return True # Don't kill the stream
    
    def on_stall_warning(self, status):
        log.error("Got Stall Warning message "+str(status))
        return True # Don't kill the stream
        
streaming_api = None
try:
    fn = sys.argv[1]
except:
    log.error("Please specifiy config file")
    sys.exit(1)

config = ConfigParser.RawConfigParser()
config.read(fn)

dbs = dict()
val = config.get('match','databases')
dbnames = val.split(',') + ['errors']
for dbname in dbnames:
    dbname = dbname.strip()
    log.info("Found %s db"%dbname)
    dbs[dbname] = getdb(dbname)

track = config.get('match','track').split(',')
log.info("Found track='%s'"%track)
regex = config.get('match','regex')
log.info("Found regex='%s'"%regex)

# main loop
interrupted = False
while not interrupted:
    try:
        # oauth dance
        auth = login(config)
        # Create a streaming API and set a timeout value of 1 minute
        streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(dbs,regex), timeout=60, secure=True)
        #Q = sys.argv[1:] 
        Q = track
        log.info("Track parameters %s"%str(Q))
        streaming_api.filter(follow=None, track=Q)
    except KeyboardInterrupt:
        interrupted = True
        log.info("got keyboardinterrupt")
    except Exception, ex:
        err =  "'%s' Error '%s' '%s'"%(str(datetime.now()), str(ex), get_trace())
        log.error(err)
        error = True
    finally:
        log.info("disconnecting...")
        streaming_api.disconnect()
        if not interrupted:
            time.sleep(5)
log.error('EXITING')
