import sys
import couchdb
import time
from datetime import date, datetime

server = couchdb.Server('http://localhost:5984')
dbname = sys.argv[1]
db = server[dbname]

_date  = sys.argv[2]
dt = datetime.strptime(_date,"%Y-%m-%d")
stime=int(time.mktime(dt.utctimetuple()))
etime=stime+86400-1

# get tags for this time interval
tags = [row.value for row in db.view('index/time_hashtags',
                                     startkey=stime,endkey=etime)]
tags = list(set(tags))
print "Tags today",set(tags)
print ""

# get count for date and hashtag
d = dt.timetuple()
for tag in sorted(tags):
    _key = [d.tm_year, d.tm_mon, d.tm_mday, tag]
    tag_count = [ (row.value) for row in db.view('index/daily_tagcount', 
                                                              key=_key) ][0]
    print "Found %d %s on %s-%s-%s "%(tag_count,tag,_key[0],_key[1],_key[2])
