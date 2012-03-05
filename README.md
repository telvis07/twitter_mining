# Twitter Mining
This project contains python code for twitter mining.

## Goal
My goal is to find novel ways to find what is important to me on twitter and 
to play with cool tech.

## Dependencies
- CouchDB
- tweepy

## To run
1. Run filter_tweets_streaming_api.py to load tweets to couchdb.

  $ python filter_tweets_streaming_api.py test twitter
  opened test
  Track parameters ['twitter']
  Delay 0 seconds. created_at 2012-03-05 01:11:45. id_str '17647.....'. tweeter 'sometweeter'. tweet 'I love to tweet!'
  Delay 0 seconds. created_at 2012-03-05 01:11:45. id_str '17647.....'. tweeter 'tweeter_guy'. tweet 'Twitter is fun!'
  ...

2. Run a "reporting" script such as top_tweeters_by_follower_count.py. More to come..

  $ python top_tweeters_by_follower_count.py test 2012-03-05
  1329886800 1329973199
  Top 10 tweeters
  0 tweeter1 followercount
  tweetid "look at my awesome tweet"
  1 tweeter2 followercount
  ...

3. That's all for now...
