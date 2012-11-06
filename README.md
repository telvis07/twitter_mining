# Twitter Mining
This project contains python code for twitter mining..

## Goal
My goal is to find novel ways to summarize topics and trends on twitter.

## Dependencies
- [Python](http://www.python.org/)
- [CouchDB](http://couchdb.apache.org/)
- [tweepy](https://github.com/tweepy/tweepy)

## To run
1. Run filter_tweets_streaming_api.py to store tweets. The delay shows when your consumer is too slow.
<pre>
   $ /usr/bin/python filter_tweets_streaming_api.py twitter_mining.cfg
</pre>

2. Run views.py to create indexes on your couchdb database  
<pre>
    $ python views.py test
</pre>

3. Run a "reporting" script such as top_tweeters_by_follower_count.py and send a summary email of tweets  
<pre>
    $ python top_tweeters_by_follower_count.py -d test 2012-03-05 --dry-run  
    Top 10 tweeters  
    tweeter1  
     "look at my awesome tweet"  
    tweeter2  
     "i'm colder than a polar bears toe nails"  
</pre>
