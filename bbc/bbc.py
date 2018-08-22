""" The Budge-Board Charts manager - main module. """

__version__ = '0.1'

import time
import urllib.request as ur

from . import dbutil
from . import imdb
from . import movie

def openurl(url):
    ## NOTE: the agent value usually affects the content format returned by the server!
    #agent = 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0'
    agent = 'Lynx/2.8.8rel.2 libwww-FM/2.14 SSL-MM/1.4.1'
    req = ur.Request(url, headers={'User-Agent': agent})
    return ur.urlopen(req)

def fileopen(filename):
    return open(filename, 'rb')

def chartiter(charturl='https://imdb.com/chart/top', opener=openurl):
    parser = imdb.ChartParser()
    chartstr = str(opener(charturl).read(), 'utf-8')
    parser.feed(chartstr)
    yield from iter(parser)

def download(db):
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

def getpunted(db):
    # Grab the last two sync timestamps.
    try:
        syncold, syncnew = gethistory(db)[-2:]
    except ValueError:
        return []
    else:
        rankold = getrankings(db, asat=syncold['whensynced'])
        ranknew = getrankings(db, asat=syncnew['whensynced'])
        puntedids = {m['movieid'] for m in rankold} - {m['movieid'] for m in ranknew}
        return [m for m in rankold if m['movieid'] in puntedids]
