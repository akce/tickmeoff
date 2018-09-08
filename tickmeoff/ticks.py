""" Manage the ticks. """

import time

from . import dbutil

def markmovie(db, movie):
    dbutil.insert(db, 'INSERT INTO ticks (movieid, datetime) VALUES (?, ?)', movie['movieid'], int(time.time()))

def getmarks(db):
    return dbutil.getall(db, 'SELECT * FROM ticks t JOIN movie m ON (t.movieid = m.movieid)')
