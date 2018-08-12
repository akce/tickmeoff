""" Of filesystems and media contained therein. """
import os
import sys

from . import dbutil
from . import mkey

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
    yield from scan(iterobj=fileiter(filename))

def pathiter(path):
    for cwd, dirs, files in os.walk(path):
        for f in files:
    	    yield cwd, f

def scanpath(path):
    yield from scan(iterobj=pathiter(path))

def scan(iterobj):
    keys = {}
    for dirpart, filepart in mediaiter(iterobj):
        title, ext = os.path.splitext(filepart)
        try:
            key = mkey.parse(title)
        except ValueError:
            print('Failed to create media key for "{}".. skipping'.format(filepart), file=sys.stderr)
        else:
            if key in keys:
                print('Duplicate "{}" == "{}"'.format(keys[key], filepart), file=sys.stderr)
            keys[key] = filepart
            yield key, filepart, dirpart

def removebase(fulldir, basedir):
    if fulldir.startswith(basedir):
        endstr = fulldir[len(basedir):].lstrip(os.path.sep)
    else:
        endstr = fulldir
    return endstr

def addmediafile(db, filename, locationid, mkeyid):
    return dbutil.insert(db, 'INSERT INTO mediafile (filename, locationid, mkeyid) VALUES (?, ?, ?)', filename, locationid, mkeyid)

def getmediafile(db, filename):
    return dbutil.getone(db, 'SELECT * FROM mediafile WHERE filename = ?', filename)

def scanpaths(db):
    added = []
    for rootpath in getpaths(db):
        basedir = os.path.expanduser(rootpath['pathname'])
        for fkey, fname, fdir in scanpath(basedir):
            dbmkey = mkey.getmkey(db, mkey=fkey)
            # Only add path entries for things that have charted.
            if dbmkey:
                mf = getmediafile(db, fname)
                if mf is None:
                    # Add a subdir.
                    subdir = removebase(fdir, basedir=basedir)
                    locationid = addlocation(db, subdir, baselocid=rootpath['locationid'])
                    # Add the mediafile entry.
                    mf = addmediafile(db, fname, locationid, dbmkey.mkeyid)
                    added.append(fname)
    return added

