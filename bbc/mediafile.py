""" Of filesystems and media contained therein. """
import os
import sys

from . import dbutil
from . import movie

extensions = {'.avi', '.m4v', '.mkv', '.mp4', '.mpg'}

def addlocation(db, path, baselocid=None):
    return dbutil.insert(db, 'INSERT INTO location (pathname, parentid) VALUES (?, ?)', path, baselocid)

def getlocation(db, path):
    return dbutil.getone(db, 'SELECT * FROM location WHERE pathname = ?', path)

def getpaths(db):
    """ Root media paths. """
    return dbutil.getall(db, 'SELECT * FROM location WHERE parentid IS NULL')

def fileiter(filename):
    """ yield (dirpart, filename) """
    with open(filename) as f:
        yield from (os.path.split(x.rstrip()) for x in f)

def mediaiter(sysiter):
    yield from ((dirpart, filename) for dirpart, filename in sysiter if os.path.splitext(filename)[1] in extensions)

def scanfiles(filename):
    yield from scan(db=db, iterobj=fileiter(filename))

def pathiter(path):
    for cwd, dirs, files in os.walk(path):
        for f in files:
    	    yield cwd, f

def scanpath(db, path):
    yield from scan(db=db, iterobj=pathiter(path))

def scan(db, iterobj):
    keys = {}
    for dirpart, filepart in mediaiter(iterobj):
        title, ext = os.path.splitext(filepart)
        for mov in movie.search(db, title):
            yield mov, filepart, dirpart

def removebase(fulldir, basedir):
    if fulldir.startswith(basedir):
        endstr = fulldir[len(basedir):].lstrip(os.path.sep)
    else:
        endstr = fulldir
    return endstr

def addmediafile(db, filename, locationid, movieid):
    return dbutil.insert(db, 'INSERT INTO mediafile (filename, locationid, movieid) VALUES (?, ?, ?)', filename, locationid, movieid)

def getmediafile(db, filename):
    return dbutil.getone(db, 'SELECT * FROM mediafile WHERE filename = ?', filename)

def scanpaths(db):
    added = []
    for rootpath in getpaths(db):
        basedir = os.path.expanduser(rootpath['pathname'])
        for mov, fname, fdir in scanpath(db, basedir):
            mf = getmediafile(db, fname)
            if mf is None:
                # Add a subdir.
                subdir = removebase(fdir, basedir=basedir)
                locationid = addlocation(db, subdir, baselocid=rootpath['locationid'])
                # Add the mediafile entry.
                mf = addmediafile(db, fname, locationid, mov['movieid'])
                added.append(fname)
    return added

