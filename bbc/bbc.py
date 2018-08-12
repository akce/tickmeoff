""" The Budge-Board Charts manager - main module. """

__version__ = '0.1'

import time
import urllib.request as ur

from . import mkey
from . import dbutil
from . import imdb

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

def addmovie(db, title, year, info, syncid, mkeyid):
    return dbutil.insert(db, 'INSERT INTO movie (title, yearmade, notes, whenadded, mkeyid) VALUES (?, ?, ?, ?, ?)', title, year, info, syncid, mkeyid)

def getmovie(db, title, year):
    return dbutil.getone(db, 'SELECT * FROM movie WHERE title = ? AND yearmade = ?', title, year)

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
        movie = getmovie(db, title, year)
        if movie:
            movieid = movie['movieid']
        else:
            mkeyid = mkey.addmkey(db, title, year)
            movieid = addmovie(db, title, year, info, now, mkeyid)
            addedmovies.append({'movieid': movieid, 'title': title, 'yearmade': year, 'notes': info, 'indexnum': i, 'mkeyid': mkeyid})
        # Add a ranking.
        rankid = addrank(db, i, movieid, now)
        newrankings.append(rankid)
    return addedmovies, newrankings

def getlastsync(db):
    return dbutil.getlast(db, 'sync')

def getmovies(db):
    return dbutil.getall(db, 'SELECT * FROM movie')

def getrankings(db):
    asat = getlastsync(db)['whensynced']
    return dbutil.getall(db, 'SELECT r.indexnum, m.* FROM rank r jOIN movie m ON r.movieid = m.movieid WHERE r.asat = ? ORDER BY r.indexnum', asat)

def gethistory(db):
    """ get the sync history """
    return dbutil.getall(db, 'SELECT * FROM sync')
