import couchdb
import time
from datetime import date, datetime
from couchdb.design import ViewDefinition

def time_tag_mapper(doc):
    from datetime import datetime
    if doc.get('tag'):
        dt = datetime.fromtimestamp(doc['time']).utctimetuple()
        yield ([dt.tm_year, dt.tm_mon, dt.tm_mday], doc['tag'])

def tag_mapper(doc):
    from datetime import datetime
    if doc.get('tag') and doc.get('time'):
        dt = datetime.fromtimestamp(doc['time']).utctimetuple()
        yield ([dt.tm_year, dt.tm_mon, dt.tm_mday, doc['tag']], doc['_id'])

def tag_sumreducer(keys, values, rereduce):
    if rereduce:
        return sum(values)
    else:
        return len(values)

def main():
    server = couchdb.Server('http://localhost:5984')
    dbname = 'test'
    try:
        server.delete(dbname)
        print "Deleted %s"%dbname
    except:
        pass

    ttime = 1334187642
    db = server.create(dbname)
    data = [('1','one', 'foo', ttime),
            ('2','two','bar', ttime),
            ('3','three','foo',ttime),
            ('4','three','bar',ttime),
            ('5','three','bar', ttime+86400)]
    for d in data:
        key, tag, txt, tt = d
        print "Input",key, tag, txt, tt
        row = {'tag':tag, 'text':txt.lower(), 'time': tt}
        db[key] = row

    # query
    _date = "2012-04-11"
    dt = datetime.strptime(_date,"%Y-%m-%d").utctimetuple()
    #dt = datetime.strptime(_date,"%Y-%m-%d")
    #stime=int(time.mktime(dt.utctimetuple()))
    # etime=stime+86400-1

    view = ViewDefinition('index','daily_tags',time_tag_mapper, language='python')
    view.sync(db)
    # tags = [row.value for row in db.view('index/daily_tags',startkey=stime,endkey=etime)]
    tags = [row.value for row in db.view('index/daily_tags',key=[dt.tm_year, dt.tm_mon, dt.tm_mday])]
    tags = list(set(tags))
    print "Tags today",set(tags)
    print ""

    view = ViewDefinition('index','daily_tagcount', tag_mapper, reduce_fun=tag_sumreducer,
                          language='python')
    view.sync(db)
    #d = dt.timetuple()
    d = dt
    for tag in sorted(tags):
        # tag_counts = [ (row.key, row.value) for row in db.view('index/tagcount', group=True) ]
        _key = [d.tm_year, d.tm_mon, d.tm_mday, tag]
        tag_count = [ (row.value) for row in db.view('index/daily_tagcount', key=_key) ][0]
        print "Found %d %s on %s-%s-%s "%(tag_count,tag,_key[0],_key[1],_key[2])

if __name__ == '__main__':
    main()

