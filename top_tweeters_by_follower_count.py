#!/usr/bin/env python
"""
Use couchdb view to rank tweets by author's follower count.

USAGE %prog [database] [date in YYYY-MM-DD format]
$ python top_tweeters_by_follower_count.py test 2012-03-05
1329886800 1329973199
Top 10 tweeters
0 tweeter1 followercount
tweetid "look at my awesome tweet"
1 tweeter2 followercount
...
"""
import sys,time
import couchdb
from couchdb.design import ViewDefinition
import jsonlib2 as json
from datetime import datetime

def main(db, date):
    dt = datetime.strptime(date,"%Y-%m-%d")
    stime=int(time.mktime(dt.timetuple()))
    etime=stime+86400-1
    tweeters = {}
    tweets = {}
    print stime,etime
    for row in db.view('index/daily_tweets', startkey=stime, endkey=etime):
        status = row.value
        screen_name = status['user']['screen_name']
        followers_count = status['user']['followers_count']
        tweeters[screen_name] = int(followers_count)
        if not tweets.has_key(screen_name):
            tweets[screen_name] = []
        tweets[screen_name].append(status['id_str'])

    # sort
    di = tweeters.items()
    di.sort(key=lambda x: x[1], reverse=True)
    print "Top 10 tweeters"
    for i in range(10):
        screen_name = di[i][0]
        followers_count = di[i][1]
        print i,screen_name,followers_count
        for tweetid in tweets[screen_name]:
            print tweetid, db[tweetid]['orig_text']

if __name__=='__main__':
    server = couchdb.Server('http://localhost:5984')
    db = sys.argv[1]
    db = server[db]
    date = sys.argv[2]

    import views # create indexes if not already
    main(db, date)
