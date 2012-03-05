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
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    if doc.get('user'):
        yield (_date, doc)

view = ViewDefinition('index', 'daily_tweets', tweets_by_created_at, language='python')
view.sync(db)

def url_tweets_by_created_at(doc):
    if doc.get('created_at'):
        _date = doc['created_at']
    else:
        _date = 0 # Jan 1 1970

    if doc.get('entities') and doc['entities'].get('urls') and len(doc['entities']['urls']):
        if doc.get('user'):
            yield (_date, doc)

view = ViewDefinition('index', 'daily_url_tweets', url_tweets_by_created_at, language='python')
view.sync(db)

