""" The Budge-Board Charts manager - main module. """

__version__ = '0.1'

import time
import urllib.request as ur

from . import dbutil
from . import imdb
from . import movie

def openurl(url):
    req = ur.Request(url)
    return ur.urlopen(req)

def fileopen(filename):
    return open(filename, 'rb')

def chartiter(charturl='https://imdb.com/chart/top', opener=openurl):
    parser = imdb.ChartParser()
    chartstr = str(opener(charturl).read(), 'utf-8')
    parser.feed(chartstr)
    yield from iter(parser)

def download(db, *args):
    return _import(db, list(chartiter()))

def fileimport(db, filename='chart.html'):
    return _import(db, list(chartiter(charturl=filename, opener=fileopen)))

def dlchart(db, outfile='chart.html', charturl='https://imdb.com/chart/top'):
    with open(outfile, 'wb') as f:
        f.write(openurl(url=charturl).read())

def addsync(db, date):
    return dbutil.insert(db, 'INSERT INTO sync (whensynced) VALUES (?)', date)

def addrank(db, position, movieid, syncid):
    return dbutil.insert(db, 'INSERT INTO rank (indexnum, movieid, asat) VALUES (?, ?, ?)', position, movieid, syncid)

def _import(db, entries):
    if not entries:
        raise Exception('Parse yields no results')
    # Add a sync date entry.
    now = int(time.time())
    syncid = addsync(db, now)
    # Import each movie title.
    addedmovies = []
    newrankings = []
    for i, (title, year, info) in enumerate(entries, 1):
        # Get an existing movie entry, create if it doesn't exist.
        mov = movie.getmovie(db, title, year)
        if mov:
            movieid = mov['movieid']
        else:
            movieid = movie.addmovie(db, title, year, info, now)
            addedmovies.append({'movieid': movieid, 'title': title, 'yearmade': year, 'notes': info, 'indexnum': i})
        # Add a ranking.
        rankid = addrank(db, i, movieid, now)
        newrankings.append(rankid)
    return addedmovies, newrankings

def getlastsync(db):
    return dbutil.getlast(db, 'sync')

def getrankings(db, asat=None):
    if asat is None:
        asat = getlastsync(db)['whensynced']
    return dbutil.getall(db, 'SELECT r.indexnum, m.* FROM rank r jOIN movie m ON r.movieid = m.movieid WHERE r.asat = ? ORDER BY r.indexnum', asat)

def gethistory(db):
    """ get the sync history """
    return dbutil.getall(db, 'SELECT * FROM sync')

def getrankingpair(db):
    # Grab the last two sync timestamps.
    syncold, syncnew = gethistory(db)[-2:]
    rankold = getrankings(db, asat=syncold['whensynced'])
    ranknew = getrankings(db, asat=syncnew['whensynced'])
    return rankold, ranknew

def getpunted(db):
    try:
        rankold, ranknew = getrankingpair(db)
    except ValueError:
        return []
    else:
        puntedids = {m['movieid'] for m in rankold} - {m['movieid'] for m in ranknew}
        return [m for m in rankold if m['movieid'] in puntedids]

def getdiffs(db):
    try:
        rankold, ranknew = getrankingpair(db)
    except ValueError:
        return
    # Build a difflist for entries in ranknew.
    rankolddict = {m['movieid']: m for m in rankold}
    for m in (dict((k, n[k]) for k in n.keys()) for n in ranknew):
        try:
            oldm = rankolddict[m['movieid']]
        except KeyError:
            # New entry
            m['diff'] = None
        else:
            # Calc diff.
            m['diff'] = oldm['indexnum'] - m['indexnum']
        yield m
