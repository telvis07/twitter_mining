"""
CouchDB views

tweets_by_created_at - map tweets to date
url_tweets_by_created_at - filter tweets with url entities by date
"""
import couchdb
from couchdb.design import ViewDefinition
import sys

server = couchdb.Server('http://localhost:5984')
db = sys.argv[1]
db = server[db]

def tweets_by_created_at(doc):
    """tweets by timestamp"""
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    if doc.get('user'):
        yield (_date, doc)

view = ViewDefinition('index', 'daily_tweets', tweets_by_created_at, language='python')
view.sync(db)

def url_tweets_by_created_at(doc):
    """filter tweets with links by timestamp"""
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    if doc.get('entities') and doc['entities'].get('urls') and len(doc['entities']['urls']):
        if doc.get('user'):
            yield (_date, doc)

view = ViewDefinition('index', 'daily_url_tweets', url_tweets_by_created_at, language='python')
view.sync(db)

def time_hashtag_mapper(doc):
    """Hash tag by timestamp"""
    from datetime import datetime
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    if doc.get('entities') and doc['entities'].get('hashtags'):
        dt = datetime.fromtimestamp(_date).utctimetuple()
        for hashtag in (doc['entities']['hashtags']):
            yield([dt.tm_year, dt.tm_mon, dt.tm_mday], 
                   hashtag['text'].lower())

view = ViewDefinition('index',
                      'time_hashtags',
                      time_hashtag_mapper, 
                      language='python')
view.sync(db)

def date_hashtag_mapper(doc):
    """tweet by date+hashtag"""
    from datetime import datetime
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    dt = datetime.fromtimestamp(_date).utctimetuple()
    if doc.get('entities') and doc['entities'].get('hashtags'):
        for hashtag in (doc['entities']['hashtags']):
            yield ([dt.tm_year, dt.tm_mon, dt.tm_mday, 
                    hashtag['text'].lower()], 
                   doc['_id'])

def sumreducer(keys, values, rereduce):
    """count then sum"""
    if rereduce:
        return sum(values)
    else:
        return len(values)

view = ViewDefinition('index',
                      'daily_tagcount', 
                      date_hashtag_mapper, 
                      reduce_fun=sumreducer,
                      language='python')
view.sync(db)
