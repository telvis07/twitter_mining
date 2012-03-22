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
import sys,time,os
import couchdb
from datetime import datetime
import ConfigParser
from optparse import OptionParser

def format_message(data):
    """Format dict as unicode string"""
    di = [(nm,data[nm]['follower_count']) for nm in data]
    di.sort(key=lambda x: x[1], reverse=True)
    out = u""
    for row in di:
        screen_name, count = row
        out += u"%(screen_name)s <http://twitter.com/%(screen_name)s>\n"%{'screen_name':screen_name}
        for tweetid in data[screen_name]['tweets']:
            tweet = data[screen_name]['tweets'][tweetid]
            out += u"  %s (https://twitter.com/%s/status/%s)\n"%(tweet,screen_name,tweetid)
        out+=u'\n'
    return out 

def run(db, date, limit=10):
    """Query a couchdb view for tweets. Sort in memory by follower count.
    Return the top 10 tweeters and their tweets"""
    print "Finding top %d tweeters"%limit

    dt = datetime.strptime(date,"%Y-%m-%d")
    stime=int(time.mktime(dt.timetuple()))
    etime=stime+86400-1
    tweeters = {}
    tweets = {}
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
    out = {}
    for i in range(limit):
        screen_name = di[i][0]
        followers_count = di[i][1]
        out[screen_name] = {}
        out[screen_name]['follower_count'] = followers_count
        out[screen_name]['tweets'] = {}
        # print i,screen_name,followers_count
        for tweetid in tweets[screen_name]:
            orig_text = db[tweetid]['orig_text']
            # print tweetid,orig_text
            out[screen_name]['tweets'][tweetid] = orig_text

    return out

if __name__=='__main__':
    op = OptionParser('%prog <date> [OPTIONS]')
    op.add_option('-c','--config',dest='config',
                  default=os.path.join(os.environ['HOME'],'conf', 'twitter_mining.cfg'),
                  help='Path to configuration file')
    op.add_option('-d', '--dbname', dest='dbname',
                  help='CouchDB database name')
    op.add_option('-b','--dbhost', dest='dbhost',
                  default='http://localhost:5984',
                  help='Url to CouchDB host')
    op.add_option('--dry-run', dest='dryrun', action='store_true',
                   default=False,  
                   help="don't really send the email")
    (opts, args) = op.parse_args()

    if not opts.config \
       or not opts.dbname \
       or not opts.dbhost \
       or len(args) != 1:
        print "Missing required options"
        op.print_help()
        sys.exit(1)

    server = couchdb.Server(opts.dbhost)
    db = server[opts.dbname]
    date = args[0]

    # run report
    output = run(db, date)
    output = format_message(output)

    from mail_results import send_email 
    config = ConfigParser.RawConfigParser()
    config.read(opts.config)
    subj = "Top tweets by follower count for '%s'"%date
    send_email(config, config.get(opts.dbname,'to'), subj, output, dryrun=opts.dryrun)
