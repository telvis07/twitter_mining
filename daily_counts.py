import sys
import couchdb
import time
from datetime import date, datetime

server = couchdb.Server('http://localhost:5984')
dbname = sys.argv[1]
db = server[dbname]

_date  = sys.argv[2]
dt = datetime.strptime(_date,"%Y-%m-%d").utctimetuple()

# get tags for this time interval
_key = [dt.tm_year, dt.tm_mon, dt.tm_mday]
tags = [row.value for row in db.view('index/time_hashtags', key=_key)]
tags = list(set(tags))
print "Tags today",len(tags)
print ""

# get count for date and hashtag
for tag in sorted(tags):
    _key = [dt.tm_year, dt.tm_mon, dt.tm_mday, tag]
    tag_count = [ (row.value) for row in db.view('index/daily_tagcount', key=_key) ]
    print "Found %d %s on %s-%s-%s "%(tag_count[0],tag,_key[0],_key[1],_key[2])
